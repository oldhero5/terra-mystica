from typing import List
from crewai.tools import tool

from .base import BaseGeoAgent, AgentConfig


class GeographicAnalystAgent(BaseGeoAgent):
    def __init__(self, config: AgentConfig = None):
        super().__init__(
            name="Geographic Analyst",
            role="Senior Geographic Intelligence Analyst",
            goal="Analyze geographical features, landmarks, and terrain to determine precise location with 50m accuracy",
            backstory="""You are a world-renowned geographic analyst with 20 years of experience 
            in satellite imagery analysis, cartography, and geographic intelligence. You have worked 
            with agencies like NASA and National Geographic, specializing in identifying locations 
            from visual cues. Your expertise includes recognizing mountain ranges, coastlines, 
            urban patterns, and natural landmarks from any angle. You excel at deductive reasoning 
            and can piece together multiple geographic clues to pinpoint exact locations.""",
            config=config,
        )

    def get_tools(self) -> List:
        return [
            self.analyze_terrain_tool,
            self.identify_landmarks_tool,
            self.calculate_sun_position_tool,
        ]

    @tool("Analyze Terrain Features")
    def analyze_terrain_tool(self, image_description: str) -> str:
        """
        Analyze terrain features including mountains, valleys, coastlines, and elevation patterns.
        Args:
            image_description: Description of the terrain visible in the image
        Returns:
            Analysis of terrain features and possible geographic regions
        """
        return f"Analyzing terrain features from: {image_description}"

    @tool("Identify Geographic Landmarks")
    def identify_landmarks_tool(self, features: str) -> str:
        """
        Identify specific geographic landmarks like mountains, rivers, lakes, or notable formations.
        Args:
            features: Description of visible geographic features
        Returns:
            Identified landmarks and their known locations
        """
        return f"Identifying landmarks from features: {features}"

    @tool("Calculate Sun Position")
    def calculate_sun_position_tool(self, shadows: str, time_estimate: str) -> str:
        """
        Calculate approximate latitude based on sun position and shadows.
        Args:
            shadows: Description of shadows in the image
            time_estimate: Estimated time of day
        Returns:
            Possible latitude range based on sun position
        """
        return f"Calculating sun position from shadows: {shadows} at time: {time_estimate}"