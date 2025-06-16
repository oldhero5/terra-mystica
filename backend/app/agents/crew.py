from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

from crewai import Crew, Task, Process
from pydantic import BaseModel, Field

from .base import AgentConfig, LocationResult
from .geographic import GeographicAnalystAgent
from .visual import VisualAnalysisAgent
from .environmental import EnvironmentalAgent
from .cultural import CulturalContextAgent
from .validation import ValidationAgent
from .research import ResearchAgent


class ImageAnalysisInput(BaseModel):
    image_path: str = Field(description="Path to the image file")
    image_description: Optional[str] = Field(
        default=None, description="Optional description of the image"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Optional metadata like EXIF data"
    )


class GeoLocationResult(BaseModel):
    primary_location: LocationResult = Field(
        description="Primary predicted location with highest confidence"
    )
    alternative_locations: List[LocationResult] = Field(
        default_factory=list, description="Alternative possible locations"
    )
    processing_time: float = Field(description="Time taken to process in seconds")
    agent_insights: Dict[str, str] = Field(
        default_factory=dict, description="Key insights from each agent"
    )


class TerraGeolocatorCrew:
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        mcp_client=None,
        verbose: bool = True,
    ):
        self.config = config or AgentConfig()
        self.mcp_client = mcp_client
        self.verbose = verbose
        
        # Initialize all agents
        self.geographic_agent = GeographicAnalystAgent(config=self.config)
        self.visual_agent = VisualAnalysisAgent(config=self.config)
        self.environmental_agent = EnvironmentalAgent(config=self.config)
        self.cultural_agent = CulturalContextAgent(config=self.config)
        self.validation_agent = ValidationAgent(config=self.config)
        self.research_agent = ResearchAgent(config=self.config, mcp_client=mcp_client)
        
        # Create the crew
        self.crew = self._create_crew()

    def _create_crew(self) -> Crew:
        # Define tasks for each agent
        tasks = [
            Task(
                description="""Analyze the geographic features in the image including:
                - Terrain characteristics (mountains, valleys, coastlines)
                - Notable landmarks and formations
                - Sun position and shadow analysis
                - Elevation and topographic patterns
                Provide specific latitude/longitude estimates based on your analysis.""",
                agent=self.geographic_agent.get_agent(),
                expected_output="Geographic analysis with location estimates",
            ),
            Task(
                description="""Extract and analyze visual elements including:
                - Architectural styles and building materials
                - Infrastructure patterns (roads, bridges, power lines)
                - Vehicle types and registration patterns
                - Urban planning characteristics
                Identify region-specific visual markers.""",
                agent=self.visual_agent.get_agent(),
                expected_output="Visual feature analysis with regional indicators",
            ),
            Task(
                description="""Analyze environmental factors including:
                - Vegetation types and patterns
                - Climate indicators and weather conditions
                - Ecosystem characteristics
                - Seasonal markers
                Determine climate zone and biogeographic region.""",
                agent=self.environmental_agent.get_agent(),
                expected_output="Environmental analysis with climate zone identification",
            ),
            Task(
                description="""Identify cultural and human elements including:
                - Language on signage or text
                - Cultural dress and customs visible
                - Architectural traditions
                - Human activity patterns
                Determine cultural region and specific location markers.""",
                agent=self.cultural_agent.get_agent(),
                expected_output="Cultural analysis with regional identification",
            ),
            Task(
                description="""Research external data sources to:
                - Verify identified features against databases
                - Cross-reference weather and climate data
                - Look up cultural and geographic information
                - Gather supporting evidence for location predictions
                Use all available MCP tools and external resources.""",
                agent=self.research_agent.get_agent(),
                expected_output="Research findings and external data verification",
            ),
            Task(
                description="""Validate all findings by:
                - Cross-referencing predictions from all agents
                - Identifying consensus and resolving conflicts
                - Calculating confidence scores for each prediction
                - Ensuring accuracy within 50 meters
                Provide final location with confidence score and alternatives.""",
                agent=self.validation_agent.get_agent(),
                expected_output="Validated location with confidence score and alternatives",
            ),
        ]
        
        return Crew(
            agents=[
                self.geographic_agent.get_agent(),
                self.visual_agent.get_agent(),
                self.environmental_agent.get_agent(),
                self.cultural_agent.get_agent(),
                self.research_agent.get_agent(),
                self.validation_agent.get_agent(),
            ],
            tasks=tasks,
            process=Process.sequential,  # Agents work in sequence
            verbose=self.verbose,
        )

    async def analyze_image(self, input_data: ImageAnalysisInput) -> GeoLocationResult:
        """
        Analyze an image to determine its geographic location.
        
        Args:
            input_data: Image analysis input including path and metadata
            
        Returns:
            GeoLocationResult with primary and alternative locations
        """
        start_time = datetime.now()
        
        # Prepare context for the crew
        context = {
            "image_path": input_data.image_path,
            "image_description": input_data.image_description or "No description provided",
            "metadata": input_data.metadata or {},
        }
        
        # Run the crew
        result = await asyncio.to_thread(self.crew.kickoff, inputs=context)
        
        # Process the results (this is a simplified version)
        # In production, this would parse the actual agent outputs
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create mock result for now
        geo_result = GeoLocationResult(
            primary_location=LocationResult(
                latitude=40.7128,
                longitude=-74.0060,
                confidence=0.85,
                reasoning="Based on architectural style and urban patterns",
                place_name="New York City",
                country="United States",
                region="New York",
                features={
                    "architecture": "Modern skyscrapers",
                    "infrastructure": "Grid pattern streets",
                }
            ),
            alternative_locations=[
                LocationResult(
                    latitude=41.8781,
                    longitude=-87.6298,
                    confidence=0.65,
                    reasoning="Similar urban characteristics",
                    place_name="Chicago",
                    country="United States",
                    region="Illinois",
                    features={}
                )
            ],
            processing_time=processing_time,
            agent_insights={
                "geographic": "Coastal urban area with grid pattern",
                "visual": "Modern architecture, typical of major US city",
                "environmental": "Temperate climate, deciduous vegetation",
                "cultural": "English signage, US-style infrastructure",
                "research": "Weather data confirms temperate coastal climate",
                "validation": "High consensus among agents, 85% confidence",
            }
        )
        
        return geo_result

    def get_agent_statuses(self) -> Dict[str, str]:
        """Get the status of all agents in the crew."""
        return {
            "geographic": "Active",
            "visual": "Active", 
            "environmental": "Active",
            "cultural": "Active",
            "research": "Active" if self.mcp_client else "Active (MCP unavailable)",
            "validation": "Active",
        }