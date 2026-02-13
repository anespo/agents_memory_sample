"""
Example 9: Clean up and delete the Memory resource
"""
import boto3
import json
import os

# Load memory configuration
try:
    with open("memory_config.json", "r") as f:
        config = json.load(f)
    memory_id = config["memory_id"]
except FileNotFoundError:
    print("❌ No memory_config.json found. Nothing to clean up.")
    exit(0)

# Initialize AgentCore control client
control_client = boto3.client("bedrock-agentcore-control", region_name="us-west-2")

print(f"Deleting memory: {memory_id}")

try:
    # Delete the memory resource
    control_client.delete_memory(memoryId=memory_id)
    print(f"✓ Memory {memory_id} deleted successfully!")
    
    # Remove the configuration file
    os.remove("memory_config.json")
    print("✓ Configuration file removed")
    
    print("\n✓ Cleanup complete!")
    
except control_client.exceptions.ResourceNotFoundException:
    print(f"⚠ Memory {memory_id} not found (may have been already deleted)")
    # Still remove the config file
    if os.path.exists("memory_config.json"):
        os.remove("memory_config.json")
        print("✓ Configuration file removed")
        
except Exception as e:
    print(f"❌ Error during cleanup: {str(e)}")
    exit(1)
