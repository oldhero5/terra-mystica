"""
Tests for CrewAI agents
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.agents.base import BaseGeoAgent, AgentConfig, LocationResult
from app.agents.geographic import GeographicAnalystAgent
from app.agents.visual import VisualAnalysisAgent
from app.agents.environmental import EnvironmentalAgent
from app.agents.cultural import CulturalContextAgent
from app.agents.validation import ValidationAgent
from app.agents.research import ResearchAgent
from app.agents.crew import TerraGeolocatorCrew, ImageAnalysisInput


class TestAgentConfig:
    """Test AgentConfig model"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = AgentConfig()
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.1
        assert config.max_iter == 5
        assert config.verbose == True
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = AgentConfig(
            model="gpt-4",
            temperature=0.5,
            max_iter=10,
            verbose=False
        )
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_iter == 10
        assert config.verbose == False


class TestLocationResult:
    """Test LocationResult model"""
    
    def test_location_result_creation(self):
        """Test creating a location result"""
        result = LocationResult(
            latitude=40.7128,
            longitude=-74.0060,
            confidence=0.85,
            reasoning="Based on landmarks",
            place_name="New York City",
            country="United States",
            region="New York",
            features={"landmarks": ["Empire State Building"]}
        )
        
        assert result.latitude == 40.7128
        assert result.longitude == -74.0060
        assert result.confidence == 0.85
        assert result.place_name == "New York City"
        assert "landmarks" in result.features
    
    def test_confidence_bounds(self):
        """Test confidence score bounds"""
        with pytest.raises(ValueError):
            LocationResult(
                latitude=0,
                longitude=0,
                confidence=1.5,  # Out of bounds
                reasoning="Test"
            )


class TestAgents:
    """Test individual agents"""
    
    @patch('app.agents.base.ChatOpenAI')
    def test_geographic_agent_creation(self, mock_llm):
        """Test GeographicAnalystAgent creation"""
        agent = GeographicAnalystAgent()
        
        assert agent.name == "Geographic Analyst"
        assert agent.role == "Senior Geographic Intelligence Analyst"
        assert len(agent.get_tools()) > 0
    
    @patch('app.agents.base.ChatOpenAI')
    def test_visual_agent_creation(self, mock_llm):
        """Test VisualAnalysisAgent creation"""
        agent = VisualAnalysisAgent()
        
        assert agent.name == "Visual Analysis Expert"
        assert "Computer Vision" in agent.role
        assert len(agent.get_tools()) > 0
    
    @patch('app.agents.base.ChatOpenAI')
    def test_environmental_agent_creation(self, mock_llm):
        """Test EnvironmentalAgent creation"""
        agent = EnvironmentalAgent()
        
        assert agent.name == "Environmental Analyst"
        assert "Climate and Ecosystem" in agent.role
        assert len(agent.get_tools()) > 0
    
    @patch('app.agents.base.ChatOpenAI')
    def test_cultural_agent_creation(self, mock_llm):
        """Test CulturalContextAgent creation"""
        agent = CulturalContextAgent()
        
        assert agent.name == "Cultural Context Specialist"
        assert "Cultural Geography" in agent.role
        assert len(agent.get_tools()) > 0
    
    @patch('app.agents.base.ChatOpenAI')
    def test_validation_agent_creation(self, mock_llm):
        """Test ValidationAgent creation"""
        agent = ValidationAgent()
        
        assert agent.name == "Validation Specialist"
        assert "Location Verification" in agent.role
        assert len(agent.get_tools()) > 0
    
    @patch('app.agents.base.ChatOpenAI')
    def test_research_agent_creation(self, mock_llm):
        """Test ResearchAgent creation"""
        agent = ResearchAgent()
        
        assert agent.name == "Research Specialist"
        assert "External Data Research" in agent.role
        assert len(agent.get_tools()) > 0
    
    @patch('app.agents.base.ChatOpenAI')
    def test_research_agent_with_mcp(self, mock_llm):
        """Test ResearchAgent with MCP client"""
        mock_mcp_client = Mock()
        agent = ResearchAgent(mcp_client=mock_mcp_client)
        
        tools = agent.get_tools()
        assert len(tools) > 3  # Should have additional MCP tools


