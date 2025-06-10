# Terra Mystica MCP Server Installation Guide

## Quick Installation

### 1. Install Dependencies

The MCP server dependencies are already included in the project's `pyproject.toml`:

```bash
cd /Users/marty/repos/terra-mystica/backend
uv pip install -e .
```

### 2. Generate Configuration Files

Run the installation script to generate all necessary configuration files:

```bash
python scripts/start_mcp_server.py --install
```

This creates:
- `configs/claude_desktop_config.json` - Claude Desktop configuration
- `configs/crewai_integration_config.json` - CrewAI integration configuration  
- `configs/.env.mcp` - Environment variable template
- `configs/SETUP.md` - Detailed setup instructions

### 3. Test the Installation

```bash
python scripts/start_mcp_server.py --test
```

Expected output:
```
🧪 Testing Terra Mystica MCP Server

📁 Testing File System Tools...
   ✅ File existence check: True
🔧 Testing Environment Tools...
   ✅ Configuration loaded: 8 sections
📂 Testing Directory Tools...
   ✅ Storage stats: 6 files
🌐 Testing HTTP Tools...
   ✅ Health check: {"status": "healthy", ...}

🎉 All tests completed!
```

## Usage Options

### CLI Usage

```bash
# Start MCP server (STDIO transport - default)
python scripts/start_mcp_server.py

# Start MCP server (SSE transport for web)
python scripts/start_mcp_server.py --transport sse --port 8001

# Use with custom API URL
python scripts/start_mcp_server.py --api-url http://localhost:8080
```

### Module Usage

```bash
# Start via Python module
python -m mcp.cli serve

# Test functionality
python -m mcp.cli test

# Show configuration
python -m mcp.cli config

# List available tools
python -m mcp.cli tools
```

## Claude Desktop Integration

1. Copy the generated configuration to Claude Desktop:

```bash
# macOS
cp configs/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows (in PowerShell)
cp configs/claude_desktop_config.json $env:APPDATA/Claude/claude_desktop_config.json
```

2. Restart Claude Desktop

3. The Terra Mystica tools will be available in Claude conversations

## CrewAI Integration

Use the MCP server in your CrewAI agents:

```python
from mcp.server import get_mcp_server
from crewai import Agent, Task, Crew

# Get MCP server instance
mcp_server = get_mcp_server()

# Create agent with MCP tools
agent = Agent(
    role="Geolocation Specialist",
    goal="Process images and determine geographic locations",
    backstory="Expert in AI geolocation using Terra Mystica",
    tools=[
        # Add MCP tools as needed
        mcp_server.fs_tools.read_file,
        mcp_server.http_tools.get,
        mcp_server.dir_tools.ensure_upload_directory,
    ]
)

# Create and run tasks
task = Task(
    description="Process uploaded image for geolocation",
    agent=agent,
    expected_output="Geographic coordinates with confidence"
)

crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

## Docker Integration

The MCP server is integrated into the Docker environment:

```bash
# Start with MCP enabled (default)
docker-compose up

# Start with specific MCP transport
MCP_TRANSPORT=sse docker-compose up

# Access MCP server directly
curl http://localhost:8081/mcp/health
```

## Environment Variables

Set these in your `.env` file or environment:

```bash
# Server Configuration
MCP_SERVER_NAME="Terra Mystica MCP Server"
MCP_TRANSPORT=stdio  # or 'sse'
MCP_HOST=0.0.0.0
MCP_PORT=8001
MCP_LOG_LEVEL=INFO

# API Configuration  
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30.0

# File System
MCP_BASE_PATH=/Users/marty/repos/terra-mystica/backend
```

## Available Tools

### File System Tools
- `read_file(file_path)` - Read file contents
- `write_file(file_path, content)` - Write to file
- `list_directory(directory_path)` - List directory
- `file_exists(file_path)` - Check existence
- `get_file_info(file_path)` - Get file metadata

### HTTP Tools
- `http_get(endpoint, params, headers)` - GET request
- `http_post(endpoint, data, json, headers)` - POST request
- `http_put(endpoint, data, json, headers)` - PUT request
- `http_delete(endpoint, params, headers)` - DELETE request

### Environment Tools
- `get_env_var(var_name, default)` - Get environment variable
- `list_env_vars(prefix)` - List environment variables

### Directory Tools
- `ensure_upload_directory(user_id)` - Create user directory
- `get_thumbnail_path(filename, size)` - Get thumbnail path
- `cleanup_temp_files(max_age_hours)` - Clean temp files
- `get_storage_stats()` - Get storage statistics

## FastAPI Endpoints

When integrated with FastAPI, these endpoints are available:

- `GET /mcp/health` - MCP server health check
- `GET /mcp/info` - MCP server information
- `GET /mcp/test` - Test MCP functionality

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure dependencies are installed with `uv pip install -e .`

2. **Permission Denied**: Check file permissions and MCP_BASE_PATH setting

3. **Connection Refused**: Verify FastAPI server is running at API_BASE_URL

4. **Tool Not Found**: Verify MCP server initialization in your code

### Debug Commands

```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG
python scripts/start_mcp_server.py --test

# Check server status
curl http://localhost:8000/mcp/health

# Verify tools
python -m mcp.cli tools
```

### Log Files

MCP server logs are written to:
- Console output (default)
- Application logs (if configured)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Test individual components with the test command
4. Verify environment configuration

## Next Steps

1. **Configure Claude Desktop** with the generated config
2. **Create CrewAI agents** using MCP tools
3. **Test file operations** with your specific use cases
4. **Monitor performance** using the health endpoints
5. **Customize tools** for your specific requirements