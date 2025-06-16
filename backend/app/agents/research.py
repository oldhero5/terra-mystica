from typing import List, Optional
from crewai.tools import tool

from .base import BaseGeoAgent, AgentConfig
from .tools import MCPToolsManager
from .tools.simple_tools import SimpleToolsManager


class ResearchAgent(BaseGeoAgent):
    def __init__(self, config: AgentConfig = None, mcp_client=None):
        self.mcp_client = mcp_client
        self.mcp_tools_manager = MCPToolsManager(mcp_client) if mcp_client else None
        self.simple_tools_manager = SimpleToolsManager()
        super().__init__(
            name="Research Specialist",
            role="External Data Research and Verification Expert",
            goal="Gather and analyze external data sources to support location identification",
            backstory="""You are a skilled research analyst specializing in open-source 
            intelligence (OSINT) and data aggregation. Your expertise lies in quickly 
            finding and synthesizing information from multiple external sources including 
            geographic databases, weather services, cultural repositories, and satellite 
            imagery archives. You excel at using various APIs and data services to gather 
            supporting evidence for location verification. Your systematic research approach 
            and ability to correlate disparate data sources make you invaluable for 
            confirming geographic predictions with real-world data.""",
            config=config,
        )

    def get_tools(self) -> List:
        tools = [
            self.search_geographic_database_tool,
            self.query_weather_data_tool,
            self.lookup_cultural_info_tool,
        ]
        
        # Add MCP tools if manager is available, otherwise use simple tools
        if self.mcp_tools_manager:
            mcp_tools = self.mcp_tools_manager.get_research_tools()
            tools.extend(mcp_tools)
        else:
            # Use simple tools for testing and fallback
            simple_tools = self.simple_tools_manager.get_research_tools()
            tools.extend(simple_tools)
            
        return tools

    @tool("Search Geographic Database")
    def search_geographic_database_tool(self, location_features: str) -> str:
        """
        Search geographic databases for matching location features.
        Args:
            location_features: Description of geographic features to search
        Returns:
            Database search results with potential matches
        """
        return f"Searching geographic database for: {location_features}"

    @tool("Query Weather Data")
    def query_weather_data_tool(self, climate_indicators: str, time_period: str) -> str:
        """
        Query historical weather data to verify climate conditions.
        Args:
            climate_indicators: Observed weather/climate conditions
            time_period: Estimated time period of the image
        Returns:
            Weather data analysis and location correlation
        """
        return f"Querying weather data for indicators: {climate_indicators} during {time_period}"

    @tool("Lookup Cultural Information")
    def lookup_cultural_info_tool(self, cultural_markers: str) -> str:
        """
        Look up cultural information databases for specific markers.
        Args:
            cultural_markers: Cultural elements to research
        Returns:
            Cultural database results and geographic associations
        """
        return f"Looking up cultural information for: {cultural_markers}"

    @tool("MCP Search External Sources")
    def mcp_search_tool(self, query: str) -> str:
        """
        Use MCP to search external data sources.
        Args:
            query: Search query for external sources
        Returns:
            Search results from MCP-connected sources
        """
        if not self.mcp_client:
            return "MCP client not available"
        
        # This will be implemented to actually use MCP
        return f"MCP search for: {query}"

    @tool("MCP Query Geographic Database")
    def mcp_query_database_tool(self, query: str) -> str:
        """
        Use MCP to query specific geographic databases.
        Args:
            query: Database query
        Returns:
            Query results from MCP-connected databases
        """
        if not self.mcp_client:
            return "MCP client not available"
        
        # This will be implemented to actually use MCP
        return f"MCP database query: {query}"