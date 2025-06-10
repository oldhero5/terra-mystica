#!/usr/bin/env python3
"""
Terra Mystica MCP Server Startup Script
Convenient startup script for the MCP server with various options
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

def setup_environment():
    """Setup environment for MCP server"""
    # Add backend to Python path
    backend_path = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_path))
    
    # Set default environment variables
    env_defaults = {
        "MCP_SERVER_NAME": "Terra Mystica MCP Server",
        "API_BASE_URL": "http://localhost:8000",
        "MCP_LOG_LEVEL": "INFO",
        "MCP_BASE_PATH": str(backend_path),
    }
    
    for key, value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = value

def start_stdio_server():
    """Start MCP server with STDIO transport"""
    print("🚀 Starting Terra Mystica MCP Server (STDIO)")
    print("📡 Transport: STDIO")
    print("🔗 API URL:", os.getenv("API_BASE_URL"))
    print("📁 Base Path:", os.getenv("MCP_BASE_PATH"))
    print()
    
    try:
        from mcp.server import MCPServer
        server = MCPServer()
        server.run_stdio()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def start_sse_server(host="0.0.0.0", port=8001):
    """Start MCP server with SSE transport"""
    print("🚀 Starting Terra Mystica MCP Server (SSE)")
    print("📡 Transport: SSE")
    print(f"🌐 Server: http://{host}:{port}")
    print("🔗 API URL:", os.getenv("API_BASE_URL"))
    print("📁 Base Path:", os.getenv("MCP_BASE_PATH"))
    print()
    
    try:
        from mcp.server import MCPServer
        server = MCPServer()
        server.run_sse(host=host, port=port)
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def test_server():
    """Test MCP server functionality"""
    print("🧪 Testing Terra Mystica MCP Server")
    print()
    
    try:
        from mcp.server import get_mcp_server
        server = get_mcp_server()
        
        # Test file system
        print("📁 Testing File System Tools...")
        try:
            exists = server.fs_tools.file_exists(__file__)
            print(f"   ✅ File existence check: {exists}")
        except Exception as e:
            print(f"   ❌ File system error: {e}")
        
        # Test environment
        print("🔧 Testing Environment Tools...")
        try:
            config = server.env_tools.get_terra_mystica_config()
            print(f"   ✅ Configuration loaded: {len(config)} sections")
        except Exception as e:
            print(f"   ❌ Environment error: {e}")
        
        # Test directory
        print("📂 Testing Directory Tools...")
        try:
            stats = server.dir_tools.get_storage_stats()
            if "totals" in stats:
                print(f"   ✅ Storage stats: {stats['totals']['total_files']} files")
            else:
                print("   ⚠️  Storage stats incomplete")
        except Exception as e:
            print(f"   ❌ Directory error: {e}")
        
        # Test HTTP (async)
        print("🌐 Testing HTTP Tools...")
        import asyncio
        async def test_http():
            try:
                health = await server.http_tools.health_check()
                if health.get("success"):
                    print(f"   ✅ Health check: {health['data']}")
                else:
                    print(f"   ⚠️  Health check failed: {health.get('error', 'Unknown')}")
            except Exception as e:
                print(f"   ❌ HTTP error: {e}")
        
        asyncio.run(test_http())
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

def install_configs():
    """Install MCP configuration files"""
    print("📦 Installing Terra Mystica MCP Server configurations")
    
    try:
        from mcp.config import generate_claude_config, get_crewai_integration_config
        
        # Create configs directory
        configs_dir = Path("configs")
        configs_dir.mkdir(exist_ok=True)
        
        # Generate Claude Desktop config
        claude_config = generate_claude_config()
        claude_path = configs_dir / "claude_desktop_config.json"
        claude_path.write_text(json.dumps(claude_config, indent=2))
        print(f"✅ Claude Desktop config: {claude_path}")
        
        # Generate CrewAI config
        crewai_config = get_crewai_integration_config()
        crewai_path = configs_dir / "crewai_integration_config.json"
        crewai_path.write_text(json.dumps(crewai_config, indent=2))
        print(f"✅ CrewAI integration config: {crewai_path}")
        
        # Create environment file template
        env_template = """# Terra Mystica MCP Server Environment Variables

# Server Configuration
MCP_SERVER_NAME="Terra Mystica MCP Server"
MCP_TRANSPORT=stdio  # or 'sse' for web-based
MCP_HOST=0.0.0.0
MCP_PORT=8001
MCP_LOG_LEVEL=INFO

# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30.0

# Security
MCP_AUTH_ENABLED=false
MCP_AUTH_SECRET=your-secret-here

# File System
MCP_BASE_PATH=/Users/marty/repos/terra-mystica/backend
"""
        
        env_path = configs_dir / ".env.mcp"
        env_path.write_text(env_template)
        print(f"✅ Environment template: {env_path}")
        
        # Create setup instructions
        setup_md = """# Terra Mystica MCP Server Setup

## Quick Start

1. **Install dependencies**:
   ```bash
   cd backend
   uv pip install -e .
   ```

2. **Configure environment**:
   ```bash
   cp configs/.env.mcp .env
   # Edit .env with your settings
   ```

3. **Start MCP server**:
   ```bash
   python scripts/start_mcp_server.py --transport stdio
   ```

4. **Test functionality**:
   ```bash
   python scripts/start_mcp_server.py --test
   ```

## Claude Desktop Setup

Copy the contents of `configs/claude_desktop_config.json` to:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`

## CrewAI Integration

Use the configuration in `configs/crewai_integration_config.json` for your CrewAI agents.

## Available Commands

- `python scripts/start_mcp_server.py` - Start STDIO server
- `python scripts/start_mcp_server.py --transport sse` - Start SSE server  
- `python scripts/start_mcp_server.py --test` - Test functionality
- `python scripts/start_mcp_server.py --install` - Install configs

## Environment Variables

See `configs/.env.mcp` for all available configuration options.
"""
        
        setup_path = configs_dir / "SETUP.md"
        setup_path.write_text(setup_md)
        print(f"✅ Setup instructions: {setup_path}")
        
        print(f"\n🎉 Installation complete! Check {configs_dir} for all files.")
        print(f"📖 Next steps: Read {setup_path}")
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Terra Mystica MCP Server Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_mcp_server.py                    # Start STDIO server
  python start_mcp_server.py --transport sse    # Start SSE server
  python start_mcp_server.py --test             # Test functionality
  python start_mcp_server.py --install          # Install configs
        """
    )
    
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse"], 
        default="stdio",
        help="Transport type (default: stdio)"
    )
    
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="Host for SSE transport (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8001,
        help="Port for SSE transport (default: 8001)"
    )
    
    parser.add_argument(
        "--test", 
        action="store_true",
        help="Test MCP server functionality"
    )
    
    parser.add_argument(
        "--install", 
        action="store_true",
        help="Install MCP configuration files"
    )
    
    parser.add_argument(
        "--api-url", 
        default="http://localhost:8000",
        help="FastAPI base URL (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Override API URL if provided
    if args.api_url:
        os.environ["API_BASE_URL"] = args.api_url
    
    # Handle different commands
    if args.install:
        install_configs()
    elif args.test:
        test_server()
    elif args.transport == "stdio":
        start_stdio_server()
    elif args.transport == "sse":
        start_sse_server(args.host, args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()