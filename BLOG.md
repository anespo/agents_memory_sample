# Building Memory-Enabled AI Agents with Amazon Bedrock AgentCore

## Introduction: The Barista Analogy

Imagine walking into your favorite coffee shop. You order a tea, but the barista immediately forgets what you said and stares at you blankly. Frustrating, right? Now imagine returning a week later, and the barista remembers your "usual" order without you saying a word. That's the difference between an agent without memory and one with proper memory management.

Agents cannot work effectively without memory. While some memory might seem "free" within an agentic loop, real production systems require managed memory over time. If an agent uses a tool, it must remember why it made the request to properly handle the response. This is where Amazon Bedrock AgentCore Memory comes in.

## Understanding Memory Types

### Short-Term Memory: The Conversational Context

Short-term memory is the conversational history maintained within a session. It's essential for the agentic loop to function. Without it, an agent can't understand follow-up questions or maintain coherence in a conversation.

Think of it as remembering what someone said five minutes ago in the current conversation. When you ask "What about New York?" after asking about Tokyo's time, the agent needs to remember the context.

**Characteristics:**
- Session-scoped (tied to a specific conversation)
- Stores raw conversational events
- Immediate access
- Disappears if the process is shut down (unless persisted)

**The Problem:** In frameworks, conversational history is typically maintained as a list of messages in memory. If the process shuts down or moves to another server, this history is lost.

**The Solution:** Persist these events in a managed database (like Amazon Bedrock AgentCore Memory) so the agent can "rehydrate" itself upon restarting.

### Long-Term Memory: The Persistent Knowledge

Long-term memory spans multiple interactions and improves the experience by remembering stable facts across visits. It's like the barista remembering your usual order a week later.

**Characteristics:**
- Actor-scoped (tied to a specific user)
- Stores extracted facts, not raw conversations
- Semantic search enabled
- Asynchronous extraction (30-60 seconds)

**The Magic:** A background process automatically extracts stable facts from conversations and stores them in a searchable format. You don't manually manage this - it happens automatically.

## Building a Simple Agent

Let's start with a basic agent using the Strands Agents SDK:

```python
from datetime import datetime
from strands import Agent, tool

@tool
def get_time(timezone: str = "UTC") -> str:
    """Get the current time for a timezone."""
    current_time = datetime.now().strftime("%I:%M:%S %p")
    return f"The current time in {timezone} is {current_time}"

agent = Agent(
    name="TimeAgent",
    tools=[get_time],
    system_prompt="You are a helpful time assistant."
)

response = await agent.invoke_async("What time is it?")
```

**The Limitation:** This agent has short-term memory during the conversation, but if you restart it, all context is lost. Ask "What did I just say?" after a restart, and the agent won't know.

## Adding Persistent Memory

### Step 1: Create a Memory Resource

First, create a memory resource in Amazon Bedrock AgentCore:

```python
import boto3

control_client = boto3.client("bedrock-agentcore-control", region_name="eu-west-1")

response = control_client.create_memory(
    name="AgentMemory",
    description="Memory for our time assistant",
    eventExpiryDuration=90  # Keep events for 90 days
)

memory_id = response["memory"]["id"]
```

This creates a managed memory resource in AWS that will persist our agent's conversations.

### Step 2: Integrate Memory with the Agent

Now integrate the memory with our agent using the AgentCore Memory Session Manager:

```python
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager
)
from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig
)

# Configure memory
memory_config = AgentCoreMemoryConfig(
    memory_id=memory_id,
    actor_id="user-1",      # Identifies the user
    session_id="session-1"  # Identifies this conversation
)

# Create session manager
session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config,
    region_name="eu-west-1"
)

# Create agent with memory
agent = Agent(
    name="TimeAgentWithMemory",
    tools=[get_time],
    system_prompt="You are a helpful time assistant.",
    session_manager=session_manager
)
```