class TestTerraGeolocatorCrew:
    """Test the main CrewAI orchestrator"""
    
    @patch('app.agents.base.ChatOpenAI')
    def test_crew_creation(self, mock_llm):
        """Test TerraGeolocatorCrew creation"""
        crew = TerraGeolocatorCrew()
        
        assert crew.geographic_agent is not None
        assert crew.visual_agent is not None
        assert crew.environmental_agent is not None
        assert crew.cultural_agent is not None
        assert crew.validation_agent is not None
        assert crew.research_agent is not None
        assert crew.crew is not None
    
    @patch('app.agents.base.ChatOpenAI')
    def test_crew_with_mcp(self, mock_llm):
        """Test crew creation with MCP client"""
        mock_mcp_client = Mock()
        crew = TerraGeolocatorCrew(mcp_client=mock_mcp_client)
        
        assert crew.mcp_client == mock_mcp_client
    
    @patch('app.agents.base.ChatOpenAI')
    def test_agent_statuses(self, mock_llm):
        """Test getting agent statuses"""
        crew = TerraGeolocatorCrew()
        statuses = crew.get_agent_statuses()
        
        assert "geographic" in statuses
        assert "visual" in statuses
        assert "environmental" in statuses
        assert "cultural" in statuses
        assert "validation" in statuses
        assert "research" in statuses
        
        for status in statuses.values():
            assert "Active" in status
    
    @pytest.mark.asyncio
    @patch('app.agents.base.ChatOpenAI')
    @patch('app.agents.crew.Crew.kickoff')
    async def test_analyze_image(self, mock_kickoff, mock_llm):
        """Test image analysis"""
        # Mock the crew kickoff to return a result
        mock_kickoff.return_value = {
            "status": "success",
            "result": "Analysis complete"
        }
        
        crew = TerraGeolocatorCrew()
        
        input_data = ImageAnalysisInput(
            image_path="/test/image.jpg",
            image_description="Test image",
            metadata={"test": "data"}
        )
        
        result = await crew.analyze_image(input_data)
        
        assert result.primary_location is not None
        assert result.primary_location.latitude is not None
        assert result.primary_location.longitude is not None
        assert result.primary_location.confidence > 0
        assert result.processing_time > 0
        assert len(result.agent_insights) > 0


@pytest.mark.asyncio
class TestGeolocationService:
    """Test the geolocation service"""
    
    @patch('app.services.geolocation.TerraGeolocatorCrew')
    async def test_service_initialization(self, mock_crew_class):
        """Test geolocation service initialization"""
        from app.services.geolocation import GeolocationService
        
        service = GeolocationService()
        assert service.crew is not None
        mock_crew_class.assert_called_once()
    
    @patch('app.services.geolocation.TerraGeolocatorCrew')
    @patch('PIL.Image.open')
    async def test_process_image(self, mock_image_open, mock_crew_class):
        """Test image processing"""
        from app.services.geolocation import GeolocationService
        
        # Mock image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.mode = "RGB"
        mock_img.format = "JPEG"
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        # Mock crew analysis
        mock_crew = Mock()
        mock_crew.analyze_image = AsyncMock()
        mock_crew.analyze_image.return_value = Mock(
            primary_location=LocationResult(
                latitude=40.7128,
                longitude=-74.0060,
                confidence=0.85,
                reasoning="Test",
                place_name="New York City",
                country="United States",
                region="New York",
                features={}
            ),
            alternative_locations=[],
            processing_time=2.5,
            agent_insights={"test": "insight"}
        )
        mock_crew_class.return_value = mock_crew
        
        service = GeolocationService()
        
        result = await service.process_image(
            image_path="/test/image.jpg",
            image_id="test-123",
            metadata={"test": "data"}
        )
        
        assert result.image_id == "test-123"
        assert result.latitude == 40.7128
        assert result.longitude == -74.0060
        assert result.confidence == 0.85
        assert result.place_name == "New York City"
    
    async def test_validation(self):
        """Test prediction validation"""
        from app.services.geolocation import GeolocationService
        from app.schemas.image import ImagePrediction
        
        service = GeolocationService()
        
        prediction = ImagePrediction(
            image_id="test-123",
            latitude=40.7128,
            longitude=-74.0060,
            confidence=0.85,
            place_name="New York City",
            country="United States",
            reasoning="Test prediction",
            processing_time=2.5
        )
        
        # Test validation with ground truth
        ground_truth = {
            "latitude": 40.7130,
            "longitude": -74.0062
        }
        
        validation = await service.validate_prediction(prediction, ground_truth)
        
        assert "distance_meters" in validation
        assert "within_50m" in validation
        assert "within_100m" in validation
        assert validation["distance_meters"] < 50  # Very close to ground truth