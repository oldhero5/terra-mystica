# Terra Mystica MCP Server

A comprehensive Model Context Protocol (MCP) server for the Terra Mystica geolocation service. This MCP server enables CrewAI agents to interact with the FastAPI application through standardized tools for file operations, HTTP requests, environment management, and directory operations.

## Overview

The Terra Mystica MCP Server provides a bridge between AI agents (particularly CrewAI) and the Terra Mystica backend services. It exposes essential functionality through MCP tools that allow agents to:

- Read and write files in the project
- Make HTTP requests to FastAPI endpoints
- Access environment variables and configuration
- Manage uploads, thumbnails, and temporary files

## Features

### 🗂️ File System Tools
- **read_file**: Read contents of any file in the project
- **write_file**: Write content to files with directory creation
- **list_directory**: List directory contents with metadata
- **file_exists**: Check file/directory existence
- **get_file_info**: Get detailed file information and permissions

### 🌐 HTTP Tools
- **http_get/post/put/delete**: Make HTTP requests to FastAPI endpoints
- **upload_file**: Upload files to API endpoints
- **health_check**: Check API health status
- **check_auth**: Validate authentication tokens

### 🔧 Environment Tools
- **get_env_var**: Get environment variable values
- **list_env_vars**: List environment variables by prefix
- **get_terra_mystica_config**: Get complete application configuration
- **validate_required_env_vars**: Validate required environment setup

### 📁 Directory Tools
- **ensure_upload_directory**: Create user upload directories
- **get_thumbnail_path**: Generate thumbnail file paths
- **cleanup_temp_files**: Clean up old temporary files
- **get_storage_stats**: Get storage usage statistics
- **list_user_files**: List files for specific users

## Installation

### 1. Install Dependencies

The MCP server dependencies are included in the main `pyproject.toml`:

```bash
cd backend
uv pip install -e .
```

### 2. Configuration

Set environment variables for MCP server:

```bash
export MCP_SERVER_NAME="Terra Mystica MCP Server"
export MCP_TRANSPORT="stdio"  # or "sse" for web-based
export API_BASE_URL="http://localhost:8000"
export MCP_LOG_LEVEL="INFO"
```

### 3. Generate Configuration Files

```bash
python -m mcp.cli install
```

This creates:
- `configs/claude_desktop_config.json` - For Claude Desktop
- `configs/crewai_integration_config.json` - For CrewAI agents
- `configs/SETUP.md` - Setup instructions

## Usage

### CLI Commands

```bash
# Start MCP server (STDIO transport)
python -m mcp.cli serve

# Start MCP server (SSE transport for web)
python -m mcp.cli serve --transport sse --host 0.0.0.0 --port 8001

# Test MCP server functionality
python -m mcp.cli test

# Show configuration
python -m mcp.cli config

# List available tools
python -m mcp.cli tools

# Generate Claude Desktop config
python -m mcp.cli generate-claude-config --output claude_config.json

# Generate CrewAI integration config
python -m mcp.cli generate-crewai-config --output crewai_config.json
```

### FastAPI Integration

The MCP server is automatically integrated with the main FastAPI application:

```python
from mcp.fastapi_integration import setup_mcp_integration

app = FastAPI()
setup_mcp_integration(app)
```

Endpoints:
- `GET /mcp/health` - MCP server health check
- `GET /mcp/info` - MCP server information
- `GET /mcp/test` - Test MCP functionality

### CrewAI Integration

```python
from crewai import Agent, Task, Crew
from mcp.server import get_mcp_server

# Get MCP server instance
mcp_server = get_mcp_server()

# Create agent with MCP tools
agent = Agent(
    role="Geolocation Processor",
    goal="Process image uploads and generate geolocation results",
    backstory="Expert in AI-powered geolocation using Terra Mystica tools",
    tools=[
        # File operations
        mcp_server.fs_tools.read_file,
        mcp_server.fs_tools.write_file,
        # HTTP operations  
        mcp_server.http_tools.get,
        mcp_server.http_tools.post,
        # Directory operations
        mcp_server.dir_tools.ensure_upload_directory,
        mcp_server.dir_tools.get_storage_stats,
    ]
)

# Create task
task = Task(
    description="Process uploaded image and determine location",
    agent=agent,
    expected_output="Location coordinates with confidence score"
)

# Run crew
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

### Claude Desktop Integration

1. Copy the generated configuration to Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`

2. Configuration example:
```json
{
  "mcpServers": {
    "terra-mystica": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "env": {
        "MCP_SERVER_NAME": "Terra Mystica MCP Server",
        "API_BASE_URL": "http://localhost:8000",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## Tool Examples

### File Operations

```python
# Read application configuration
config_content = mcp_server.fs_tools.read_file("app/core/config.py")

