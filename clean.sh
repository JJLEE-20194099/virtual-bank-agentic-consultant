REGION=ap-southeast-1

for agent_id in $(aws bedrock-agent list-agents \
    --region $REGION \
    --query "agentSummaries[].agentId" \
    --output text); do

  echo "Processing agent: $agent_id"

  # 1. Xoá alias
  for alias_id in $(aws bedrock-agent list-agent-aliases \
      --region $REGION \
      --agent-id $agent_id \
      --query "agentAliasSummaries[].agentAliasId" \
      --output text); do

    echo "  Deleting alias: $alias_id"

    aws bedrock-agent delete-agent-alias \
      --region $REGION \
      --agent-id $agent_id \
      --agent-alias-id $alias_id
  done

  # 2. Xoá agent
  echo "Deleting agent: $agent_id"

  aws bedrock-agent delete-agent \
    --region $REGION \
    --agent-id $agent_id \
    --skip-resource-in-use-check

done