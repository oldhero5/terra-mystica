from typing import List
from crewai.tools import tool

from .base import BaseGeoAgent, AgentConfig


class CulturalContextAgent(BaseGeoAgent):
    def __init__(self, config: AgentConfig = None):
        super().__init__(
            name="Cultural Context Specialist",
            role="Cultural Geography and Anthropology Expert",
            goal="Identify cultural markers, human elements, and societal indicators to determine geographic location",
            backstory="""You are a distinguished cultural geographer and anthropologist with 
            extensive field experience documenting human societies worldwide. Your expertise 
            spans linguistics, architecture, cultural practices, and societal patterns. You've 
            worked with UNESCO and various cultural preservation organizations, developing an 
            acute eye for cultural markers that indicate specific regions. You can identify 
            languages from signage, recognize cultural dress patterns, architectural traditions, 
            and subtle societal indicators that reveal geographic origins. Your knowledge 
            encompasses both historical and contemporary cultural landscapes.""",
            config=config,
        )

    def get_tools(self) -> List:
        return [
            self.analyze_signage_text_tool,
            self.identify_cultural_markers_tool,
            self.assess_human_patterns_tool,
        ]

    @tool("Analyze Signage and Text")
    def analyze_signage_text_tool(self, text_description: str) -> str:
        """
        Analyze visible text, signage, license plates, and written language indicators.
        Args:
            text_description: Description of visible text and signage
        Returns:
            Language identification and regional analysis
        """
        return f"Analyzing signage and text: {text_description}"

    @tool("Identify Cultural Markers")
    def identify_cultural_markers_tool(self, cultural_elements: str) -> str:
        """
        Identify cultural markers including dress, customs, architectural styles, and decorations.
        Args:
            cultural_elements: Description of visible cultural elements
        Returns:
            Cultural analysis and likely geographic regions
        """
        return f"Identifying cultural markers from: {cultural_elements}"

    @tool("Assess Human Activity Patterns")
    def assess_human_patterns_tool(self, activity_description: str) -> str:
        """
        Assess patterns of human activity, urban planning, and societal organization.
        Args:
            activity_description: Description of human activities and patterns
        Returns:
            Analysis of human patterns and regional indicators
        """
        return f"Assessing human activity patterns: {activity_description}"