# CrewAI Multi-Agent Implementation Guide

## Overview

This document provides the technical implementation details for Terra Mystica's multi-agent geolocation system using CrewAI framework with GPT-4o-mini and MCP integration.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Terra Mystica Backend                    │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Endpoints                                         │
│  ├── /api/v1/geolocation/analyze                          │
│  └── /api/v1/geolocation/results/{task_id}                │
├─────────────────────────────────────────────────────────────┤
│  CrewAI Orchestration Layer                               │
│  ├── GeolocationCrew (Main Orchestrator)                  │
│  ├── Agent Manager                                        │
│  └── Task Distribution Engine                             │
├─────────────────────────────────────────────────────────────┤
│  Specialized Agents                                       │
│  ├── Geographic Analyst Agent                             │
│  ├── Visual Analysis Agent                                │
│  ├── Environmental Agent                                  │
│  ├── Cultural Context Agent                               │
│  ├── Validation Agent                                     │
│  └── Research Agent                                       │
├─────────────────────────────────────────────────────────────┤
│  Tool & Data Integration Layer                            │
│  ├── MCP Servers                                         │
│  ├── Geographic APIs                                      │
│  ├── Computer Vision Models                               │
│  └── External Database Connectors                        │
├─────────────────────────────────────────────────────────────┤
│  Storage & Caching                                        │
│  ├── Redis (Agent State & Caching)                       │
│  ├── PostgreSQL (Results & Metadata)                     │
│  └── S3 (Image Storage)                                  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CrewAI Framework Configuration

#### Main Crew Definition
```python
# app/agents/geolocation_crew.py
from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class GeolocationCrew:
    """Main orchestrator for geolocation analysis"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def geographic_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['geographic_analyst'],
            tools=[geographic_analysis_tool, terrain_classifier],
            verbose=True
        )
    
    @agent
    def visual_analysis(self) -> Agent:
        return Agent(
            config=self.agents_config['visual_analysis'],
            tools=[landmark_detector, architecture_classifier],
            verbose=True
        )
    
    # ... other agents
    
    @task
    def analyze_geographic_features(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_geographic_features'],
            agent=self.geographic_analyst()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_llm=ChatOpenAI(model="gpt-4o-mini"),
            verbose=2
        )
```

### 2. Agent Configurations

#### Geographic Analyst Agent
```yaml
# config/agents.yaml
geographic_analyst:
  role: >
    Geographic and Terrain Analysis Expert
  goal: >
    Analyze physical geography, terrain features, and geological formations 
    to generate location hypotheses based on environmental characteristics
  backstory: >
    You are a world-renowned physical geographer with expertise in global 
    landforms, climate patterns, and geological formations. Your ability to 
    identify terrain types and geographic features from visual cues is legendary.
  max_iter: 3
  memory: true
  verbose: true
  allow_delegation: false
```

#### Visual Analysis Agent
```yaml
visual_analysis:
  role: >
    Computer Vision and Landmark Recognition Specialist
  goal: >
    Extract and classify visual features, landmarks, and architectural 
    elements to identify location-specific indicators
  backstory: >
    You are an expert in computer vision and architectural history with an 
    encyclopedic knowledge of global landmarks, building styles, and 
    infrastructure patterns.
  max_iter: 3
  memory: true
  verbose: true
  allow_delegation: false
```

### 3. Task Definitions

```yaml
# config/tasks.yaml
analyze_geographic_features:
  description: >
    Analyze the image for geographic and terrain features including:
    - Topographic characteristics (mountains, valleys, plains)
    - Geological formations and rock types
    - Vegetation patterns and biome indicators
    - Climate zone indicators
    - Water bodies and coastal features
    
    Provide 3-5 location hypotheses with confidence scores and reasoning.
  expected_output: >
    A structured analysis containing:
    1. Geographic feature classification
    2. Terrain type identification
    3. Climate zone assessment
    4. Location hypotheses with confidence scores
    5. Reasoning for each hypothesis

analyze_visual_features:
  description: >
    Perform computer vision analysis to identify:
    - Architectural styles and building types
    - Landmarks and monuments
    - Transportation infrastructure
    - Urban planning patterns
    - Cultural and religious symbols
    
    Cross-reference findings with landmark databases.
  expected_output: >
    Visual analysis report including:
    1. Identified landmarks or architectural features
    2. Building style classification
    3. Infrastructure observations
    4. Cultural symbol recognition
    5. Location suggestions based on visual evidence
```

