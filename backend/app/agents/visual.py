from typing import List
from crewai.tools import tool

from .base import BaseGeoAgent, AgentConfig


class VisualAnalysisAgent(BaseGeoAgent):
    def __init__(self, config: AgentConfig = None):
        super().__init__(
            name="Visual Analysis Expert",
            role="Computer Vision and Scene Analysis Specialist",
            goal="Extract and analyze visual elements, objects, and patterns to identify location-specific features",
            backstory="""You are an expert in computer vision and scene analysis with a background 
            in forensic image analysis and pattern recognition. You've worked with intelligence 
            agencies and research institutions to develop advanced techniques for extracting 
            meaningful information from images. Your specialties include identifying architectural 
            styles, infrastructure patterns, vehicle types, and other visual elements that can 
            indicate specific geographic regions. You have an encyclopedic knowledge of global 
            visual patterns and can spot subtle details others might miss.""",
            config=config,
        )

    def get_tools(self) -> List:
        return [
            self.extract_visual_features_tool,
            self.analyze_architecture_tool,
            self.identify_infrastructure_tool,
        ]

    @tool("Extract Visual Features")
    def extract_visual_features_tool(self, image_data: str) -> str:
        """
        Extract detailed visual features including colors, textures, objects, and patterns.
        Args:
            image_data: Description or data about the image
        Returns:
            Comprehensive list of visual features extracted
        """
        return f"Extracting visual features from image data: {image_data}"

    @tool("Analyze Architecture Styles")
    def analyze_architecture_tool(self, buildings_description: str) -> str:
        """
        Analyze architectural styles, building materials, and construction patterns.
        Args:
            buildings_description: Description of visible buildings and structures
        Returns:
            Analysis of architectural styles and likely regions
        """
        return f"Analyzing architecture from: {buildings_description}"

    @tool("Identify Infrastructure Patterns")
    def identify_infrastructure_tool(self, infrastructure: str) -> str:
        """
        Identify infrastructure patterns like road designs, power lines, signage styles.
        Args:
            infrastructure: Description of visible infrastructure elements
        Returns:
            Analysis of infrastructure patterns and regional indicators
        """
        return f"Identifying infrastructure patterns from: {infrastructure}"