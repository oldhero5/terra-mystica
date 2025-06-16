"""
MCP Tools for CrewAI Agents
Integrates Model Context Protocol tools with CrewAI agents
"""

from typing import Any, Dict, List, Optional
import asyncio
from functools import wraps

from crewai.tools import BaseTool
try:
    from mcp import Client
    from mcp.types import Tool as MCPTool
except ImportError:
    # Fallback if MCP is not available
    Client = None
    MCPTool = None

from app.core.logging import logger


def async_to_sync(async_func):
    """Convert async function to sync for CrewAI compatibility"""
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


class MCPToolWrapper(BaseTool):
    """Wrapper to make MCP tools compatible with CrewAI"""
    
    name: str = "MCP Tool"
    description: str = "MCP Tool for external data access"
    
    def __init__(self, mcp_tool, mcp_client):
        self.mcp_tool = mcp_tool
        self.mcp_client = mcp_client
        if mcp_tool and hasattr(mcp_tool, 'name'):
            self.name = mcp_tool.name
            self.description = getattr(mcp_tool, 'description', f"MCP tool: {mcp_tool.name}")
        super().__init__()
    
    @async_to_sync
    async def _run(self, **kwargs) -> str:
        """Execute the MCP tool with provided arguments"""
        try:
            result = await self.mcp_client.call_tool(self.mcp_tool.name, kwargs)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing MCP tool {self.name}: {str(e)}")
            return f"Error: {str(e)}"


class GeographicDatabaseTool(BaseTool):
    """Search geographic databases for location information"""
    
    name: str = "Geographic Database Search"
    description: str = "Search geographic databases for location features and landmarks"
    
    def __init__(self, mcp_client=None):
        super().__init__()
        # Store in __dict__ to avoid Pydantic field validation
        object.__setattr__(self, '_mcp_client', mcp_client)
    
    @async_to_sync
    async def _run(self, query: str) -> str:
        """Search geographic databases"""
        try:
            if getattr(self, '_mcp_client', None):
                # Use MCP for external database access
                result = await self.mcp_client.call_tool(
                    "search_geographic_db",
                    {"query": query}
                )
                return str(result)
            else:
                # Fallback to mock data
                return f"Geographic search results for '{query}': Mountain ranges, coastal features, urban areas..."
        except Exception as e:
            logger.error(f"Geographic database search error: {str(e)}")
            return f"Search error: {str(e)}"


class WeatherDataTool(BaseTool):
    """Query weather and climate data"""
    
    name: str = "Weather Data Query"
    description: str = "Query historical weather and climate data for location verification"
    
    def __init__(self, mcp_client=None):
        super().__init__()
        self.mcp_client = mcp_client
    
    @async_to_sync
    async def _run(self, location: str, date_range: Optional[str] = None) -> str:
        """Query weather data for a location"""
        try:
            if self.mcp_client:
                # Use MCP for weather API access
                result = await self.mcp_client.call_tool(
                    "query_weather",
                    {"location": location, "date_range": date_range}
                )
                return str(result)
            else:
                # Fallback to mock data
                return f"Weather data for {location}: Temperate climate, average temp 15°C, moderate rainfall"
        except Exception as e:
            logger.error(f"Weather data query error: {str(e)}")
            return f"Query error: {str(e)}"


class CulturalDatabaseTool(BaseTool):
    """Search cultural and historical databases"""
    
    name: str = "Cultural Database Search"
    description: str = "Search cultural, linguistic, and historical databases for regional information"
    
    def __init__(self, mcp_client=None):
        super().__init__()
        self.mcp_client = mcp_client
    
    @async_to_sync
    async def _run(self, query: str) -> str:
        """Search cultural databases"""
        try:
            if self.mcp_client:
                # Use MCP for cultural database access
                result = await self.mcp_client.call_tool(
                    "search_cultural_db",
                    {"query": query}
                )
                return str(result)
            else:
                # Fallback to mock data
                return f"Cultural search for '{query}': Language patterns, architectural styles, customs..."
        except Exception as e:
            logger.error(f"Cultural database search error: {str(e)}")
            return f"Search error: {str(e)}"


class SatelliteImageryTool(BaseTool):
    """Access satellite imagery for verification"""
    
    name: str = "Satellite Imagery Access"
    description: str = "Access satellite imagery archives for location verification"
    
    def __init__(self, mcp_client=None):
        super().__init__()
        self.mcp_client = mcp_client
    
    @async_to_sync
    async def _run(self, coordinates: str, date: Optional[str] = None) -> str:
        """Access satellite imagery for given coordinates"""
        try:
            if self.mcp_client:
                # Use MCP for satellite imagery access
                result = await self.mcp_client.call_tool(
                    "get_satellite_imagery",
                    {"coordinates": coordinates, "date": date}
                )
                return str(result)
            else:
                # Fallback to mock data
                return f"Satellite imagery for {coordinates}: Urban area visible, vegetation index 0.7"
        except Exception as e:
            logger.error(f"Satellite imagery access error: {str(e)}")
            return f"Access error: {str(e)}"


class MCPToolsManager:
    """Manage MCP tools for CrewAI agents"""
    
    def __init__(self, mcp_client=None):
        self.mcp_client = mcp_client
        self._tools_cache: Dict[str, BaseTool] = {}
    
    async def initialize(self):
        """Initialize MCP client and discover available tools"""
        if self.mcp_client:
            try:
                # Get available tools from MCP
                tools = await self.mcp_client.list_tools()
                
                # Wrap each MCP tool for CrewAI
                for tool in tools:
                    wrapped_tool = MCPToolWrapper(tool, self.mcp_client)
                    self._tools_cache[tool.name] = wrapped_tool
                    
                logger.info(f"Initialized {len(tools)} MCP tools for CrewAI")
            except Exception as e:
                logger.error(f"Failed to initialize MCP tools: {str(e)}")
    
    def get_research_tools(self) -> List[BaseTool]:
        """Get all research tools for the Research Agent"""
        tools = [
            GeographicDatabaseTool(self.mcp_client),
            WeatherDataTool(self.mcp_client),
            CulturalDatabaseTool(self.mcp_client),
            SatelliteImageryTool(self.mcp_client),
        ]
        
        # Add any discovered MCP tools
        tools.extend(self._tools_cache.values())
        
        return tools
    
    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """Get a specific tool by name"""
        # Check cache first
        if name in self._tools_cache:
            return self._tools_cache[name]
        
        # Check predefined tools
        predefined_tools = {
            "geographic_database": GeographicDatabaseTool(self.mcp_client),
            "weather_data": WeatherDataTool(self.mcp_client),
            "cultural_database": CulturalDatabaseTool(self.mcp_client),
            "satellite_imagery": SatelliteImageryTool(self.mcp_client),
        }
        
        return predefined_tools.get(name)