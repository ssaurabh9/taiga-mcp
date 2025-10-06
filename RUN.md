# 🚀 Running Taiga MCP Server

Complete guide for setting up and running Taiga MCP Server with Claude Desktop and Claude Code.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Claude Desktop Setup](#claude-desktop-setup)
- [Claude Code Setup](#claude-code-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Python 3.10+**: Check with `python --version` or `python3 --version`
- **Taiga Account**: Sign up at [taiga.io](https://taiga.io/) or use your self-hosted instance
- **MCP Client**: One of:
  - [Claude Desktop](https://claude.ai/download)
  - [Claude Code](https://docs.claude.com/claude-code) (VS Code/Cursor extension)
  - Any MCP-compatible client

### Optional but Recommended

- **Conda**: For isolated Python environments
- **Git**: For cloning the repository

---

## Installation

### Method 1: Using Conda (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/taiga-mcp.git
cd taiga-mcp

# Create conda environment
conda create -n taiga-mcp python=3.11 -y

# Activate environment
conda activate taiga-mcp

# Install dependencies
pip install --upgrade pip
pip install -e ".[dev]"
```

### Method 2: Using venv

```bash
# Clone the repository
git clone https://github.com/yourusername/taiga-mcp.git
cd taiga-mcp

# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -e ".[dev]"
```

### Method 3: Using uv (Fastest)

```bash
# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/yourusername/taiga-mcp.git
cd taiga-mcp

# Install with uv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

---

## Configuration

### Step 1: Create Environment File

```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env  # or vim, code, etc.
```

### Step 2: Add Your Credentials

Edit `.env` file:

```env
# Required
TAIGA_API_URL=https://api.taiga.io/api/v1
TAIGA_USERNAME=your_username_or_email
TAIGA_PASSWORD=your_password

# Optional
DEBUG=false  # Set to true for detailed logs
```

**Security Note**: Never commit `.env` file to git. It's already in `.gitignore`.

---

## Claude Desktop Setup

### Step 1: Find Your Python Path

```bash
# If using conda
conda activate taiga-mcp
which python

# If using venv
source venv/bin/activate
which python

# Example output: /opt/anaconda3/envs/taiga-mcp/bin/python
# Copy this path!
```

### Step 2: Locate Claude Desktop Config

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### Step 3: Edit Configuration

Open the config file:

```bash
# macOS
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or use your preferred editor
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Step 4: Add Taiga MCP Server

**Option A: Using Environment Variables (Recommended)**

```json
{
  "mcpServers": {
    "taiga": {
      "command": "/opt/anaconda3/envs/taiga-mcp/bin/python",
      "args": ["-m", "app.server"],
      "cwd": "/path/to/taiga-mcp",
      "env": {
        "TAIGA_API_URL": "https://api.taiga.io/api/v1",
        "TAIGA_USERNAME": "your_username",
        "TAIGA_PASSWORD": "your_password",
        "DEBUG": "false"
      }
    }
  }
}
```

**Option B: Using .env File (More Secure)**

```json
{
  "mcpServers": {
    "taiga": {
      "command": "/opt/anaconda3/envs/taiga-mcp/bin/python",
      "args": ["-m", "app.server"],
      "cwd": "/path/to/taiga-mcp"
    }
  }
}
```

**Important Replacements:**

1. Replace `/opt/anaconda3/envs/taiga-mcp/bin/python` with **your** Python path from Step 1
2. Replace `/path/to/taiga-mcp` with the actual path to your cloned repository
3. Replace `your_username` and `your_password` with your Taiga credentials

### Step 5: Restart Claude Desktop

```bash
# Quit Claude Desktop completely
osascript -e 'quit app "Claude"'

# Wait 2 seconds
sleep 2

# Reopen Claude Desktop
open -a Claude
```

Or manually:
1. Right-click Claude in Dock → Quit
2. Reopen from Applications

### Step 6: Verify Connection

In Claude Desktop:

1. Look for the **🔨 hammer icon** or **MCP servers** section
2. You should see **"taiga"** listed as connected
3. Try a command: `"List all my Taiga projects"`

---

## Claude Code Setup

### Step 1: Install Claude Code Extension

1. Open VS Code or Cursor
2. Go to Extensions (Cmd+Shift+X / Ctrl+Shift+X)
3. Search for "Claude Code"
4. Click Install

### Step 2: Find Python Path

```bash
# Activate your environment
conda activate taiga-mcp  # or: source venv/bin/activate

# Get Python path
which python
# Copy the output!
```

### Step 3: Configure MCP Server

**In VS Code/Cursor:**

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Claude Code: Open MCP Settings"
3. Or manually edit: `.vscode/mcp_settings.json` (workspace) or User settings

**Add this configuration:**

```json
{
  "mcpServers": {
    "taiga": {
      "command": "/opt/anaconda3/envs/taiga-mcp/bin/python",
      "args": ["-m", "app.server"],
      "cwd": "/Users/yourname/path/to/taiga-mcp",
      "env": {
        "TAIGA_API_URL": "https://api.taiga.io/api/v1",
        "TAIGA_USERNAME": "your_username",
        "TAIGA_PASSWORD": "your_password"
      }
    }
  }
}
```

**Replace:**
- Python path with your actual path
- `cwd` with repository path
- Username and password with your Taiga credentials

### Step 4: Reload Window

1. Press `Cmd+Shift+P` / `Ctrl+Shift+P`
2. Type "Developer: Reload Window"
3. Hit Enter

### Step 5: Verify

1. Open Claude Code panel
2. Look for Taiga in MCP servers list
3. Test: Ask Claude to "List all my Taiga projects"

---

## Verification

### Quick Test Script

Run the verification script:

```bash
# Activate environment
conda activate taiga-mcp  # or: source venv/bin/activate

# Run test
python test_setup.py
```

Expected output:
```
✓ Python 3.11.x
✓ HTTP client (httpx)
✓ MCP SDK (mcp)
✓ Data validation (pydantic)
✓ .env file found
✓ Configuration loaded
✓ Taiga MCP modules imported successfully

All checks passed! Setup is complete.
```

### Connection Test

Test actual Taiga connection:

```bash
python test_connection.py
```

Expected output:
```
🔍 Testing Taiga MCP Connection
==================================================

1. Testing authentication...
✅ Authentication successful!

2. Getting current user info...
✅ Logged in as: Your Name (username)

3. Fetching projects...
✅ Found X project(s):
   - Project Name (slug: project-slug, id: 12345)

All tests passed! MCP server is ready to use.
```

### Manual Server Test

Run the server directly:

```bash
# With debug logging
DEBUG=true python -m app.server

# Or use the debug script
./run_server_debug.sh
```

You should see:
```
2025-10-06 12:00:00 - app.server - INFO - Starting Taiga MCP server...
2025-10-06 12:00:00 - app.server - INFO - API URL: https://api.taiga.io/api/v1
2025-10-06 12:00:00 - app.server - INFO - Server ready, waiting for MCP messages on stdin/stdout
```

Press `Ctrl+C` to stop.

---

## Troubleshooting

### Common Issues

#### 1. "Server not connecting" in Claude Desktop

**Check Python path:**
```bash
conda activate taiga-mcp
which python
# Make sure this matches what's in claude_desktop_config.json
```

**Check Claude Desktop logs:**
```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp-server-taiga.log

# Look for error messages
```

**Solution:** Verify the Python path and `cwd` in config are correct.

---

#### 2. "Authentication failed"

**Test credentials manually:**
```bash
curl -X POST https://api.taiga.io/api/v1/auth \
  -H "Content-Type: application/json" \
  -d '{"type":"normal","username":"YOUR_USER","password":"YOUR_PASS"}'
```

**Solutions:**
- Verify credentials in `.env` are correct
- Try logging into Taiga web interface with same credentials
- Check if API URL is correct (self-hosted vs taiga.io)

---

#### 3. "Module not found" errors

**Reinstall dependencies:**
```bash
conda activate taiga-mcp
pip install --force-reinstall -e ".[dev]"
```

**Verify installation:**
```bash
python -c "import app; print('OK')"
```

---

#### 4. ".env file not loading"

**Check file location:**
```bash
ls -la .env
# Should be in project root
```

**Check file permissions:**
```bash
chmod 600 .env
```

**Verify in config:**
```json
{
  "mcpServers": {
    "taiga": {
      "cwd": "/absolute/path/to/taiga-mcp"  // Must be absolute!
    }
  }
}
```

---

#### 5. Server appears "hung"

**This is normal!** The MCP server waits for input from the client.

When you run `python -m app.server` directly, it will appear to hang because it's waiting for MCP protocol messages on stdin.

**To see logs:**
```bash
DEBUG=true python -m app.server
```

---

### Debug Mode

Enable debug mode for detailed logs:

**In .env:**
```env
DEBUG=true
```

**Or in Claude Desktop config:**
```json
{
  "env": {
    "DEBUG": "true"
  }
}
```

**View logs:**
```bash
# The server logs to stderr
# In Claude Desktop, check:
tail -f ~/Library/Logs/Claude/mcp-server-taiga.log
```

---

### Getting Help

If you're still having issues:

1. **Check the logs**:
   - Claude Desktop: `~/Library/Logs/Claude/mcp*.log`
   - Server debug: Run with `DEBUG=true`

2. **Run verification**:
   ```bash
   python test_setup.py
   python test_connection.py
   ```

3. **Check GitHub Issues**: [github.com/yourrepo/taiga-mcp/issues](https://github.com/yourrepo/taiga-mcp/issues)

4. **Ask for help**: Open a new issue with:
   - Output of `python test_setup.py`
   - Relevant log excerpts
   - Your environment (OS, Python version, conda/venv)

---

## Quick Reference

### Start Server (Debug Mode)

```bash
conda activate taiga-mcp
./run_server_debug.sh
```

### Update Configuration

```bash
# Edit credentials
nano .env

# Update Claude Desktop config
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Desktop
osascript -e 'quit app "Claude"' && sleep 2 && open -a Claude
```

### Test Installation

```bash
# Quick test
python test_setup.py

# Full connection test
python test_connection.py
```

### View Logs

```bash
# Server logs (if running with DEBUG=true)
./run_server_debug.sh

# Claude Desktop logs
tail -f ~/Library/Logs/Claude/mcp-server-taiga.log
```

---

## Example Workflow

After setup, try this workflow in Claude Desktop:

```
1. "List all my Taiga projects"
   → Shows all your projects

2. "Show me details about project 'my-project'"
   → Displays project information

3. "Create a user story in 'my-project' with title 'Setup authentication'"
   → Creates new story

4. "List all user stories in 'my-project'"
   → Shows all stories with their #ref numbers

5. "Update user story #42 - set status to 'In Progress'"
   → Updates the story status

6. "Create a task in story #42 titled 'Write tests'"
   → Adds task to story

7. "Show me all tasks for user story #42"
   → Lists all tasks
```

---

## Next Steps

- **Explore all tools**: See [README.md](./README.md#available-tools)
- **Contribute**: See [README.md](./README.md#contributing)
- **Report issues**: [GitHub Issues](https://github.com/yourrepo/taiga-mcp/issues)
- **Star the repo**: If you find it useful! ⭐

---

<div align="center">

**Happy automating with Taiga MCP! 🚀**

Need help? Check [DEBUGGING.md](./DEBUGGING.md) for advanced troubleshooting.

</div>
