"""
Simplified tools that don't require complex MCP integration for testing
"""

from typing import Any, Dict, List, Optional
from crewai.tools import BaseTool

from app.core.logging import logger


class SimpleGeographicTool(BaseTool):
    """Simple geographic database search tool"""
    
    name: str = "Geographic Database Search"
    description: str = "Search geographic databases for location features and landmarks"
    
    def _run(self, query: str) -> str:
        """Search geographic databases"""
        # Mock geographic search
        return f"Geographic search results for '{query}': Mountain ranges, coastal features, urban areas found"


class SimpleWeatherTool(BaseTool):
    """Simple weather data query tool"""
    
    name: str = "Weather Data Query"
    description: str = "Query historical weather and climate data for location verification"
    
    def _run(self, location: str, date_range: str = None) -> str:
        """Query weather data for a location"""
        # Mock weather data
        return f"Weather data for {location}: Temperate climate, average temp 15°C, moderate rainfall"


class SimpleCulturalTool(BaseTool):
    """Simple cultural database search tool"""
    
    name: str = "Cultural Database Search"
    description: str = "Search cultural, linguistic, and historical databases for regional information"
    
    def _run(self, query: str) -> str:
        """Search cultural databases"""
        # Mock cultural search
        return f"Cultural search for '{query}': Language patterns, architectural styles, customs found"


class SimpleSatelliteTool(BaseTool):
    """Simple satellite imagery access tool"""
    
    name: str = "Satellite Imagery Access"
    description: str = "Access satellite imagery archives for location verification"
    
    def _run(self, coordinates: str, date: str = None) -> str:
        """Access satellite imagery for given coordinates"""
        # Mock satellite data
        return f"Satellite imagery for {coordinates}: Urban area visible, vegetation index 0.7"


class SimpleToolsManager:
    """Manage simple tools for testing"""
    
    def __init__(self):
        self._tools_cache: Dict[str, BaseTool] = {}
    
    def get_research_tools(self) -> List[BaseTool]:
        """Get all research tools"""
        return [
            SimpleGeographicTool(),
            SimpleWeatherTool(),
            SimpleCulturalTool(),
            SimpleSatelliteTool(),
        ]
    
    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """Get a specific tool by name"""
        tools_map = {
            "geographic_database": SimpleGeographicTool(),
            "weather_data": SimpleWeatherTool(),
            "cultural_database": SimpleCulturalTool(),
            "satellite_imagery": SimpleSatelliteTool(),
        }
        return tools_map.get(name)