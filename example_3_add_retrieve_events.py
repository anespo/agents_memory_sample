"""
Example 3: Add events to Memory and retrieve them
"""
import boto3
import json
from datetime import datetime
import time

# Load memory configuration
with open("memory_config.json", "r") as f:
    config = json.load(f)

memory_id = config["memory_id"]
actor_id = "user-1"
session_id = "session-1"

# Initialize clients
control_client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")
data_client = boto3.client("bedrock-agentcore", region_name="us-west-2")

# Wait for memory to become active
print("Waiting for memory to become active...")
while True:
    response = control_client.get_memory(memoryId=memory_id)
    status = response["memory"]["status"]
    if status == "ACTIVE":
        print("✓ Memory is active!")
        break
    print(f"  Status: {status}, waiting...")
    time.sleep(5)

# Add events to memory
print("\nAdding conversation to memory...")
payload = [
    {
        "conversational": {
            "content": {"text": "My name is Mike and I really enjoy drinking tea"},
            "role": "USER",
        }
    },
    {
        "conversational": {
            "content": {"text": "Nice to meet you Mike! Tea is wonderful."},
            "role": "ASSISTANT",
        }
    },
    {
        "conversational": {
            "content": {"text": "I prefer black tea, with no milk or sugar"},
            "role": "USER",
        }
    },
    {
        "conversational": {
            "content": {"text": "That's a classic way to enjoy it! Pure and simple."},
            "role": "ASSISTANT",
        }
    },
]

data_client.create_event(
    memoryId=memory_id,
    actorId=actor_id,
    sessionId=session_id,
    eventTimestamp=datetime.now(),
    payload=payload,
)

print("✓ Events added successfully!")

# Retrieve events from memory
print("\nRetrieving events from memory...")
response = data_client.list_events(
    memoryId=memory_id, actorId=actor_id, sessionId=session_id
)

events = response.get("events", [])
print(f"Found {len(events)} events:\n")

for i, event in enumerate(events, 1):
    print(f"Event {i}:")
    payload = event.get("payload", [])
    for turn in payload:
        if "conversational" in turn:
            conv = turn["conversational"]
            role = conv.get("role", "unknown")
            text = conv.get("content", {}).get("text", "")
            print(f"  [{role}]: {text}")
    print()
