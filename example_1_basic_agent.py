"""
Example 1: Basic Strands Agent with a single tool and CLI interface
"""
import asyncio, json
from datetime import datetime
from strands import Agent, tool

@tool
def get_time(timezone: str = "UTC") -> str:
    """Get the current time for a timezone."""
    current_time = datetime.now().strftime("%I:%M:%S %p")
    return f"The current time in {timezone} is {current_time}"


async def main():
    # Create agent with a single tool
    agent = Agent(
        name="TimeAgent",
        tools=[get_time],
        system_prompt="You are a helpful time assistant.",
        callback_handler=None
    )

    print("Agent CLI (type 'quit' to exit, 'messages' to see history)")
    print("-" * 60)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            break

        if user_input.lower() == "messages":
            # List out all messages in the conversation
            print("\n=== Conversation History ===")
            print(json.dumps(agent.messages, indent=2))
            print("=" * 30)
            continue

        if user_input:
            response = await agent.invoke_async(user_input)
            print(f"\nAgent: {response}")


if __name__ == "__main__":
    asyncio.run(main())
