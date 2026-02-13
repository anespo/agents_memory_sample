"""
Example 4: Agent with AgentCore Memory Session Manager
"""
import asyncio
import json
from datetime import datetime
from strands import Agent, tool
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig


@tool
def get_time(timezone: str = "UTC") -> str:
    """Get the current time for a timezone."""
    current_time = datetime.now().strftime("%I:%M:%S %p")
    return f"The current time in {timezone} is {current_time}"


async def main():
    # Load memory configuration
    with open("memory_config.json", "r") as f:
        config = json.load(f)

    memory_id = config["memory_id"]

    # Create memory configuration
    memory_config = AgentCoreMemoryConfig(
        memory_id=memory_id,
        actor_id="user-1",
        session_id="session-2",
    )

    # Create memory session manager
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
        region_name="us-west-2",
    )

    # Create agent with memory
    agent = Agent(
        name="TimeAgentWithMemory",
        tools=[get_time],
        system_prompt="You are a helpful time assistant.",
        session_manager=session_manager,
        callback_handler=None,
    )

    print("Time Agent with Memory CLI (type 'quit' to exit)")
    print("-" * 60)
    print("Conversation is automatically saved to AgentCore Memory\n")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            break

        if user_input:
            response = await agent.invoke_async(user_input)
            print(f"\nAgent: {response}")


if __name__ == "__main__":
    asyncio.run(main())