### 4. Tool Integration Framework

#### Geographic Analysis Tools
```python
# app/tools/geographic_tools.py
from crewai_tools import tool
import geopandas as gpd
import rasterio

@tool("Terrain Classifier")
def classify_terrain(image_analysis: str) -> str:
    """
    Classify terrain type based on visual analysis description.
    
    Args:
        image_analysis: Description of terrain features from image
        
    Returns:
        Terrain classification with confidence score
    """
    # Implementation using ML models for terrain classification
    pass

@tool("Climate Zone Detector")
def detect_climate_zone(vegetation_desc: str, terrain_type: str) -> str:
    """
    Determine climate zone based on vegetation and terrain.
    
    Args:
        vegetation_desc: Description of visible vegetation
        terrain_type: Classified terrain type
        
    Returns:
        Climate zone classification
    """
    # Köppen climate classification logic
    pass
```

#### Computer Vision Tools
```python
# app/tools/vision_tools.py
from crewai_tools import tool
import cv2
import torch
from transformers import pipeline

@tool("Landmark Detector")
def detect_landmarks(image_path: str) -> str:
    """
    Detect and identify landmarks in the image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        List of detected landmarks with confidence scores
    """
    # Implementation using computer vision models
    pass

@tool("Architecture Classifier")
def classify_architecture(image_path: str) -> str:
    """
    Classify architectural style and building types.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Architectural style classification
    """
    # Implementation using architectural classification models
    pass
```

#### MCP Integration Tools
```python
# app/tools/mcp_tools.py
from crewai_tools import tool
from mcp.client import MCPClient

@tool("Geographic Database Query")
def query_geographic_db(location_hypothesis: str) -> str:
    """
    Query external geographic databases for location verification.
    
    Args:
        location_hypothesis: Proposed location to verify
        
    Returns:
        Geographic data and verification information
    """
    # MCP client implementation for geographic APIs
    pass

@tool("Weather Data Retrieval")
def get_weather_data(coordinates: str, date_estimate: str) -> str:
    """
    Retrieve historical weather data for location verification.
    
    Args:
        coordinates: Lat/lon coordinates
        date_estimate: Estimated date of image
        
    Returns:
        Weather data for verification
    """
    # MCP client for weather APIs
    pass
```

### 5. Service Layer Implementation

#### Main Geolocation Service
```python
# app/services/geolocation_service.py
import asyncio
from typing import List, Dict, Any
from crewai import Crew
from app.agents.geolocation_crew import GeolocationCrew
from app.models.geolocation import GeolocationResult
from app.core.logging import logger

class GeolocationService:
    """Main service for orchestrating geolocation analysis"""
    
    def __init__(self):
        self.crew = GeolocationCrew().crew()
        
    async def analyze_image(
        self, 
        image_path: str, 
        user_id: int,
        metadata: Dict[str, Any] = None
    ) -> GeolocationResult:
        """
        Perform multi-agent geolocation analysis on an image.
        
        Args:
            image_path: Path to the image file
            user_id: ID of the user requesting analysis
            metadata: Optional image metadata (EXIF, etc.)
            
        Returns:
            GeolocationResult with predictions and analysis
        """
        try:
            # Prepare input data for agents
            inputs = {
                'image_path': image_path,
                'metadata': metadata or {},
                'user_id': user_id
            }
            
            # Execute the crew
            result = self.crew.kickoff(inputs=inputs)
            
            # Process and structure the results
            structured_result = self._process_crew_output(result, user_id)
            
            return structured_result
            
        except Exception as e:
            logger.error(f"Geolocation analysis failed: {e}")
            raise
    
    def _process_crew_output(
        self, 
        crew_output: Any, 
        user_id: int
    ) -> GeolocationResult:
        """Process crew output into structured result"""
        # Implementation to parse and structure agent outputs
        pass
```

#### Agent Manager
```python
# app/services/agent_manager.py
from typing import Dict, List, Optional
from crewai import Agent
from app.core.config import settings

class AgentManager:
    """Manages agent lifecycle and configuration"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.load_agents()
    
    def load_agents(self):
        """Load and initialize all agents"""
        # Dynamic agent loading based on configuration
        pass
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Retrieve a specific agent by name"""
        return self.agents.get(agent_name)
    
    def get_active_agents(self, image_type: str = None) -> List[Agent]:
        """Get list of agents relevant for specific image type"""
        # Selective agent activation based on image characteristics
        pass
```

