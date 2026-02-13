# Troubleshooting Guide

Common issues and solutions for the Agent Memory Management application.

## 🔧 Installation Issues

### OpenTelemetry Dependency Conflicts

**Symptom:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
autogen-core 0.7.5 requires opentelemetry-api>=1.34.1, but you have opentelemetry-api 1.33.1
```

**Solution:**
The requirements.txt has been updated to include compatible OpenTelemetry versions. Reinstall:

```bash
# Using uv (recommended)
uv sync

# Or using pip with upgrade flag
pip install --upgrade -r requirements.txt

# Or force reinstall
pip install --force-reinstall -r requirements.txt
```

**Alternative Solution:**
If conflicts persist, create a fresh virtual environment:

```bash
# Create new virtual environment
python3 -m venv .venv-fresh

# Activate it
source .venv-fresh/bin/activate  # Unix/macOS
# or
.venv-fresh\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Python Version Issues

**Symptom:**
```
ERROR: This package requires Python >=3.10
```

**Solution:**
Ensure you're using Python 3.10 or higher:

```bash
python3 --version
# Should show 3.10.x or higher

# If not, install Python 3.10+ and use it explicitly
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### uv Package Manager Not Found

**Symptom:**
```
bash: uv: command not found
```

**Solution:**
Install uv or use pip instead:

```bash
# Option 1: Install uv (recommended)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Option 2: Use pip directly
pip install -r requirements.txt
```

## 🔐 AWS Configuration Issues

### AWS Credentials Not Found

**Symptom:**
```
NoCredentialsError: Unable to locate credentials
```

**Solution:**
Configure AWS credentials:

```bash
# Check if credentials exist
cat ~/.aws/credentials

# If not, configure them
aws configure --profile default
aws configure --profile default-xavi

# Or manually create ~/.aws/credentials
```

Example credentials file:
```ini
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET

[default-xavi]
aws_access_key_id = YOUR_LLM_KEY
aws_secret_access_key = YOUR_LLM_SECRET
```

### Profile Not Found

**Symptom:**
```
ProfileNotFound: The config profile (default-xavi) could not be found
```

**Solution:**
Ensure both profiles exist in `~/.aws/credentials` and `~/.aws/config`:

```bash
# Check profiles
aws configure list-profiles

# Should show:
# default
# default-xavi

# If missing, add them
aws configure --profile default-xavi
```

### Region Configuration Issues

**Symptom:**
```
You must specify a region
```

**Solution:**
Add region to `~/.aws/config`:

```ini
[default]
region = eu-west-1

[profile default-xavi]
region = eu-west-1
```

Or set environment variable:
```bash
export AWS_DEFAULT_REGION=eu-west-1
```

## 🧠 Memory Resource Issues

### Memory Not Active

**Symptom:**
- Status shows "CREATING" indefinitely
- Operations fail with "Memory not active"

**Solution:**
1. Wait 10-15 seconds after creation
2. Check AWS Console for resource status
3. Verify IAM permissions:

```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock-agentcore-control:CreateMemory",
    "bedrock-agentcore-control:GetMemory",
    "bedrock-agentcore-control:UpdateMemory"
  ],
  "Resource": "*"
}
```

### Memory Creation Fails

**Symptom:**
```
AccessDeniedException: User is not authorized to perform: bedrock-agentcore-control:CreateMemory
```

**Solution:**
Add required IAM permissions to your AWS user/role. See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md#iam-permissions-required) for complete permission set.

### Memory Config File Not Found

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'memory_config.json'
```

**Solution:**
This is normal on first run. Create a memory resource in the Setup tab, which will generate this file automatically.

## 📝 Long-Term Memory Issues

### No Long-Term Memories Found

**Symptom:**
- Queries return empty results
- "No memories found" message

**Solutions:**

1. **Wait for extraction** (most common)
   - Long-term extraction takes 30-60 seconds
   - Wait after adding events before querying

2. **Verify strategies are enabled**
   ```
   Setup Tab → Long-Term Memory Strategies → Add Strategies
   ```

3. **Check namespace**
   - Ensure query uses correct namespace
   - Default: `/preferences/{actor_id}`

4. **Verify events were added**
   ```
   Short-Term Memory Tab → Retrieve Current Session Events
   ```

### Extraction Taking Too Long

**Symptom:**
- Waiting more than 2 minutes for extraction

**Solution:**
1. Check AWS CloudWatch logs for errors
2. Verify memory resource is active
3. Ensure events contain extractable information
4. Try with sample events first

## 🤖 Agent Issues

### Agent Not Responding

**Symptom:**
- Spinner runs indefinitely
- No response in chat

**Solutions:**

1. **Check LLM profile credentials**
   ```bash
   aws bedrock list-foundation-models --profile default-xavi --region eu-west-1
   ```

2. **Verify Bedrock model access**
   - Go to AWS Console → Bedrock → Model access
   - Ensure Claude models are enabled

3. **Check Streamlit console for errors**
   - Look for error messages in terminal
   - Common: "ModelNotFound", "AccessDenied"

4. **Test with simple query**
   - Try: "What time is it?"
   - Should use get_time tool

