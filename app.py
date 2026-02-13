"""
Amazon Bedrock Agent Core Memory Management - Unified Streamlit Application

This application demonstrates the complete lifecycle of agent memory management:
- Short-term memory (conversational history within sessions)
- Long-term memory (persistent facts across sessions)
- Memory strategies (user preferences, summaries, semantic facts)

Target Audience: Data Scientists, ML/AI Engineers, AWS Architects
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

import boto3
import streamlit as st
from strands import Agent, tool
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)
from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig,
    RetrievalConfig,
)

# Page configuration
st.set_page_config(
    page_title="Bedrock Agent Memory Management",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Constants
MEMORY_CONFIG_FILE = "memory_config.json"
AWS_REGION = "eu-west-1"
AWS_PROFILE = "default"

# Initialize session state
if "memory_id" not in st.session_state:
    st.session_state.memory_id = None
if "actor_id" not in st.session_state:
    st.session_state.actor_id = "user-1"
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session-{int(time.time())}"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "memory_status" not in st.session_state:
    st.session_state.memory_status = "Not Created"


# Tool definitions
@tool
def get_time(timezone: str = "UTC") -> str:
    """Get the current time for a timezone."""
    current_time = datetime.now().strftime("%I:%M:%S %p")
    return f"The current time in {timezone} is {current_time}"


# Utility functions
def get_boto3_session() -> boto3.Session:
    """Create boto3 session with configured profile."""
    return boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)


def load_memory_config() -> Optional[Dict]:
    """Load memory configuration from file."""
    if os.path.exists(MEMORY_CONFIG_FILE):
        with open(MEMORY_CONFIG_FILE, "r") as f:
            return json.load(f)
    return None


def save_memory_config(memory_id: str):
    """Save memory configuration to file."""
    with open(MEMORY_CONFIG_FILE, "w") as f:
        json.dump({"memory_id": memory_id}, f, indent=2)


def create_memory_resource(name: str, description: str, expiry_days: int) -> str:
    """Create a new memory resource in Bedrock AgentCore."""
    session = get_boto3_session()
    control_client = session.client("bedrock-agentcore-control")

    response = control_client.create_memory(
        name=name,
        description=description,
        eventExpiryDuration=expiry_days,
    )

    memory_id = response["memory"]["id"]
    save_memory_config(memory_id)
    return memory_id


def wait_for_memory_active(memory_id: str, max_wait: int = 60) -> bool:
    """Wait for memory resource to become active."""
    session = get_boto3_session()
    control_client = session.client("bedrock-agentcore-control")

    start_time = time.time()
    while time.time() - start_time < max_wait:
        response = control_client.get_memory(memoryId=memory_id)
        status = response["memory"]["status"]
        if status == "ACTIVE":
            return True
        time.sleep(2)
    return False


def add_longterm_strategies(memory_id: str, strategies: List[str]):
    """Add long-term memory strategies to existing memory."""
    session = get_boto3_session()
    control_client = session.client("bedrock-agentcore-control")

    strategy_configs = []
    actor_id = st.session_state.actor_id

    if "user_preference" in strategies:
        strategy_configs.append(
            {
                "userPreferenceMemoryStrategy": {
                    "name": "PreferenceLearner",
                    "namespaces": [f"/preferences/{actor_id}"],
                }
            }
        )

    if "summary" in strategies:
        strategy_configs.append(
            {
                "summaryMemoryStrategy": {
                    "name": "SessionSummarizer",
                    "namespaces": [f"/summaries/{actor_id}/{{sessionId}}"],
                }
            }
        )

    if "semantic" in strategies:
        strategy_configs.append(
            {
                "semanticMemoryStrategy": {
                    "name": "FactExtractor",
                    "namespaces": [f"/facts/{actor_id}"],
                }
            }
        )

    if strategy_configs:
        control_client.update_memory(
            memoryId=memory_id,
            memoryStrategies={"addMemoryStrategies": strategy_configs},
        )


def add_events_to_memory(
    memory_id: str, actor_id: str, session_id: str, events: List[Dict]
):
    """Add conversational events to memory."""
    session = get_boto3_session()
    data_client = session.client("bedrock-agentcore")

    payload = []
    for event in events:
        payload.append(
            {
                "conversational": {
                    "content": {"text": event["text"]},
                    "role": event["role"],
                }
            }
        )

    data_client.create_event(
        memoryId=memory_id,
        actorId=actor_id,
        sessionId=session_id,
        eventTimestamp=datetime.now(),
        payload=payload,
    )


def retrieve_longterm_memories(
    memory_id: str, actor_id: str, query: str, top_k: int = 3
) -> List[Dict]:
    """Retrieve long-term memories using semantic search."""
    session = get_boto3_session()
    data_client = session.client("bedrock-agentcore")

    namespace = f"/preferences/{actor_id}"

    response = data_client.retrieve_memory_records(
        memoryId=memory_id,
        namespace=namespace,
        searchCriteria={"searchQuery": query, "topK": top_k},
    )

    return response.get("memoryRecordSummaries", [])


def delete_memory_resource(memory_id: str):
    """Delete memory resource and clean up configuration."""
    session = get_boto3_session()
    control_client = session.client("bedrock-agentcore-control")

    try:
        control_client.delete_memory(memoryId=memory_id)
        if os.path.exists(MEMORY_CONFIG_FILE):
            os.remove(MEMORY_CONFIG_FILE)
        return True
    except Exception as e:
        st.error(f"Error deleting memory: {str(e)}")
        return False


async def create_agent_with_memory(
    memory_id: str,
    actor_id: str,
    session_id: str,
    enable_longterm: bool = False,
) -> Agent:
    """Create an agent with memory session manager."""
    # Create memory configuration
    memory_config_params = {
        "memory_id": memory_id,
        "actor_id": actor_id,
        "session_id": session_id,
    }

    if enable_longterm:
        memory_config_params["retrieval_config"] = {
            f"/preferences/{actor_id}": RetrievalConfig(top_k=3)
        }

    memory_config = AgentCoreMemoryConfig(**memory_config_params)

    # Create session manager
    session = get_boto3_session()
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=memory_config,
        region_name=AWS_REGION,
        boto3_session=session,
    )

    # Create agent
    agent = Agent(
        name="MemoryEnabledAgent",
        tools=[get_time],
        system_prompt=(
            "You are a helpful assistant with memory capabilities. "
            "Use context about the user to personalize responses. "
            "Be concise and friendly."
        ),
        session_manager=session_manager,
        callback_handler=None,
    )

    return agent


# UI Components
def render_sidebar():
    """Render sidebar with configuration and controls."""
    st.sidebar.title("🧠 Memory Configuration")

    # Load existing config
    config = load_memory_config()
    if config:
        st.session_state.memory_id = config["memory_id"]
        st.session_state.memory_status = "Active"

    # Memory status
    status_color = "🟢" if st.session_state.memory_status == "Active" else "🔴"
    st.sidebar.markdown(f"**Status:** {status_color} {st.session_state.memory_status}")

    if st.session_state.memory_id:
        st.sidebar.code(st.session_state.memory_id, language=None)

    st.sidebar.markdown("---")

    # Actor and Session IDs
    st.sidebar.subheader("Identity Configuration")
    st.session_state.actor_id = st.sidebar.text_input(
        "Actor ID (User)", value=st.session_state.actor_id
    )
    st.session_state.session_id = st.sidebar.text_input(
        "Session ID", value=st.session_state.session_id
    )

    if st.sidebar.button("🔄 New Session ID"):
        st.session_state.session_id = f"session-{int(time.time())}"
        st.session_state.chat_history = []
        st.session_state.agent = None
        st.rerun()

    st.sidebar.markdown("---")

    # AWS Configuration Info
    with st.sidebar.expander("ℹ️ AWS Configuration"):
        st.markdown(
            f"""
        **Profile:** `{AWS_PROFILE}`  
        **Region:** `{AWS_REGION}`
        """
        )


def render_memory_setup_tab():
    """Render memory setup and management tab."""
    st.header("1️⃣ Memory Resource Setup")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
        ### Create Memory Resource
        Memory resources in Amazon Bedrock AgentCore provide persistent storage for both 
        short-term (conversational) and long-term (extracted facts) memory.
        """
        )

        with st.form("create_memory_form"):
            memory_name = st.text_input(
                "Memory Name", value="AgentMemoryDemo", key="memory_name"
            )
            memory_desc = st.text_area(
                "Description",
                value="Demonstration of agent memory capabilities",
                key="memory_desc",
            )
            expiry_days = st.number_input(
                "Event Expiry (days)", min_value=1, max_value=365, value=90
            )

            submit = st.form_submit_button("Create Memory Resource")

            if submit:
                with st.spinner("Creating memory resource..."):
                    try:
                        memory_id = create_memory_resource(
                            memory_name, memory_desc, expiry_days
                        )
                        st.session_state.memory_id = memory_id

                        # Wait for activation
                        if wait_for_memory_active(memory_id):
                            st.session_state.memory_status = "Active"
                            st.success(f"✅ Memory created: {memory_id}")
                        else:
                            st.warning("Memory created but not yet active. Please wait.")
                    except Exception as e:
                        st.error(f"Error creating memory: {str(e)}")

    with col2:
        st.markdown("### Current Status")
        if st.session_state.memory_id:
            st.info(
                f"""
            **Memory ID:**  
            `{st.session_state.memory_id}`
            
            **Status:** {st.session_state.memory_status}
            """
            )
        else:
            st.warning("No memory resource created yet")

    st.markdown("---")

    # Long-term strategies
    st.subheader("Long-Term Memory Strategies")
    st.markdown(
        """
    Long-term strategies extract stable facts from conversations and store them 
    for cross-session retrieval. This process happens asynchronously (30-60 seconds).
    """
    )

    if st.session_state.memory_id and st.session_state.memory_status == "Active":
        col1, col2 = st.columns([3, 1])

        with col1:
            strategies = st.multiselect(
                "Select Strategies to Enable",
                ["user_preference", "summary", "semantic"],
                default=["user_preference"],
                help="User preferences are recommended for personalization",
            )

        with col2:
            if st.button("Add Strategies", type="primary"):
                with st.spinner("Adding strategies..."):
                    try:
                        add_longterm_strategies(st.session_state.memory_id, strategies)
                        st.success("✅ Strategies added successfully!")
                    except Exception as e:
                        st.error(f"Error adding strategies: {str(e)}")
    else:
        st.info("Create and activate a memory resource first")

    st.markdown("---")

    # Cleanup
    st.subheader("⚠️ Cleanup")
    if st.session_state.memory_id:
        if st.button("Delete Memory Resource", type="secondary"):
            if delete_memory_resource(st.session_state.memory_id):
                st.session_state.memory_id = None
                st.session_state.memory_status = "Not Created"
                st.session_state.agent = None
                st.success("✅ Memory resource deleted")
                st.rerun()