### 6. Database Models

#### Geolocation Result Model
```python
# app/models/geolocation.py
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class GeolocationResult(Base):
    __tablename__ = "geolocation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Primary prediction
    predicted_latitude = Column(Float, nullable=True)
    predicted_longitude = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Agent analysis results
    geographic_analysis = Column(JSON, nullable=True)
    visual_analysis = Column(JSON, nullable=True)
    environmental_analysis = Column(JSON, nullable=True)
    cultural_analysis = Column(JSON, nullable=True)
    validation_analysis = Column(JSON, nullable=True)
    research_analysis = Column(JSON, nullable=True)
    
    # Alternative predictions
    alternative_locations = Column(JSON, nullable=True)
    
    # Processing metadata
    processing_time = Column(Float, nullable=True)
    agent_contributions = Column(JSON, nullable=True)
    reasoning_chain = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    image = relationship("Image", back_populates="geolocation_results")
    user = relationship("User")
```

### 7. API Endpoints

#### Geolocation Analysis Endpoint
```python
# app/api/api_v1/endpoints/geolocation.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.services.geolocation_service import GeolocationService
from app.schemas.geolocation import GeolocationRequest, GeolocationResponse

router = APIRouter()
geolocation_service = GeolocationService()

@router.post("/analyze", response_model=GeolocationResponse)
async def analyze_image_location(
    request: GeolocationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Analyze image for geolocation using multi-agent system.
    """
    try:
        # Start analysis
        result = await geolocation_service.analyze_image(
            image_path=request.image_path,
            user_id=current_user.id,
            metadata=request.metadata
        )
        
        # Save to database
        db_result = GeolocationResult(**result.dict())
        db.add(db_result)
        db.commit()
        
        return GeolocationResponse.from_orm(db_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 8. Configuration Management

#### Environment Variables
```bash
# .env additions for CrewAI
OPENAI_API_KEY=your_openai_api_key_here
CREWAI_LOG_LEVEL=INFO
CREWAI_AGENT_TIMEOUT=120
CREWAI_MAX_ITERATIONS=3
CREWAI_MEMORY_ENABLED=true

# MCP Configuration
MCP_GEOGRAPHIC_SERVER_URL=http://localhost:8001
MCP_WEATHER_SERVER_URL=http://localhost:8002
MCP_LANDMARK_SERVER_URL=http://localhost:8003
```

#### CrewAI Configuration File
```yaml
# config/crewai_config.yaml
crew:
  name: "GeolocationAnalysisCrew"
  process: "hierarchical"
  memory: true
  verbose: 2
  max_execution_time: 300  # 5 minutes max
  
agents:
  max_iter: 3
  memory: true
  verbose: true
  allow_delegation: false
  
llm:
  model: "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 2000
```

## Performance Optimization

### 1. Parallel Processing
- Agents execute independently where possible
- Asynchronous task processing using asyncio
- Background task queuing with Celery

### 2. Caching Strategy
- Redis caching for frequently accessed geographic data
- Image analysis result caching
- Agent memory persistence

### 3. Resource Management
- Connection pooling for external APIs
- Rate limiting for OpenAI API calls
- Graceful degradation for failed external services

## Monitoring and Observability

### 1. Agent Performance Metrics
- Individual agent execution times
- Success rates and error patterns
- Confidence score distributions

### 2. System Health Monitoring
- API response times
- External service availability
- Resource utilization tracking

### 3. Logging Strategy
- Structured logging for agent interactions
- Request/response tracing
- Error tracking and alerting

## Testing Strategy

### 1. Unit Testing
- Individual agent testing with mock data
- Tool function validation
- Configuration loading tests

### 2. Integration Testing
- Multi-agent workflow testing
- External API integration tests
- End-to-end geolocation pipeline tests

### 3. Performance Testing
- Load testing with concurrent requests
- Agent scaling behavior
- Resource usage optimization

This implementation provides a robust, scalable foundation for the multi-agent geolocation system while maintaining clear separation of concerns and enabling future enhancements.