from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from crewai import Agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings


class AgentConfig(BaseModel):
    model: str = Field(
        default_factory=lambda: settings.OPENAI_MODEL,
        description="LLM model to use"
    )
    temperature: float = Field(
        default_factory=lambda: settings.OPENAI_TEMPERATURE,
        description="Temperature for LLM responses"
    )
    max_iter: int = Field(
        default_factory=lambda: settings.CREWAI_MAX_ITERATIONS,
        description="Maximum iterations for the agent"
    )
    verbose: bool = Field(
        default_factory=lambda: settings.CREWAI_VERBOSE,
        description="Enable verbose logging"
    )
    api_key: Optional[str] = Field(
        default_factory=lambda: settings.OPENAI_API_KEY,
        description="OpenAI API key"
    )


class BaseGeoAgent(ABC):
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        config: Optional[AgentConfig] = None,
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.config = config or AgentConfig()
        self.llm = self._create_llm()
        self.agent = self._create_agent()

    def _create_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
            api_key=self.config.api_key,
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )

    def _create_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            max_iter=self.config.max_iter,
            verbose=self.config.verbose,
            tools=self.get_tools(),
        )

    @abstractmethod
    def get_tools(self) -> list:
        pass

    def get_agent(self) -> Agent:
        return self.agent


class LocationResult(BaseModel):
    latitude: float = Field(description="Latitude of the predicted location")
    longitude: float = Field(description="Longitude of the predicted location")
    confidence: float = Field(
        description="Confidence score between 0 and 1", ge=0, le=1
    )
    reasoning: str = Field(description="Reasoning for the location prediction")
    place_name: Optional[str] = Field(
        default=None, description="Human-readable place name"
    )
    country: Optional[str] = Field(default=None, description="Country name")
    region: Optional[str] = Field(default=None, description="Region or state name")
    features: Dict[str, Any] = Field(
        default_factory=dict, description="Notable features identified"
    )