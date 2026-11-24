import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";
import * as sqs from "aws-cdk-lib/aws-sqs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sources from "aws-cdk-lib/aws-lambda-event-sources";
import * as ddb from "aws-cdk-lib/aws-dynamodb";
import * as cw from "aws-cdk-lib/aws-cloudwatch";
import * as logs from "aws-cdk-lib/aws-logs";
import { NagSuppressions } from "cdk-nag";

/** Reference solution for the order-notifications spec (Lab 03), generated and reviewed with Kiro + AWS IaC MCP. */
export class NotificationsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bus = new events.EventBus(this, "OrdersBus", { eventBusName: "orders" });

    const dlq = new sqs.Queue(this, "NotifyDlq", {
      retentionPeriod: cdk.Duration.days(14),
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      enforceSSL: true,
    });
    const queue = new sqs.Queue(this, "NotifyQueue", {
      visibilityTimeout: cdk.Duration.seconds(180), // ≥ 6 × function timeout
      deadLetterQueue: { queue: dlq, maxReceiveCount: 3 },
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      enforceSSL: true,
    });

    new events.Rule(this, "OrderShippedRule", {
      eventBus: bus,
      eventPattern: { detailType: ["OrderShipped"] },
      targets: [new targets.SqsQueue(queue)],
    });

    const prefs = new ddb.TableV2(this, "Preferences", {
      partitionKey: { name: "customerId", type: ddb.AttributeType.STRING },
      pointInTimeRecoverySpecification: { pointInTimeRecoveryEnabled: true },
    });
    const idem = new ddb.TableV2(this, "Idempotency", {
      partitionKey: { name: "pk", type: ddb.AttributeType.STRING },
      timeToLiveAttribute: "expiresAt",
    });

    const fn = new lambda.Function(this, "Notifier", {
      runtime: lambda.determineLatestNodeRuntime(this),
      architecture: lambda.Architecture.ARM_64,
      memorySize: 512,
      timeout: cdk.Duration.seconds(30),
      handler: "index.handler",
      code: lambda.Code.fromAsset("lambda"),
      tracing: lambda.Tracing.ACTIVE,
      logGroup: new logs.LogGroup(this, "NotifierLogs", { retention: logs.RetentionDays.ONE_MONTH }),
      environment: { PREFS_TABLE: prefs.tableName, IDEMPOTENCY_TABLE: idem.tableName },
    });
    fn.addEventSource(new sources.SqsEventSource(queue, { batchSize: 10, reportBatchItemFailures: true }));
    prefs.grantReadData(fn);
    idem.grantWriteData(fn);

    new cw.Alarm(this, "DlqNotEmpty", {
      metric: dlq.metricApproximateNumberOfMessagesVisible({ period: cdk.Duration.minutes(1) }),
      threshold: 0,
      comparisonOperator: cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
      evaluationPeriods: 5,
      alarmDescription: "Notifications are landing in the DLQ (Req 3.2)",
    });

    // Documented, reviewed exceptions — the agent must justify every suppression (see Lab 16 step 4).
    NagSuppressions.addResourceSuppressions(fn, [
      { id: "AwsSolutions-IAM4", reason: "AWSLambdaBasicExecutionRole only grants log delivery to this function's log group.",
        appliesTo: ["Policy::arn:<AWS::Partition>:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"] },
      { id: "AwsSolutions-IAM5", reason: "X-Ray PutTraceSegments/PutTelemetryRecords do not support resource-level permissions.",
        appliesTo: ["Resource::*"] },
      { id: "AwsSolutions-L1", reason: "determineLatestNodeRuntime() selects the newest runtime GA in the target region; cdk-nag may know of a newer one." },
    ], true);

    new cdk.CfnOutput(this, "BusName", { value: bus.eventBusName });
  }
}
