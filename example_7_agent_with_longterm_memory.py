"""
Example 7: Agent with long-term memory retrieval
"""
import asyncio
import json
from datetime import datetime
from strands import Agent, tool
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig


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
    actor_id = "user-1"
    session_id = "session-3"

    # Create memory configuration with long-term retrieval
    memory_config = AgentCoreMemoryConfig(
        memory_id=memory_id,
        actor_id="user-1",
        session_id="session-4",
        retrieval_config={
            f"/preferences/{actor_id}": RetrievalConfig(top_k=3)
        },
    )

    # Create memory session manager
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
        region_name="us-west-2",
    )

    # Create agent with long-term memory
    agent = Agent(
        name="TimeAgentWithLongTermMemory",
        tools=[get_time],
        system_prompt="You are a helpful time assistant. Use context about the user to personalize responses.",
        session_manager=session_manager,
        callback_handler=None,
    )

    print("Time Agent with Long-Term Memory CLI (type 'quit' to exit)")
    print("-" * 60)
    print("The agent automatically retrieves relevant long-term memories!\n")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            break

        if user_input:
            response = await agent.invoke_async(user_input)
            print(f"\nAgent: {response}")


if __name__ == "__main__":
    asyncio.run(main())
