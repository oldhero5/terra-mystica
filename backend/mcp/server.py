"""
Terra Mystica MCP Server
Main MCP server implementation using FastMCP
"""

import os
import asyncio
from typing import Dict, Any, Optional
from fastmcp import FastMCP
import structlog

from .tools import (
    FileSystemTools,
    HTTPTools, 
    EnvironmentTools,
    DirectoryTools,
)

logger = structlog.get_logger(__name__)


class MCPServer:
    """
    Terra Mystica MCP Server for CrewAI agent integration
    
    Provides tools for:
    - File system operations (read/write files)
    - HTTP requests to FastAPI endpoints
    - Environment variable access
    - Directory operations for uploads/thumbnails
    """
    
    def __init__(self, 
                 name: str = "Terra Mystica MCP Server",
                 version: str = "1.0.0",
                 api_base_url: str = "http://localhost:8000"):
        """
        Initialize MCP server
        
        Args:
            name: Server name
            version: Server version
            api_base_url: Base URL for FastAPI application
        """
        self.name = name
        self.version = version
        self.api_base_url = api_base_url
        
        # Initialize FastMCP server
        self.mcp = FastMCP(name)
        
        # Initialize tool handlers
        self.fs_tools = FileSystemTools()
        self.http_tools = HTTPTools(api_base_url)
        self.env_tools = EnvironmentTools()
        self.dir_tools = DirectoryTools()
        
        # Register all tools
        self._register_tools()
        
        logger.info("MCP Server initialized", 
                   name=name, version=version, api_base_url=api_base_url)
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        # File System Tools
        @self.mcp.tool()
        def read_file(file_path: str) -> str:
            """
            Read contents of a file
            
            Args:
                file_path: Path to the file to read
                
            Returns:
                File contents as string
            """
            return self.fs_tools.read_file(file_path)
        
        @self.mcp.tool()
        def write_file(file_path: str, content: str, create_dirs: bool = True) -> str:
            """
            Write content to a file
            
            Args:
                file_path: Path to the file to write
                content: Content to write to the file
                create_dirs: Whether to create parent directories if they don't exist
                
            Returns:
                Success message
            """
            return self.fs_tools.write_file(file_path, content, create_dirs)
        
        @self.mcp.tool()
        def list_directory(directory_path: str, include_hidden: bool = False) -> Dict[str, Any]:
            """
            List contents of a directory
            
            Args:
                directory_path: Path to the directory to list
                include_hidden: Whether to include hidden files/directories
                
            Returns:
                Dictionary with directory contents information
            """
            return self.fs_tools.list_directory(directory_path, include_hidden)
        
        @self.mcp.tool()
        def file_exists(file_path: str) -> bool:
            """
            Check if a file or directory exists
            
            Args:
                file_path: Path to check
                
            Returns:
                True if file/directory exists, False otherwise
            """
            return self.fs_tools.file_exists(file_path)
        
        @self.mcp.tool()
        def get_file_info(file_path: str) -> Dict[str, Any]:
            """
            Get detailed information about a file
            
            Args:
                file_path: Path to the file
                
            Returns:
                Dictionary with file information (size, modified time, etc.)
            """
            return self.fs_tools.get_file_info(file_path)
        
        # HTTP Tools
        @self.mcp.tool()
        async def http_get(endpoint: str, params: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
            """
            Make HTTP GET request to FastAPI endpoint
            
            Args:
                endpoint: API endpoint (relative to base URL)
                params: Query parameters
                headers: Request headers
                
            Returns:
                Response data as dictionary
            """
            return await self.http_tools.get(endpoint, params, headers)
        
        @self.mcp.tool()
        async def http_post(endpoint: str, data: Optional[Dict[str, Any]] = None,
                           json: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
            """
            Make HTTP POST request to FastAPI endpoint
            
            Args:
                endpoint: API endpoint (relative to base URL)
                data: Form data
                json: JSON data
                headers: Request headers
                
            Returns:
                Response data as dictionary
            """
            return await self.http_tools.post(endpoint, data, json, headers)
        
        @self.mcp.tool()
        async def http_put(endpoint: str, data: Optional[Dict[str, Any]] = None,
                          json: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
            """
            Make HTTP PUT request to FastAPI endpoint
            
            Args:
                endpoint: API endpoint (relative to base URL)
                data: Form data
                json: JSON data
                headers: Request headers
                
            Returns:
                Response data as dictionary
            """
            return await self.http_tools.put(endpoint, data, json, headers)
        
        @self.mcp.tool()
        async def http_delete(endpoint: str, params: Optional[Dict[str, Any]] = None,
                             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
            """
            Make HTTP DELETE request to FastAPI endpoint
            
            Args:
                endpoint: API endpoint (relative to base URL)
                params: Query parameters
                headers: Request headers
                
            Returns:
                Response data as dictionary
            """
            return await self.http_tools.delete(endpoint, params, headers)
        
        # Environment Tools
        @self.mcp.tool()
        def get_env_var(var_name: str, default: Optional[str] = None) -> Optional[str]:
            """
            Get environment variable value
            
            Args:
                var_name: Environment variable name
                default: Default value if variable not found
                
            Returns:
                Environment variable value or default
            """
            return self.env_tools.get_env_var(var_name, default)
        
        @self.mcp.tool()
        def list_env_vars(prefix: Optional[str] = None) -> Dict[str, str]:
            """
            List environment variables
            
            Args:
                prefix: Optional prefix to filter variables
                
            Returns:
                Dictionary of environment variables
            """
            return self.env_tools.list_env_vars(prefix)
        
        # Directory Tools
        @self.mcp.tool()
        def ensure_upload_directory(user_id: int) -> str:
            """
            Ensure user upload directory exists
            
            Args:
                user_id: User ID
                
            Returns:
                Path to user upload directory
            """
            return self.dir_tools.ensure_upload_directory(user_id)
        
        @self.mcp.tool()
        def get_thumbnail_path(image_filename: str, size: str = "medium") -> str:
            """
            Get thumbnail file path for an image
            
            Args:
                image_filename: Original image filename
                size: Thumbnail size (small, medium, large)
                
            Returns:
                Path to thumbnail file
            """
            return self.dir_tools.get_thumbnail_path(image_filename, size)
        
        @self.mcp.tool()
        def cleanup_temp_files(max_age_hours: int = 24) -> Dict[str, Any]:
            """
            Clean up temporary files older than specified age
            
            Args:
                max_age_hours: Maximum age in hours for temp files
                
            Returns:
                Dictionary with cleanup results
            """
            return self.dir_tools.cleanup_temp_files(max_age_hours)
        
        @self.mcp.tool()
        def get_storage_stats() -> Dict[str, Any]:
            """
            Get storage statistics for uploads and thumbnails
            
            Returns:
                Dictionary with storage statistics
            """
            return self.dir_tools.get_storage_stats()
    
    def run_stdio(self):
        """Run MCP server with STDIO transport (default)"""
        logger.info("Starting MCP server with STDIO transport")
        self.mcp.run()
    
    def run_sse(self, host: str = "0.0.0.0", port: int = 8001):
        """Run MCP server with SSE transport"""
        logger.info("Starting MCP server with SSE transport", host=host, port=port)
        self.mcp.run_sse(host=host, port=port)
    
    def get_fastapi_app(self):
        """Get FastAPI app for integration with main application"""
        return self.mcp.create_app()


# Global MCP server instance
mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Get or create global MCP server instance"""
    global mcp_server
    if mcp_server is None:
        api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        mcp_server = MCPServer(api_base_url=api_base_url)
    return mcp_server


async def start_mcp_server():
    """Start MCP server as async task"""
    server = get_mcp_server()
    # Run in background task
    asyncio.create_task(server.run_stdio())


if __name__ == "__main__":
    # Run MCP server standalone
    server = MCPServer()
    server.run_stdio()