def render_shortterm_memory_tab():
    """Render short-term memory demonstration tab."""
    st.header("2️⃣ Short-Term Memory (Conversational History)")

    st.markdown(
        """
    Short-term memory maintains the conversational context within a session. 
    This is essential for the agent to understand follow-up questions and maintain coherence.
    """
    )

    if not st.session_state.memory_id:
        st.warning("⚠️ Please create a memory resource in the Setup tab first")
        return

    # Sample events
    st.subheader("Add Sample Conversation")
    st.markdown("Inject a sample conversation to populate short-term memory:")

    if st.button("Add Sample Events"):
        sample_events = [
            {"role": "USER", "text": "My name is Alex and I enjoy drinking coffee"},
            {
                "role": "ASSISTANT",
                "text": "Nice to meet you Alex! Coffee is a great choice.",
            },
            {"role": "USER", "text": "I prefer espresso, double shot"},
            {
                "role": "ASSISTANT",
                "text": "Strong and bold - that's the way to start the day!",
            },
            {"role": "USER", "text": "I'm a data scientist working with Python"},
            {
                "role": "ASSISTANT",
                "text": "Python is excellent for data science! What frameworks do you use?",
            },
            {
                "role": "USER",
                "text": "Mostly pandas, scikit-learn, and recently PyTorch",
            },
            {
                "role": "ASSISTANT",
                "text": "That's a solid stack for ML work!",
            },
        ]

        with st.spinner("Adding events to memory..."):
            try:
                add_events_to_memory(
                    st.session_state.memory_id,
                    st.session_state.actor_id,
                    st.session_state.session_id,
                    sample_events,
                )
                st.success("✅ Sample conversation added to memory!")
                st.info(
                    "💡 These events will be extracted into long-term memory within 30-60 seconds"
                )
            except Exception as e:
                st.error(f"Error adding events: {str(e)}")

    st.markdown("---")

    # Retrieve events
    st.subheader("View Short-Term Memory")
    if st.button("Retrieve Current Session Events"):
        session = get_boto3_session()
        data_client = session.client("bedrock-agentcore")

        try:
            response = data_client.list_events(
                memoryId=st.session_state.memory_id,
                actorId=st.session_state.actor_id,
                sessionId=st.session_state.session_id,
            )

            events = response.get("events", [])

            if events:
                st.success(f"Found {len(events)} events in current session")

                for i, event in enumerate(events, 1):
                    with st.expander(f"Event {i}"):
                        payload = event.get("payload", [])
                        for turn in payload:
                            if "conversational" in turn:
                                conv = turn["conversational"]
                                role = conv.get("role", "unknown")
                                text = conv.get("content", {}).get("text", "")

                                if role == "USER":
                                    st.markdown(f"**👤 User:** {text}")
                                else:
                                    st.markdown(f"**🤖 Assistant:** {text}")
            else:
                st.info("No events found in current session")

        except Exception as e:
            st.error(f"Error retrieving events: {str(e)}")