**The Result:** Now the agent automatically saves conversations to AgentCore Memory. Restart the agent, and it will reload the conversation history. Ask "What did I just say?" and it will remember!

## Enabling Long-Term Memory

Short-term memory is great for maintaining context within a conversation, but what about remembering facts across multiple sessions?

### Step 3: Add Long-Term Strategies

Enable long-term memory strategies to extract stable facts:

```python
control_client.update_memory(
    memoryId=memory_id,
    memoryStrategies={
        "addMemoryStrategies": [
            {
                "userPreferenceMemoryStrategy": {
                    "name": "PreferenceLearner",
                    "namespaces": ["/preferences/user-1"]
                }
            }
        ]
    }
)
```

### Step 4: Add Conversational Events

Add some conversation to the memory:

```python
data_client = boto3.client("bedrock-agentcore", region_name="eu-west-1")

payload = [
    {
        "conversational": {
            "content": {"text": "I really enjoy drinking tea, especially black tea"},
            "role": "USER"
        }
    },
    {
        "conversational": {
            "content": {"text": "That's a classic choice!"},
            "role": "ASSISTANT"
        }
    }
]

data_client.create_event(
    memoryId=memory_id,
    actorId="user-1",
    sessionId="session-1",
    eventTimestamp=datetime.now(),
    payload=payload
)
```

**Wait 30-60 seconds** for the background extraction process to run.

### Step 5: Query Long-Term Memory

Now query the extracted facts:

```python
response = data_client.retrieve_memory_records(
    memoryId=memory_id,
    namespace="/preferences/user-1",
    searchCriteria={
        "searchQuery": "What do I like to drink?",
        "topK": 3
    }
)

for record in response.get("memoryRecordSummaries", []):
    print(record["content"]["text"])
    # Output: "The user enjoys drinking tea, with a preference for black tea"
```

**The Magic:** The system didn't just return the raw conversation. It extracted the stable fact: "The user enjoys drinking tea, with a preference for black tea."

## Automatic Long-Term Memory Integration

The real power comes when you integrate long-term memory retrieval directly into the agent:

```python
from bedrock_agentcore.memory.integrations.strands.config import RetrievalConfig

memory_config = AgentCoreMemoryConfig(
    memory_id=memory_id,
    actor_id="user-1",
    session_id="session-2",  # New session!
    retrieval_config={
        "/preferences/user-1": RetrievalConfig(top_k=3)
    }
)

session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=memory_config,
    region_name="eu-west-1"
)

agent = Agent(
    name="MemoryEnabledAgent",
    tools=[get_time],
    system_prompt="You are a helpful assistant. Use context about the user to personalize responses.",
    session_manager=session_manager
)
```

**The Result:** Every time the user sends a message, the agent automatically:
1. Performs a semantic search of long-term memory
2. Injects relevant facts into the context
3. Generates a personalized response

Even in a brand new session (session-2), the agent remembers that the user likes tea because it pulled that fact from long-term memory!

## The Complete Streamlit Application

To make this accessible, I built a comprehensive Streamlit application that demonstrates all these concepts:

### Features

1. **Memory Resource Setup**
   - Create and configure memory resources
   - Enable long-term strategies
   - Monitor resource status

2. **Short-Term Memory Management**
   - Add sample conversational events
   - View session history
   - Understand context persistence

3. **Long-Term Memory Queries**
   - Semantic search across extracted facts
   - Query user preferences
   - Test cross-session retrieval

4. **Interactive Agent Chat**
   - Chat with a memory-enabled agent
   - Toggle long-term memory retrieval
   - Experience personalized responses

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The application opens at `http://localhost:8501` with an intuitive interface for exploring all memory concepts.

## Real-World Use Cases

### Customer Support Agent

```python
actor_id = hash(customer_email)  # Stable per customer
session_id = f"support-{ticket_id}"  # Unique per ticket

# The agent remembers:
# - Customer preferences across tickets
# - Previous issues and resolutions
# - Communication style preferences
```

