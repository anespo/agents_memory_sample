"""
Example 6: Add events and retrieve top K long-term memories
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
session_id = "session-3"

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

# Add diverse events to build long-term memory
print("\nAdding diverse conversation to memory...")
payload = [
    {"conversational": {"content": {"text": "I really enjoy drinking tea, especially black tea"}, "role": "USER"}},
    {"conversational": {"content": {"text": "That's a classic choice! How do you take your tea?"}, "role": "ASSISTANT"}},
    {"conversational": {"content": {"text": "I prefer it with no milk or sugar, just plain"}, "role": "USER"}},
    {"conversational": {"content": {"text": "Pure and simple - that's the best way to taste the tea itself."}, "role": "ASSISTANT"}},
    {"conversational": {"content": {"text": "I'm a big fan of Python programming"}, "role": "USER"}},
    {"conversational": {"content": {"text": "Python is a great language! What do you use it for?"}, "role": "ASSISTANT"}},
    {"conversational": {"content": {"text": "Mostly for building AI agents and working with AWS services"}, "role": "USER"}},
    {"conversational": {"content": {"text": "That's an excellent combination for modern development."}, "role": "ASSISTANT"}},
    {"conversational": {"content": {"text": "I'm from Brisbane, Australia"}, "role": "USER"}},
    {"conversational": {"content": {"text": "Brisbane is a beautiful city! Great weather there."}, "role": "ASSISTANT"}},
]

data_client.create_event(
    memoryId=memory_id,
    actorId=actor_id,
    sessionId=session_id,
    eventTimestamp=datetime.now(),
    payload=payload,
)

print("✓ Events added successfully!")

# Wait for long-term memory extraction
print("\nWaiting for long-term memories to be extracted...")
print("(This happens asynchronously and may take a few minutes)")
time.sleep(60)

# Query long-term memories
print("\nQuerying long-term memories...")
namespace = f"/preferences/{actor_id}"

queries = [
    "What do I like to drink?",
    "What programming language do I use?",
    "Where am I from?",
]

for query_text in queries:
    print(f"\nQuery: '{query_text}'")
    print("-" * 60)
    
    response = data_client.retrieve_memory_records(
        memoryId=memory_id,
        namespace=namespace,
        searchCriteria={"searchQuery": query_text, "topK": 2},
    )
    
    records = response.get("memoryRecordSummaries", [])
    
    if records:
        for i, record in enumerate(records, 1):
            content = record.get("content", {})
            print(f"{i}. {content.get('text', 'No text')}")
    else:
        print("No memories found yet (extraction may still be in progress)")
