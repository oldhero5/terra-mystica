"""
MCP integration for Terra Mystica FastAPI application
"""

import asyncio
from typing import Dict, Any
from fastapi import FastAPI

from app.core.logging import logger
from app.mcp.config import mcp_manager, get_mcp_config, test_mcp_servers


def setup_mcp_integration(app: FastAPI) -> Dict[str, Any]:
    """
    Set up MCP server integration with FastAPI application
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Dictionary with MCP integration status
    """
    try:
        # Start MCP servers
        success = mcp_manager.start_all_servers()
        
        config = get_mcp_config()
        
        integration_info = {
            "enabled": success,
            "servers": config,
            "status": mcp_manager.get_server_status() if success else {}
        }
        
        if success:
            logger.info("MCP integration setup completed successfully")
        else:
            logger.error("MCP integration setup failed")
            
        return integration_info
        
    except Exception as e:
        logger.error(f"Error setting up MCP integration: {str(e)}")
        return {
            "enabled": False,
            "error": str(e),
            "servers": {},
            "status": {}
        }


async def mcp_health() -> Dict[str, Any]:
    """
    Check health of all MCP servers
    
    Returns:
        Dictionary with health status of each server
    """
    try:
        server_status = mcp_manager.get_server_status()
        
        overall_health = all(server_status.values()) if server_status else False
        
        return {
            "healthy": overall_health,
            "servers": server_status,
            "total_servers": len(server_status),
            "healthy_servers": sum(1 for status in server_status.values() if status)
        }
        
    except Exception as e:
        logger.error(f"Error checking MCP health: {str(e)}")
        return {
            "healthy": False,
            "error": str(e),
            "servers": {},
            "total_servers": 0,
            "healthy_servers": 0
        }


async def mcp_info() -> Dict[str, Any]:
    """
    Get information about MCP servers and their capabilities
    
    Returns:
        Dictionary with MCP server information
    """
    try:
        config = get_mcp_config()
        status = mcp_manager.get_server_status()
        
        # Get tool information for each server
        tools_info = {}
        
        # FastAPI server tools
        try:
            from app.mcp.fastapi_server import mcp as fastapi_mcp
            tools_info["fastapi"] = {
                "tool_count": len(fastapi_mcp.tools),
                "tools": list(fastapi_mcp.tools.keys())
            }
        except Exception as e:
            tools_info["fastapi"] = {"error": str(e)}
        
        # PostgreSQL server tools
        try:
            from app.mcp.postgres_server import mcp as postgres_mcp
            tools_info["postgres"] = {
                "tool_count": len(postgres_mcp.tools),
                "tools": list(postgres_mcp.tools.keys())
            }
        except Exception as e:
            tools_info["postgres"] = {"error": str(e)}
        
        return {
            "config": config,
            "status": status,
            "tools": tools_info,
            "description": "Terra Mystica MCP Server Integration"
        }
        
    except Exception as e:
        logger.error(f"Error getting MCP info: {str(e)}")
        return {
            "error": str(e),
            "config": {},
            "status": {},
            "tools": {}
        }


async def test_mcp_integration() -> Dict[str, Any]:
    """
    Test MCP server integration functionality
    
    Returns:
        Dictionary with test results
    """
    try:
        logger.info("Testing MCP integration...")
        
        # Test server health first
        health = await mcp_health()
        
        if not health["healthy"]:
            return {
                "success": False,
                "error": "MCP servers are not healthy",
                "health": health,
                "tests": {}
            }
        
        # Run MCP server tests
        test_result = await test_mcp_servers()
        
        return {
            "success": test_result,
            "health": health,
            "tests": {
                "mcp_servers": test_result
            },
            "message": "MCP integration test completed" if test_result else "MCP integration test failed"
        }
        
    except Exception as e:
        logger.error(f"Error testing MCP integration: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "health": {},
            "tests": {}
        }


async def restart_mcp_servers() -> Dict[str, Any]:
    """
    Restart all MCP servers
    
    Returns:
        Dictionary with restart results
    """
    try:
        logger.info("Restarting MCP servers...")
        
        success = mcp_manager.restart_all_servers()
        status = mcp_manager.get_server_status()
        
        return {
            "success": success,
            "status": status,
            "message": "MCP servers restarted successfully" if success else "Failed to restart MCP servers"
        }
        
    except Exception as e:
        logger.error(f"Error restarting MCP servers: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "status": {}
        }


def shutdown_mcp_integration():
    """
    Shutdown MCP integration and stop all servers
    """
    try:
        logger.info("Shutting down MCP integration...")
        mcp_manager.stop_all_servers()
        logger.info("MCP integration shutdown completed")
    except Exception as e:
        logger.error(f"Error shutting down MCP integration: {str(e)}")


# Export functions for use in main.py
__all__ = [
    "setup_mcp_integration",
    "mcp_health", 
    "mcp_info",
    "test_mcp_integration",
    "restart_mcp_servers",
    "shutdown_mcp_integration"
]