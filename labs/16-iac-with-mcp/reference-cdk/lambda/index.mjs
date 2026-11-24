// Notifier: preference filtering + idempotent per-channel send with partial batch failures.
import { DynamoDBClient, GetItemCommand, PutItemCommand } from "@aws-sdk/client-dynamodb";

const ddb = new DynamoDBClient({});
const { PREFS_TABLE, IDEMPOTENCY_TABLE } = process.env;

async function claim(eventId, channel) {
  try {
    await ddb.send(new PutItemCommand({
      TableName: IDEMPOTENCY_TABLE,
      Item: { pk: { S: `${eventId}#${channel}` }, expiresAt: { N: String(Math.floor(Date.now() / 1000) + 7 * 86400) } },
      ConditionExpression: "attribute_not_exists(pk)",
    }));
    return true;
  } catch (e) {
    if (e.name === "ConditionalCheckFailedException") return false;
    throw e;
  }
}

async function send(channel, detail) {
  // Replace with SES / SNS calls. Kept as a log line so the lab deploys without verified identities.
  console.log(JSON.stringify({ msg: "send", channel, orderId: detail.orderId }));
}

export const handler = async (event) => {
  const batchItemFailures = [];
  for (const record of event.Records) {
    try {
      const evt = JSON.parse(record.body);
      const detail = evt.detail;
      const res = await ddb.send(new GetItemCommand({ TableName: PREFS_TABLE, Key: { customerId: { S: detail.customerId } } }));
      const prefs = res.Item ?? {};
      const channels = ["email", "push"].filter((c) => prefs[c]?.BOOL !== false);
      if (channels.length === 0) console.log(JSON.stringify({ msg: "suppressed", orderId: detail.orderId }));
      for (const ch of channels) if (await claim(evt.id, ch)) await send(ch, detail);
    } catch (err) {
      console.error(err);
      batchItemFailures.push({ itemIdentifier: record.messageId });
    }
  }
  return { batchItemFailures };
};
