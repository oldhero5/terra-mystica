"""
Tests for MCP tools integration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.agents.tools.mcp_tools import (
    MCPToolWrapper,
    GeographicDatabaseTool,
    WeatherDataTool,
    CulturalDatabaseTool,
    SatelliteImageryTool,
    MCPToolsManager,
)


class TestMCPToolWrapper:
    """Test MCP tool wrapper"""
    
    def test_wrapper_creation(self):
        """Test creating an MCP tool wrapper"""
        mock_mcp_tool = Mock()
        mock_mcp_tool.name = "test_tool"
        mock_mcp_tool.description = "Test tool description"
        
        mock_client = Mock()
        
        wrapper = MCPToolWrapper(mock_mcp_tool, mock_client)
        
        assert wrapper.name == "test_tool"
        assert wrapper.description == "Test tool description"
        assert wrapper.mcp_client == mock_client
    
    @patch('asyncio.new_event_loop')
    @patch('asyncio.set_event_loop')
    def test_wrapper_execution(self, mock_set_loop, mock_new_loop):
        """Test executing an MCP tool"""
        # Setup mocks
        mock_mcp_tool = Mock()
        mock_mcp_tool.name = "test_tool"
        
        mock_client = Mock()
        mock_client.call_tool = AsyncMock(return_value={"result": "success"})
        
        mock_loop = Mock()
        mock_loop.run_until_complete = Mock(return_value='{"result": "success"}')
        mock_loop.close = Mock()
        mock_new_loop.return_value = mock_loop
        
        wrapper = MCPToolWrapper(mock_mcp_tool, mock_client)
        
        # Execute tool
        result = wrapper._run(test_param="value")
        
        assert result == '{"result": "success"}'
        mock_loop.close.assert_called_once()


class TestSpecializedTools:
    """Test specialized MCP tools"""
    
    def test_geographic_database_tool(self):
        """Test GeographicDatabaseTool"""
        tool = GeographicDatabaseTool()
        
        assert tool.name == "Geographic Database Search"
        assert "geographic databases" in tool.description.lower()
        
        # Test without MCP client (fallback)
        result = tool._run(query="Mount Everest")
        assert "Geographic search results" in result
    
    def test_weather_data_tool(self):
        """Test WeatherDataTool"""
        tool = WeatherDataTool()
        
        assert tool.name == "Weather Data Query"
        assert "weather" in tool.description.lower()
        
        # Test without MCP client (fallback)
        result = tool._run(location="New York", date_range="2024-01")
        assert "Weather data" in result
    
    def test_cultural_database_tool(self):
        """Test CulturalDatabaseTool"""
        tool = CulturalDatabaseTool()
        
        assert tool.name == "Cultural Database Search"
        assert "cultural" in tool.description.lower()
        
        # Test without MCP client (fallback)
        result = tool._run(query="Japanese architecture")
        assert "Cultural search" in result
    
    def test_satellite_imagery_tool(self):
        """Test SatelliteImageryTool"""
        tool = SatelliteImageryTool()
        
        assert tool.name == "Satellite Imagery Access"
        assert "satellite" in tool.description.lower()
        
        # Test without MCP client (fallback)
        result = tool._run(coordinates="40.7128,-74.0060")
        assert "Satellite imagery" in result


class TestMCPToolsWithClient:
    """Test tools with MCP client"""
    
    @patch('asyncio.new_event_loop')
    @patch('asyncio.set_event_loop')
    def test_geographic_tool_with_mcp(self, mock_set_loop, mock_new_loop):
        """Test geographic tool with MCP client"""
        # Setup mocks
        mock_client = Mock()
        mock_client.call_tool = AsyncMock(
            return_value={"locations": ["Mount Everest", "Himalayas"]}
        )
        
        mock_loop = Mock()
        mock_loop.run_until_complete = Mock(
            return_value='{"locations": ["Mount Everest", "Himalayas"]}'
        )
        mock_loop.close = Mock()
        mock_new_loop.return_value = mock_loop
        
        tool = GeographicDatabaseTool(mcp_client=mock_client)
        result = tool._run(query="highest mountain")
        
        assert "locations" in result


class TestMCPToolsManager:
    """Test MCP tools manager"""
    
    def test_manager_creation(self):
        """Test creating tools manager"""
        manager = MCPToolsManager()
        
        assert manager.mcp_client is None
        assert isinstance(manager._tools_cache, dict)
    
    def test_manager_with_client(self):
        """Test manager with MCP client"""
        mock_client = Mock()
        manager = MCPToolsManager(mcp_client=mock_client)
        
        assert manager.mcp_client == mock_client
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test manager initialization with MCP"""
        mock_client = Mock()
        mock_tool1 = Mock(name="tool1", description="Tool 1")
        mock_tool2 = Mock(name="tool2", description="Tool 2")
        mock_client.list_tools = AsyncMock(return_value=[mock_tool1, mock_tool2])
        
        manager = MCPToolsManager(mcp_client=mock_client)
        await manager.initialize()
        
        assert len(manager._tools_cache) == 2
        assert "tool1" in manager._tools_cache
        assert "tool2" in manager._tools_cache
    
    def test_get_research_tools(self):
        """Test getting research tools"""
        manager = MCPToolsManager()
        tools = manager.get_research_tools()
        
        assert len(tools) >= 4  # At least the 4 predefined tools
        
        # Check tool types
        tool_names = [tool.name for tool in tools]
        assert "Geographic Database Search" in tool_names
        assert "Weather Data Query" in tool_names
        assert "Cultural Database Search" in tool_names
        assert "Satellite Imagery Access" in tool_names
    
    def test_get_tool_by_name(self):
        """Test getting specific tool by name"""
        manager = MCPToolsManager()
        
        # Test predefined tools
        geo_tool = manager.get_tool_by_name("geographic_database")
        assert geo_tool is not None
        assert geo_tool.name == "Geographic Database Search"
        
        weather_tool = manager.get_tool_by_name("weather_data")
        assert weather_tool is not None
        assert weather_tool.name == "Weather Data Query"
        
        # Test non-existent tool
        none_tool = manager.get_tool_by_name("non_existent")
        assert none_tool is None


@pytest.mark.asyncio
class TestMCPIntegrationScenarios:
    """Test complete MCP integration scenarios"""
    
    async def test_research_agent_with_mcp_tools(self):
        """Test research agent using MCP tools"""
        from app.agents.research import ResearchAgent
        
        # Create mock MCP client
        mock_client = Mock()
        mock_client.list_tools = AsyncMock(return_value=[])
        
        # Create research agent with MCP
        with patch('app.agents.base.ChatOpenAI'):
            agent = ResearchAgent(mcp_client=mock_client)
            
            # Verify tools include MCP tools
            tools = agent.get_tools()
            assert len(tools) > 3  # Base tools + MCP tools
    
    async def test_tool_error_handling(self):
        """Test error handling in MCP tools"""
        mock_client = Mock()
        mock_client.call_tool = AsyncMock(side_effect=Exception("MCP error"))
        
        tool = GeographicDatabaseTool(mcp_client=mock_client)
        
        with patch('asyncio.new_event_loop') as mock_new_loop:
            mock_loop = Mock()
            mock_loop.run_until_complete = Mock(return_value="Error: MCP error")
            mock_loop.close = Mock()
            mock_new_loop.return_value = mock_loop
            
            result = tool._run(query="test")
            assert "Error" in result