### Agent Doesn't Remember Context

**Symptom:**
- Agent forgets previous messages
- No memory of conversation

**Solutions:**

1. **Verify memory resource is active**
   ```
   Setup Tab → Check status shows "Active"
   ```

2. **Check session ID**
   - Same session = short-term memory works
   - Different session = only long-term memory

3. **Enable long-term memory retrieval**
   ```
   Agent Chat Tab → Enable Long-Term Memory Retrieval checkbox
   ```

4. **Verify agent was created with memory**
   - Clear chat and start new conversation
   - Agent recreates with current settings

## 🌐 Streamlit Issues

### Port Already in Use

**Symptom:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Option 1: Use different port
streamlit run app.py --server.port 8502

# Option 2: Kill existing process
lsof -ti:8501 | xargs kill -9  # Unix/macOS
# or
netstat -ano | findstr :8501  # Windows (find PID)
taskkill /PID <PID> /F  # Windows (kill process)
```

### Streamlit Not Found

**Symptom:**
```
streamlit: command not found
```

**Solution:**
```bash
# Ensure streamlit is installed
pip install streamlit

# Or use full path
python -m streamlit run app.py

# Or with uv
uv run streamlit run app.py
```

### Browser Doesn't Open

**Symptom:**
- Streamlit starts but browser doesn't open

**Solution:**
Manually open: http://localhost:8501

Or configure Streamlit:
```bash
# Create ~/.streamlit/config.toml
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
[server]
headless = false

[browser]
gatherUsageStats = false
EOF
```

## 🐛 Application Errors

### Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'strands'
```

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or with uv
uv sync
```

### Session State Errors

**Symptom:**
```
AttributeError: 'SessionState' object has no attribute 'memory_id'
```

**Solution:**
- Refresh the page (Ctrl+R or Cmd+R)
- Clear browser cache
- Restart Streamlit application

### Boto3 Client Errors

**Symptom:**
```
botocore.exceptions.ClientError: An error occurred (ValidationException)
```

**Solution:**
1. Check AWS service availability in your region
2. Verify API parameters are correct
3. Check CloudWatch logs for detailed error
4. Ensure service quotas aren't exceeded

## 📊 Performance Issues

### Slow Response Times

**Symptom:**
- Agent takes >5 seconds to respond
- UI feels sluggish

**Solutions:**

1. **Reduce top_k in retrieval config**
   ```python
   # In app.py, reduce from 3 to 1-2
   RetrievalConfig(top_k=2)
   ```

2. **Check network latency**
   ```bash
   ping bedrock.eu-west-1.amazonaws.com
   ```

3. **Use closer AWS region**
   - Change REGION_DEFAULT and REGION_LLM in app.py

4. **Monitor AWS CloudWatch metrics**
   - Check API latency
   - Look for throttling

### High Memory Usage

**Symptom:**
- Application uses excessive RAM
- System becomes slow

**Solutions:**

1. **Clear chat history periodically**
   ```
   Agent Chat Tab → Clear Chat button
   ```

2. **Restart application**
   ```bash
   # Stop (Ctrl+C) and restart
   streamlit run app.py
   ```

3. **Limit conversation length**
   - Start new sessions for long conversations

## 🔍 Debugging Tips

### Enable Debug Logging

Add to app.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Streamlit Logs

```bash
# Run with verbose output
streamlit run app.py --logger.level=debug
```

### Test AWS Connectivity

```bash
# Test memory operations
aws bedrock-agentcore-control list-memories \
  --profile default \
  --region eu-west-1

# Test LLM access
aws bedrock list-foundation-models \
  --profile default-xavi \
  --region eu-west-1
```

### Verify Python Environment

```bash
# Check Python version
python3 --version

# Check installed packages
pip list | grep -E "bedrock|strands|streamlit|boto3"

# Check package versions
pip show bedrock-agentcore strands-agents streamlit boto3
```

## 📞 Getting Additional Help

### Check Documentation
1. [USAGE_GUIDE.md](USAGE_GUIDE.md) - Comprehensive usage
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
3. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Production setup

### AWS Resources
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Support](https://console.aws.amazon.com/support/)
- [AWS re:Post](https://repost.aws/)

### Community
- GitHub Issues (if applicable)
- AWS Developer Forums
- Stack Overflow (tag: amazon-bedrock)

## 🔄 Reset Everything

If all else fails, start fresh:

```bash
# 1. Delete memory resource
python example_9_cleanup_memory.py

# 2. Remove virtual environment
rm -rf .venv

# 3. Create fresh environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Run application
streamlit run app.py
```

## ✅ Verification Checklist

Before reporting an issue, verify:

- [ ] Python 3.10+ installed
- [ ] Dependencies installed correctly
- [ ] AWS credentials configured (both profiles)
- [ ] AWS region set to eu-west-1
- [ ] Bedrock model access enabled
- [ ] IAM permissions granted
- [ ] Memory resource created and active
- [ ] Streamlit running without errors
- [ ] Browser can access localhost:8501

---

**Still having issues?** Check the [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for more resources or review the example scripts for working code patterns.
