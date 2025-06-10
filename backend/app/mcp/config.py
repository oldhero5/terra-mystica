"""
MCP Server Configuration and Manager
"""

import asyncio
import subprocess
import signal
from typing import Dict, List, Optional
from pathlib import Path

from app.core.config import settings
from app.core.logging import logger


class MCPServerManager:
    """Manage MCP servers for Terra Mystica"""
    
    def __init__(self):
        self.servers: Dict[str, subprocess.Popen] = {}
        self.base_dir = Path(__file__).parent
        
    def start_fastapi_server(self, port: Optional[int] = None) -> bool:
        """Start the FastAPI MCP server"""
        try:
            server_path = self.base_dir / "fastapi_server.py"
            cmd = ["python", str(server_path)]
            
            if port:
                cmd.extend(["--port", str(port)])
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.servers["fastapi"] = process
            logger.info(f"Started FastAPI MCP server (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start FastAPI MCP server: {str(e)}")
            return False
    
    def start_postgres_server(self, port: Optional[int] = None) -> bool:
        """Start the PostgreSQL MCP server"""
        try:
            server_path = self.base_dir / "postgres_server.py"
            cmd = ["python", str(server_path)]
            
            if port:
                cmd.extend(["--port", str(port)])
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.servers["postgres"] = process
            logger.info(f"Started PostgreSQL MCP server (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start PostgreSQL MCP server: {str(e)}")
            return False
    
    def start_all_servers(self) -> bool:
        """Start all MCP servers"""
        success = True
        
        if not self.start_fastapi_server():
            success = False
            
        if not self.start_postgres_server():
            success = False
            
        if success:
            logger.info("All MCP servers started successfully")
        else:
            logger.error("Some MCP servers failed to start")
            
        return success
    
    def stop_server(self, server_name: str) -> bool:
        """Stop a specific MCP server"""
        if server_name not in self.servers:
            logger.warning(f"Server {server_name} is not running")
            return False
            
        try:
            process = self.servers[server_name]
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            del self.servers[server_name]
            logger.info(f"Stopped {server_name} MCP server")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping {server_name} MCP server: {str(e)}")
            return False
    
    def stop_all_servers(self) -> bool:
        """Stop all MCP servers"""
        success = True
        
        for server_name in list(self.servers.keys()):
            if not self.stop_server(server_name):
                success = False
        
        if success:
            logger.info("All MCP servers stopped")
        else:
            logger.error("Some MCP servers failed to stop properly")
            
        return success
    
    def get_server_status(self) -> Dict[str, bool]:
        """Get status of all servers"""
        status = {}
        
        for server_name, process in self.servers.items():
            try:
                # Check if process is still running
                status[server_name] = process.poll() is None
            except:
                status[server_name] = False
        
        return status
    
    def restart_server(self, server_name: str) -> bool:
        """Restart a specific MCP server"""
        logger.info(f"Restarting {server_name} MCP server")
        
        # Stop the server if it's running
        if server_name in self.servers:
            self.stop_server(server_name)
        
        # Start the server
        if server_name == "fastapi":
            return self.start_fastapi_server()
        elif server_name == "postgres":
            return self.start_postgres_server()
        else:
            logger.error(f"Unknown server name: {server_name}")
            return False
    
    def restart_all_servers(self) -> bool:
        """Restart all MCP servers"""
        logger.info("Restarting all MCP servers")
        
        self.stop_all_servers()
        return self.start_all_servers()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup servers"""
        self.stop_all_servers()


# Global MCP server manager instance
mcp_manager = MCPServerManager()


def get_mcp_config() -> Dict[str, str]:
    """Get MCP server configuration for external clients"""
    return {
        "fastapi_server": {
            "transport": "stdio",
            "command": ["python", str(Path(__file__).parent / "fastapi_server.py")],
            "description": "Terra Mystica FastAPI operations"
        },
        "postgres_server": {
            "transport": "stdio", 
            "command": ["python", str(Path(__file__).parent / "postgres_server.py")],
            "description": "Terra Mystica PostgreSQL operations"
        }
    }


async def test_mcp_servers():
    """Test MCP servers functionality"""
    logger.info("Testing MCP servers...")
    
    try:
        # Test FastAPI server tools
        from app.mcp.fastapi_server import mcp as fastapi_mcp
        
        # Test directory listing
        result = await fastapi_mcp.tools["list_directory"]("/app/uploads")
        logger.info(f"FastAPI MCP test result: {result[:100]}...")
        
        # Test PostgreSQL server tools
        from app.mcp.postgres_server import mcp as postgres_mcp
        
        # Test database stats
        result = await postgres_mcp.tools["get_database_stats"]()
        logger.info(f"PostgreSQL MCP test result: {result[:100]}...")
        
        logger.info("MCP servers test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"MCP servers test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Start all MCP servers when run directly
    with mcp_manager:
        if mcp_manager.start_all_servers():
            print("MCP servers started. Press Ctrl+C to stop.")
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping MCP servers...")
        else:
            print("Failed to start MCP servers")
            exit(1)