### Personal Assistant

```python
actor_id = user_id
session_id = f"session-{timestamp}"

# The agent learns:
# - User habits and preferences
# - Important facts and context
# - Personalized recommendations
```

### Data Analysis Agent

```python
actor_id = analyst_id
session_id = f"analysis-{project_id}"

# The agent maintains:
# - Analysis preferences
# - Project context
# - Historical analysis patterns
```

## Key Insights

### 1. Short-Term Memory is Essential
Without short-term memory, the agentic loop cannot function. The agent needs to remember why it called a tool to handle the response properly.

### 2. Long-Term Memory Enables Personalization
Extracting stable facts across sessions creates a personalized experience that improves over time.

### 3. Asynchronous Extraction is Powerful
The background extraction process (30-60 seconds) means you don't have to manually manage what to remember - the system figures it out.

### 4. Semantic Search is Key
Instead of keyword matching, semantic search finds relevant facts based on meaning, making retrieval more intelligent.

### 5. Managed Services Simplify Operations
Amazon Bedrock AgentCore handles the heavy lifting of persisting, extracting, and searching memories, so you can focus on building great agents.

## Architecture Patterns

### Separation of Concerns
- **Control Plane**: Create/manage memory resources
- **Data Plane**: Store/retrieve events and memories
- **Agent Framework**: Handle inference and tool execution

### Namespace Organization
```
/preferences/{actor_id}     # User preferences
/summaries/{actor_id}/{sessionId}  # Session summaries
/facts/{actor_id}           # General facts
```

### Memory Strategies
- **User Preference**: Learns likes/dislikes
- **Summary**: Creates session summaries
- **Semantic**: Extracts general facts

## Performance Considerations

### Typical Latency
- Memory creation: 5-10 seconds
- Event storage: <100ms
- Long-term extraction: 30-60 seconds (async)
- Semantic search: <200ms
- Agent response: 1-3 seconds

### Cost Optimization
- Use appropriate expiry durations (30-90 days typical)
- Limit top_k in retrieval (3-5 typical)
- Use specific namespaces for targeted retrieval
- Monitor storage usage

### Scaling
- Single user: ~10-50MB memory
- 100s of users: ~1-5GB total
- 1000s of users: Implement namespace partitioning

## Best Practices

### 1. ID Management
- Use stable actor IDs (user IDs, email hashes)
- Generate unique session IDs per conversation
- Never use PII directly in IDs

### 2. Strategy Selection
- Enable only strategies you need
- User preferences for personalization
- Summaries for session context
- Semantic for general facts

### 3. Testing
- Wait 30-60 seconds after adding events
- Test with sample data first
- Verify extraction before production

### 4. Production Deployment
- Use IAM roles instead of access keys
- Enable CloudWatch monitoring
- Set up proper error handling
- Implement resource cleanup

## Conclusion

Memory is fundamental to building effective AI agents. Short-term memory enables the agentic loop to function, while long-term memory creates personalized experiences that improve over time.

Amazon Bedrock AgentCore Memory provides a managed solution that handles the complexity of persisting, extracting, and searching memories, allowing you to focus on building great agent experiences.

The Streamlit application I built demonstrates all these concepts in an accessible, interactive way. Whether you're learning about agent memory, building a proof-of-concept, or deploying to production, the patterns and code are ready to use.

## Try It Yourself

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure AWS credentials
4. Run: `streamlit run app.py`
5. Explore the four tabs to understand memory concepts
6. Build your own memory-enabled agents!

The future of AI agents is memory-enabled, personalized, and context-aware. Start building today!

---

**Resources:**
- [GitHub Repository](your-repo-url)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Strands Agents SDK](https://github.com/awslabs/strands-agents)

**About the Author:**
Senior MLOps Engineer with 15+ years of experience building agentic applications, RAG systems, and production ML systems for clients worldwide.
