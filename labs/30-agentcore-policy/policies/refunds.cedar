// Illustrative Cedar for the rules in requirements.txt.
// Entity and action names are derived from YOUR gateway's tool schemas — generate with
// create_policies.py (natural language → policy) or copy names from the generated assets
// before creating policies by hand. Policies are validated against that schema on create.

permit (
  principal is AgentCore::OAuthUser,
  action == AgentCore::Action::"orders___get_order",
  resource == AgentCore::Gateway::"<gateway-arn>"
);

permit (
  principal is AgentCore::OAuthUser,
  action == AgentCore::Action::"orders___issue_refund",
  resource == AgentCore::Gateway::"<gateway-arn>"
)
when {
  principal.hasTag("role") &&
  ["support-agent", "support-lead"].contains(principal.getTag("role")) &&
  context.input.amount <= 100
};

permit (
  principal is AgentCore::OAuthUser,
  action == AgentCore::Action::"orders___issue_refund",
  resource == AgentCore::Gateway::"<gateway-arn>"
)
when {
  principal.hasTag("role") && principal.getTag("role") == "support-lead" &&
  context.input.amount <= 1000
};

forbid (
  principal,
  action == AgentCore::Action::"orders___issue_refund",
  resource
)
unless { context.input.order_id like "A-*" };
