"""
MCP Server CLI
Command-line interface for Terra Mystica MCP server
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .server import MCPServer, get_mcp_server
from .config import get_mcp_config, generate_claude_config, get_crewai_integration_config

app = typer.Typer(name="mcp", help="Terra Mystica MCP Server CLI")
console = Console()


@app.command()
def serve(
    transport: str = typer.Option("stdio", help="Transport type (stdio, sse, http)"),
    host: str = typer.Option("0.0.0.0", help="Host for SSE/HTTP transport"),
    port: int = typer.Option(8001, help="Port for SSE/HTTP transport"),
    api_url: str = typer.Option("http://localhost:8000", help="FastAPI base URL"),
):
    """Start MCP server"""
    try:
        config = get_mcp_config()
        server = MCPServer(
            name=config.server_name,
            version=config.version,
            api_base_url=api_url or config.api_base_url
        )
        
        rprint(f"[green]Starting Terra Mystica MCP Server[/green]")
        rprint(f"[blue]Transport:[/blue] {transport}")
        rprint(f"[blue]API URL:[/blue] {api_url}")
        
        if transport == "stdio":
            server.run_stdio()
        elif transport == "sse":
            rprint(f"[blue]SSE Server:[/blue] http://{host}:{port}")
            server.run_sse(host=host, port=port)
        else:
            rprint(f"[red]Error:[/red] Unsupported transport: {transport}")
            raise typer.Exit(1)
            
    except KeyboardInterrupt:
        rprint("\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        rprint(f"[red]Error starting server:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def config():
    """Show MCP server configuration"""
    config = get_mcp_config()
    
    table = Table(title="MCP Server Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    # Add configuration rows
    table.add_row("Server Name", config.server_name)
    table.add_row("Version", config.version)
    table.add_row("Transport", config.transport)
    table.add_row("Host", config.host)
    table.add_row("Port", str(config.port))
    table.add_row("API Base URL", config.api_base_url)
    table.add_row("Base Path", config.base_path)
    table.add_row("Log Level", config.log_level)
    table.add_row("Auth Enabled", str(config.auth_enabled))
    
    console.print(table)


@app.command()
def test():
    """Test MCP server tools"""
    try:
        rprint("[blue]Testing MCP server tools...[/blue]")
        
        server = get_mcp_server()
        
        # Test file system
        rprint("\n[green]Testing File System Tools:[/green]")
        test_file = "/tmp/mcp_test.txt"
        
        # Write test
        result = server.fs_tools.write_file(test_file, "MCP Test Content")
        rprint(f"Write: {result}")
        
        # Read test
        content = server.fs_tools.read_file(test_file)
        rprint(f"Read: {content}")
        
        # List test
        listing = server.fs_tools.list_directory("/tmp")
        rprint(f"List: Found {len(listing.get('files', []))} files in /tmp")
        
        # Clean up
        Path(test_file).unlink(missing_ok=True)
        
        # Test environment tools
        rprint("\n[green]Testing Environment Tools:[/green]")
        home = server.env_tools.get_env_var("HOME")
        rprint(f"HOME: {home}")
        
        config_vars = server.env_tools.get_terra_mystica_config()
        rprint(f"Config sections: {list(config_vars.keys())}")
        
        # Test directory tools
        rprint("\n[green]Testing Directory Tools:[/green]")
        stats = server.dir_tools.get_storage_stats()
        if "totals" in stats:
            rprint(f"Storage: {stats['totals']['total_files']} files, {stats['totals']['total_size_mb']} MB")
        
        validation = server.dir_tools.validate_directories()
        rprint(f"Directory validation: {'✓' if validation.get('all_valid') else '✗'}")
        
        # Test HTTP tools (async)
        rprint("\n[green]Testing HTTP Tools:[/green]")
        async def test_http():
            try:
                health = await server.http_tools.health_check()
                if health.get("success"):
                    rprint(f"Health check: ✓ {health['data']}")
                else:
                    rprint(f"Health check: ✗ {health.get('error', 'Unknown error')}")
            except Exception as e:
                rprint(f"Health check: ✗ {e}")
        
        asyncio.run(test_http())
        
        rprint("\n[green]✓ All tests completed![/green]")
        
    except Exception as e:
        rprint(f"[red]Test failed:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def generate_claude_config(
    output: Optional[str] = typer.Option(None, help="Output file path")
):
    """Generate Claude Desktop MCP configuration"""
    try:
        config = generate_claude_config()
        
        if output:
            output_path = Path(output)
            output_path.write_text(json.dumps(config, indent=2))
            rprint(f"[green]Configuration written to:[/green] {output}")
        else:
            rprint("[blue]Claude Desktop MCP Configuration:[/blue]")
            rprint(json.dumps(config, indent=2))
            
    except Exception as e:
        rprint(f"[red]Error generating configuration:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def generate_crewai_config(
    output: Optional[str] = typer.Option(None, help="Output file path")
):
    """Generate CrewAI integration configuration"""
    try:
        config = get_crewai_integration_config()
        
        if output:
            output_path = Path(output)
            output_path.write_text(json.dumps(config, indent=2))
            rprint(f"[green]Configuration written to:[/green] {output}")
        else:
            rprint("[blue]CrewAI Integration Configuration:[/blue]")
            rprint(json.dumps(config, indent=2))
            
    except Exception as e:
        rprint(f"[red]Error generating configuration:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def tools():
    """List available MCP tools"""
    table = Table(title="Available MCP Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Category", style="yellow")
    table.add_column("Description", style="green")
    
    # File System Tools
    table.add_row("read_file", "FileSystem", "Read contents of a file")
    table.add_row("write_file", "FileSystem", "Write content to a file")
    table.add_row("list_directory", "FileSystem", "List directory contents")
    table.add_row("file_exists", "FileSystem", "Check if file exists")
    table.add_row("get_file_info", "FileSystem", "Get detailed file information")
    
    # HTTP Tools
    table.add_row("http_get", "HTTP", "Make HTTP GET request")
    table.add_row("http_post", "HTTP", "Make HTTP POST request")
    table.add_row("http_put", "HTTP", "Make HTTP PUT request")
    table.add_row("http_delete", "HTTP", "Make HTTP DELETE request")
    
    # Environment Tools
    table.add_row("get_env_var", "Environment", "Get environment variable")
    table.add_row("list_env_vars", "Environment", "List environment variables")
    
    # Directory Tools
    table.add_row("ensure_upload_directory", "Directory", "Ensure user upload directory exists")
    table.add_row("get_thumbnail_path", "Directory", "Get thumbnail file path")
    table.add_row("cleanup_temp_files", "Directory", "Clean up temporary files")
    table.add_row("get_storage_stats", "Directory", "Get storage statistics")
    
    console.print(table)


@app.command()
def install():
    """Install MCP server (generate configs and setup instructions)"""
    try:
        # Create configs directory
        configs_dir = Path("configs")
        configs_dir.mkdir(exist_ok=True)
        
        # Generate Claude config
        claude_config = generate_claude_config()
        claude_config_path = configs_dir / "claude_desktop_config.json"
        claude_config_path.write_text(json.dumps(claude_config, indent=2))
        
        # Generate CrewAI config
        crewai_config = get_crewai_integration_config()
        crewai_config_path = configs_dir / "crewai_integration_config.json"
        crewai_config_path.write_text(json.dumps(crewai_config, indent=2))
        
        # Generate setup instructions
        instructions = """