# Write processing results
results = {"location": [37.7749, -122.4194], "confidence": 0.89}
mcp_server.fs_tools.write_file(
    "results/geolocation_result.json", 
    json.dumps(results, indent=2)
)

# List user uploads
uploads = mcp_server.fs_tools.list_directory("uploads/images/123")
```

### HTTP Operations

```python
# Check API health
health = await mcp_server.http_tools.get("/health")

# Upload image for processing
upload_result = await mcp_server.http_tools.upload_file(
    "/api/v1/images/upload",
    "/path/to/image.jpg",
    additional_data={"user_id": 123}
)

# Get processing results
results = await mcp_server.http_tools.get(
    f"/api/v1/images/{image_id}/results"
)
```

### Environment and Configuration

```python
# Get database URL
db_url = mcp_server.env_tools.get_env_var("DATABASE_URL")

# Get complete app configuration
config = mcp_server.env_tools.get_terra_mystica_config()

# Validate environment setup
validation = mcp_server.env_tools.validate_required_env_vars()
if not validation["valid"]:
    print(f"Missing required vars: {validation['missing_required']}")
```

### Directory Management

```python
# Ensure user directory exists
user_dir = mcp_server.dir_tools.ensure_upload_directory(user_id=123)

# Get thumbnail path
thumbnail = mcp_server.dir_tools.get_thumbnail_path(
    "image_123.jpg", 
    size="medium"
)

# Clean up old temp files
cleanup_result = mcp_server.dir_tools.cleanup_temp_files(max_age_hours=24)
print(f"Cleaned {cleanup_result['cleaned_files']} files")

# Get storage statistics
stats = mcp_server.dir_tools.get_storage_stats()
print(f"Total storage: {stats['totals']['total_size_mb']} MB")
```

## Security

### File System Security
- All file operations are restricted to the application base directory
- Path traversal attacks are prevented through path validation
- Hidden files are excluded from listings unless explicitly requested

### Environment Variable Security
- Only allowed prefixes can be accessed (TERRA_, API_, DATABASE_, etc.)
- Sensitive variables (passwords, secrets, keys) are masked in logs
- Environment access is logged for audit purposes

### HTTP Security
- Configurable timeouts prevent hanging requests
- Request/response logging for debugging
- Support for authentication headers

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_NAME` | "Terra Mystica MCP Server" | Server display name |
| `MCP_TRANSPORT` | "stdio" | Transport type (stdio/sse) |
| `MCP_HOST` | "0.0.0.0" | Host for SSE transport |
| `MCP_PORT` | 8001 | Port for SSE transport |
| `API_BASE_URL` | "http://localhost:8000" | FastAPI base URL |
| `MCP_BASE_PATH` | Current directory | Base path for file operations |
| `MCP_LOG_LEVEL` | "INFO" | Logging level |
| `MCP_AUTH_ENABLED` | false | Enable authentication |

### Transport Options

#### STDIO Transport (Default)
- Best for local CLI tools and desktop applications
- Direct process communication
- Lower latency

#### SSE Transport
- Best for web-based applications
- HTTP-based communication
- Supports remote access

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure all dependencies are installed with `uv pip install -e .`
2. **Permission Denied**: Check file permissions and base path configuration
3. **Connection Refused**: Verify FastAPI server is running and accessible
4. **Tool Not Found**: Verify MCP server is properly initialized

### Debug Mode

Enable debug logging:
```bash
export MCP_LOG_LEVEL=DEBUG
python -m mcp.cli serve
```

### Health Checks

```bash
# Test MCP server
python -m mcp.cli test

# Check FastAPI integration
curl http://localhost:8000/mcp/health

# Verify tools
python -m mcp.cli tools
```

## Docker Support

The MCP server is integrated into the Docker environment:

```bash
# Start with MCP enabled
MCP_ENABLED=true docker-compose up

# Start with SSE transport
MCP_TRANSPORT=sse docker-compose up

# Access MCP server
curl http://localhost:8081/mcp/health
```

## Development

### Adding New Tools

1. Create tool function in appropriate module (`mcp/tools/`)
2. Register tool in `mcp/server.py`
3. Add CLI command if needed in `mcp/cli.py`
4. Update documentation

### Testing

```bash
# Run MCP tests
python -m mcp.cli test

# Test specific functionality
python -c "
from mcp.server import get_mcp_server
server = get_mcp_server()
print(server.fs_tools.read_file('pyproject.toml')[:100])
"
```

## API Reference

See the generated documentation at `/docs` when running the FastAPI server, or use the CLI:

```bash
python -m mcp.cli tools  # List all available tools
```

## License

This MCP server is part of the Terra Mystica project and follows the same licensing terms.