def render_longterm_memory_tab():
    """Render long-term memory query tab."""
    st.header("3️⃣ Long-Term Memory (Semantic Search)")

    st.markdown(
        """
    Long-term memory stores extracted facts that persist across sessions. 
    Query this memory using semantic search to retrieve relevant user preferences and information.
    """
    )

    if not st.session_state.memory_id:
        st.warning("⚠️ Please create a memory resource in the Setup tab first")
        return

    st.info(
        "💡 Long-term memories are extracted asynchronously. "
        "Wait 30-60 seconds after adding events before querying."
    )

    # Query interface
    st.subheader("Query Long-Term Memory")

    query_text = st.text_input(
        "Enter your query",
        placeholder="What do I like to drink?",
        key="longterm_query",
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        top_k = st.slider("Number of results", min_value=1, max_value=10, value=3)

    with col2:
        search_button = st.button("🔍 Search", type="primary")

    if search_button and query_text:
        with st.spinner("Searching long-term memory..."):
            try:
                records = retrieve_longterm_memories(
                    st.session_state.memory_id,
                    st.session_state.actor_id,
                    query_text,
                    top_k,
                )

                if records:
                    st.success(f"Found {len(records)} relevant memories")

                    for i, record in enumerate(records, 1):
                        content = record.get("content", {})
                        text = content.get("text", "No text available")

                        with st.expander(f"Memory {i}", expanded=True):
                            st.markdown(text)
                else:
                    st.warning(
                        "No memories found. Ensure:\n"
                        "1. Events have been added\n"
                        "2. Long-term strategies are enabled\n"
                        "3. Sufficient time has passed for extraction (30-60s)"
                    )

            except Exception as e:
                st.error(f"Error querying memory: {str(e)}")

    # Preset queries
    st.markdown("---")
    st.subheader("Quick Queries")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("What do I like to drink?"):
            st.session_state.preset_query = "What do I like to drink?"
            st.rerun()

    with col2:
        if st.button("What's my profession?"):
            st.session_state.preset_query = "What's my profession?"
            st.rerun()

    with col3:
        if st.button("What tools do I use?"):
            st.session_state.preset_query = "What tools do I use?"
            st.rerun()

    if "preset_query" in st.session_state:
        query = st.session_state.preset_query
        del st.session_state.preset_query

        with st.spinner(f"Searching for: {query}"):
            try:
                records = retrieve_longterm_memories(
                    st.session_state.memory_id, st.session_state.actor_id, query, 3
                )

                if records:
                    for i, record in enumerate(records, 1):
                        content = record.get("content", {})
                        st.info(f"**Result {i}:** {content.get('text', 'N/A')}")
                else:
                    st.warning("No results found")

            except Exception as e:
                st.error(f"Error: {str(e)}")


def render_agent_chat_tab():
    """Render interactive agent chat tab."""
    st.header("4️⃣ Interactive Agent with Memory")

    st.markdown(
        """
    Chat with an agent that has full memory capabilities. The agent automatically:
    - Maintains short-term conversational context
    - Retrieves relevant long-term memories to personalize responses
    """
    )

    if not st.session_state.memory_id:
        st.warning("⚠️ Please create a memory resource in the Setup tab first")
        return

    # Memory mode selection
    col1, col2 = st.columns([3, 1])

    with col1:
        enable_longterm = st.checkbox(
            "Enable Long-Term Memory Retrieval",
            value=True,
            help="Automatically inject relevant long-term memories into context",
        )

    with col2:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.agent = None
            st.rerun()

    # Display chat history
    st.markdown("---")

    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Create agent if not exists
                    if st.session_state.agent is None:
                        st.session_state.agent = asyncio.run(
                            create_agent_with_memory(
                                st.session_state.memory_id,
                                st.session_state.actor_id,
                                st.session_state.session_id,
                                enable_longterm,
                            )
                        )

                    # Get response
                    response = asyncio.run(
                        st.session_state.agent.invoke_async(user_input)
                    )

                    st.markdown(response)

                    # Add to history
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": response}
                    )

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": error_msg}
                    )


# Main application
def main():
    st.title("🧠 Amazon Bedrock Agent Core Memory Management")
    st.markdown(
        """
    **Comprehensive demonstration of agent memory capabilities for production ML systems**
    
    This application showcases the complete lifecycle of memory management in agentic systems:
    short-term conversational context and long-term persistent knowledge.
    """
    )

    # Render sidebar
    render_sidebar()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "1️⃣ Setup",
            "2️⃣ Short-Term Memory",
            "3️⃣ Long-Term Memory",
            "4️⃣ Agent Chat",
        ]
    )

    with tab1:
        render_memory_setup_tab()

    with tab2:
        render_shortterm_memory_tab()

    with tab3:
        render_longterm_memory_tab()

    with tab4:
        render_agent_chat_tab()

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    Built for Data Scientists, ML Engineers, and AWS Architects | 
    Amazon Bedrock Agent Core Memory Management
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