# Terra Mystica MCP Server Setup

## Installation Complete!

The following configuration files have been generated:

1. **Claude Desktop Configuration**: `configs/claude_desktop_config.json`
2. **CrewAI Integration Configuration**: `configs/crewai_integration_config.json`

## Next Steps:

### 1. Claude Desktop Setup
Copy the contents of `claude_desktop_config.json` to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`

### 2. CrewAI Integration
Use the configuration in `crewai_integration_config.json` for your CrewAI agents.

### 3. Test the Server
Run the following command to test the MCP server:
```bash
python -m mcp.cli test
```

### 4. Start the Server
Start the MCP server with:
```bash
python -m mcp.cli serve
```

For SSE transport (web-based):
```bash
python -m mcp.cli serve --transport sse --host 0.0.0.0 --port 8001
```

## Available Commands:
- `mcp serve` - Start the MCP server
- `mcp config` - Show configuration
- `mcp test` - Test MCP tools
- `mcp tools` - List available tools
- `mcp generate-claude-config` - Generate Claude config
- `mcp generate-crewai-config` - Generate CrewAI config

## Environment Variables:
Set these environment variables for optimal configuration:
- `MCP_SERVER_NAME` - Server name
- `API_BASE_URL` - FastAPI base URL
- `MCP_TRANSPORT` - Transport type (stdio/sse)
- `MCP_LOG_LEVEL` - Logging level
"""
        
        readme_path = configs_dir / "SETUP.md"
        readme_path.write_text(instructions.strip())
        
        rprint("[green]✓ MCP Server installation complete![/green]")
        rprint(f"[blue]Configuration files:[/blue]")
        rprint(f"  - Claude Desktop: {claude_config_path}")
        rprint(f"  - CrewAI Integration: {crewai_config_path}")
        rprint(f"  - Setup Instructions: {readme_path}")
        rprint(f"\n[yellow]Next:[/yellow] Follow the instructions in {readme_path}")
        
    except Exception as e:
        rprint(f"[red]Installation failed:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()