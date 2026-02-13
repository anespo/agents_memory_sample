# Quick Start Guide

Get up and running with the Agent Memory Management application in 5 minutes.

## Prerequisites

- Python 3.10+
- AWS account with Bedrock access
- AWS credentials configured

## Step 1: Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

**Optional: Verify Setup**
```bash
python verify_setup.py
```

## Step 2: Configure AWS Credentials

Create or edit `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

Create or edit `~/.aws/config`:

```ini
[default]
region = eu-west-1
```

**Verify access:**
```bash
aws bedrock list-foundation-models --region eu-west-1
```

## Step 3: Launch the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Step 4: Create Memory Resource

1. Go to the "Setup" tab
2. Fill in the memory details (or use defaults)
3. Click "Create Memory Resource"
4. Wait for status to show "Active" (5-10 seconds)

## Step 5: Enable Long-Term Memory

1. In the Setup tab, scroll to "Long-Term Memory Strategies"
2. Select "user_preference"
3. Click "Add Strategies"

## Step 6: Add Sample Data

1. Go to "Short-Term Memory" tab
2. Click "Add Sample Events"
3. Wait 30-60 seconds for long-term extraction

## Step 7: Query Long-Term Memory

1. Go to "Long-Term Memory" tab
2. Try the quick queries or enter your own
3. See extracted facts from conversations

## Step 8: Chat with the Agent

1. Go to "Agent Chat" tab
2. Ensure "Enable Long-Term Memory Retrieval" is checked
3. Start chatting!

## Example Conversation

```
You: What time is it?
Agent: [Uses get_time tool and responds]

You: What do I like to drink?
Agent: [Retrieves from long-term memory]

[Change session ID in sidebar]

You: Do you remember my preferences?
Agent: [Still remembers via long-term memory]
```

## Cleanup

When done:
1. Go to "Setup" tab
2. Click "Delete Memory Resource"

## Troubleshooting

**Memory not active?**
- Wait 5-10 seconds after creation

**No long-term memories?**
- Wait 30-60 seconds after adding events
- Ensure strategies are enabled

**AWS credentials error?**
- Check `~/.aws/credentials` exists
- Verify Bedrock access in AWS Console

**More issues?**
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Next Steps

- Experiment with different session IDs
- Try different memory strategies
- Build your own memory-enabled agents
- Read [BLOG.md](BLOG.md) for detailed concepts

---

**Need help?** Check [README.md](README.md) or open an issue on GitHub.
