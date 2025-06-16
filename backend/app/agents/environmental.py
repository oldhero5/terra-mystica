from typing import List
from crewai.tools import tool

from .base import BaseGeoAgent, AgentConfig


class EnvironmentalAgent(BaseGeoAgent):
    def __init__(self, config: AgentConfig = None):
        super().__init__(
            name="Environmental Analyst",
            role="Climate and Ecosystem Analysis Expert",
            goal="Analyze environmental factors including vegetation, climate indicators, and ecosystem characteristics",
            backstory="""You are a leading environmental scientist with expertise in biogeography, 
            climatology, and ecosystem analysis. With decades of fieldwork across all continents, 
            you can identify plant species, soil types, and climate zones from visual cues. Your 
            work with conservation organizations and climate research institutes has given you 
            deep knowledge of how environmental factors vary by location. You can determine 
            latitude and climate zones from vegetation patterns, identify specific ecosystems, 
            and recognize seasonal indicators that help pinpoint geographic locations.""",
            config=config,
        )

    def get_tools(self) -> List:
        return [
            self.analyze_vegetation_tool,
            self.identify_climate_indicators_tool,
            self.assess_ecosystem_tool,
        ]

    @tool("Analyze Vegetation Patterns")
    def analyze_vegetation_tool(self, vegetation_description: str) -> str:
        """
        Analyze vegetation types, density, and patterns to determine climate zone and region.
        Args:
            vegetation_description: Description of visible vegetation
        Returns:
            Analysis of vegetation types and likely geographic regions
        """
        return f"Analyzing vegetation patterns: {vegetation_description}"

    @tool("Identify Climate Indicators")
    def identify_climate_indicators_tool(self, environmental_cues: str) -> str:
        """
        Identify climate indicators like weather patterns, seasonal cues, and atmospheric conditions.
        Args:
            environmental_cues: Description of environmental and weather indicators
        Returns:
            Climate analysis and possible geographic zones
        """
        return f"Identifying climate from indicators: {environmental_cues}"

    @tool("Assess Ecosystem Type")
    def assess_ecosystem_tool(self, ecosystem_features: str) -> str:
        """
        Assess the ecosystem type based on flora, fauna, and environmental features.
        Args:
            ecosystem_features: Description of ecosystem elements
        Returns:
            Ecosystem classification and geographic distribution
        """
        return f"Assessing ecosystem type from features: {ecosystem_features}"