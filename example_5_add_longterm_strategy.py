"""
Example 5: Add long-term strategies to existing memory
"""
import boto3
import json

# Load existing memory configuration
with open("memory_config.json", "r") as f:
    config = json.load(f)

memory_id = config["memory_id"]

# Initialize AgentCore control client
control_client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")

# Add long-term strategies to existing memory
response = control_client.update_memory(
    memoryId=memory_id,
    memoryStrategies={
        "addMemoryStrategies": [
            {
                "userPreferenceMemoryStrategy": {
                    "name": "PreferenceLearner",
                    "namespaces": ["/preferences/{actorId}"],
                }
            },
            # {
            #     "summaryMemoryStrategy": {
            #         "name": "SessionSummarizer",
            #         "namespaces": ["/summaries/{actorId}/{sessionId}"],
            #     }
            # },
            # {
            #     "semanticMemoryStrategy": {
            #         "name": "FactExtractor",
            #         "namespaces": ["/facts/{actorId}"],
            #     }
            # },
        ]
    },
)

print(f"✓ Long-term strategies added to existing memory!")
print(f"  Memory ID: {memory_id}")
