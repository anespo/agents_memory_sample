"""
Example 2: Create a Memory resource in AgentCore Memory using Boto3
"""
import boto3
import json

# Initialize AgentCore control client
control_client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")

# Create memory
response = control_client.create_memory(
    name="exampleAgentMemory",
    description="Example memory for agent demonstrations",
    eventExpiryDuration=90,  # Keep events for 90 days
)

memory_id = response["memory"]["id"]

print(f"✓ Memory created successfully!")
print(f"  Memory ID: {memory_id}")

# Save to file for use in other examples
with open("memory_config.json", "w") as f:
    json.dump({"memory_id": memory_id}, f, indent=2)

print(f"\n✓ Memory configuration saved to memory_config.json")
