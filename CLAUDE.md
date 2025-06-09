# CLAUDE.md - Terra Mystica

## Project Overview

Terra Mystica is a production-ready web application that uses state-of-the-art AI/ML techniques to identify the geographic location of outdoor images within 50-meter accuracy. The system leverages CrewAI multi-agent framework with GPT-4o-mini as the core reasoning engine, deploying specialized agents for comprehensive geolocation analysis with confidence scores.

## Architecture

### Frontend (Next.js + TypeScript)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS with custom Midnight Aurora theme
- **State Management**: Zustand for global state, React Query for server state
- **Maps**: Mapbox GL JS for interactive mapping
- **UI Components**: Radix UI primitives with custom theming
- **Authentication**: NextAuth.js with JWT tokens

### Backend (Python + FastAPI)
- **Framework**: FastAPI with async support
- **Package Manager**: UV for dependency management
- **ML Framework**: CrewAI multi-agent system with GPT-4o-mini
- **MCP Integration**: Model Context Protocol for external data access
- **Task Queue**: Celery with Redis for async processing
- **WebSockets**: For real-time processing updates
- **Storage**: S3 for images, OpenSearch for results indexing

### Infrastructure
- **Containerization**: Docker with docker-compose
- **Cloud**: AWS (EC2 with GPU, S3, OpenSearch Service)
- **CI/CD**: ArgoCD for GitOps deployment
- **Monitoring**: Prometheus + Grafana
- **AI Integration**: OpenAI API for GPT-4o-mini reasoning engine

## Key Features

1. **Image Upload & Processing**
   - Drag-and-drop or file selection
   - Real-time processing status via WebSocket
   - Batch upload support

2. **Geolocation Results**
   - Primary prediction with confidence score
   - Top 5 alternative locations
   - Interactive map visualization
   - Historical search results

3. **User Management**
   - Authentication with email/password
   - User dashboard with search history
   - API key management for programmatic access

4. **Admin Dashboard**
   - System metrics and accuracy tracking
   - User activity monitoring
   - Model performance analytics

5. **Export & API**
   - JSON/CSV export of results
   - RESTful API for integration
   - Webhook support for async results

## Theme Options

### 1. Midnight Aurora (Primary)
```css
--primary: hsl(280, 100%, 70%);     /* Aurora Purple */
--secondary: hsl(160, 100%, 50%);   /* Aurora Green */
--background: hsl(230, 40%, 10%);   /* Deep Blue-Black */
--foreground: hsl(210, 40%, 98%);   /* Off-White */
--accent: hsl(190, 90%, 50%);       /* Aurora Teal */
```

### 2. Northern Depths
```css
--primary: hsl(200, 100%, 50%);     /* Electric Blue */
--secondary: hsl(280, 80%, 60%);    /* Deep Purple */
--background: hsl(240, 20%, 8%);    /* Near Black */
--foreground: hsl(0, 0%, 95%);      /* Light Gray */
--accent: hsl(160, 70%, 45%);       /* Sea Green */
```

### 3. Cosmic Dusk
```css
--primary: hsl(260, 90%, 65%);      /* Nebula Purple */
--secondary: hsl(200, 80%, 55%);    /* Space Blue */
--background: hsl(250, 30%, 11%);   /* Dark Purple-Black */
--foreground: hsl(240, 20%, 96%);   /* Soft White */
--accent: hsl(340, 70%, 55%);       /* Cosmic Pink */
```

## Project Status

**Repository**: https://github.com/oldhero5/terra-mystica  
**Current Phase**: Foundation Setup  
**Last Updated**: December 2024

### Completed Issues ✅
- **Issue #1**: Docker Development Environment Setup - ARM64 support, all services configured
- **Issue #2**: Pre-commit Hooks and Code Quality Setup - Full linting, formatting, security scanning
- **Issue #4**: FastAPI Application Scaffold - Complete backend structure with UV, health checks
- **Issue #11**: Next.js Application Setup with Theme System - Midnight Aurora theme, responsive design

### Next Priority Issues 📋
- **Issue #5**: Authentication System Implementation (JWT, refresh tokens)
- **Issue #6**: Image Upload and S3 Integration (file upload, WebSocket progress)
- **Issue #8**: CrewAI Multi-Agent Geolocation System Integration (ML inference pipeline)
- **Issue #12**: Authentication UI Implementation (login/register forms)

### Development Status by Epic

#### Epic 1: Infrastructure & Development Environment (3/3 completed)
- ✅ Docker Compose with ARM64 support
- ✅ Pre-commit hooks and code quality
- ⏳ AWS Infrastructure Terraform Setup (Issue #3)

#### Epic 2: Backend Core Development (1/4 completed)
- ✅ FastAPI Application Scaffold
- ⏳ Authentication System (Issue #5)
- ⏳ Image Upload and S3 Integration (Issue #6)
- ⏳ OpenSearch Integration Layer (Issue #7)

#### Epic 3: CrewAI Multi-Agent Pipeline Implementation (0/4 completed)
- ⏳ CrewAI Multi-Agent Geolocation System Integration (Issue #8)
- ⏳ CrewAI Agent Specialization and Tool Integration (Issue #9)
- ⏳ Celery Task Queue Setup (Issue #10)
- ⏳ CrewAI Framework Setup and Agent Orchestration (Issue #25)

#### Epic 4: Frontend Development (1/6 completed)
- ✅ Next.js with Midnight Aurora Theme
- ⏳ Authentication UI (Issue #12)
- ⏳ Image Upload Interface (Issue #13)
- ⏳ Interactive Map Component (Issue #14)
- ⏳ Results Dashboard (Issue #15)
- ⏳ Admin Dashboard (Issue #16)

#### Epic 5: Integration & Testing (0/3 completed)
- ⏳ E2E Test Suite with Playwright (Issue #17)
- ⏳ API and Unit Testing (Issue #18)
- ⏳ ML Model Accuracy Benchmarking (Issue #19)

#### Epic 6: Deployment & Operations (0/3 completed)
- ⏳ ArgoCD GitOps Setup (Issue #20)
- ⏳ Monitoring and Observability Stack (Issue #21)
- ⏳ Production Readiness Checklist (Issue #22)

## Development Workflow

### Local Development
```bash
# Clone repository
git clone https://github.com/oldhero5/terra-mystica.git
cd terra-mystica

# Start services with Docker
docker-compose up -d

# Frontend development
cd frontend
npm install
npm run dev

# Backend development
cd backend
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
uvicorn main:app --reload
```

### Pre-commit Hooks
- **Linting**: ESLint (frontend), Ruff (backend)
- **Formatting**: Prettier (frontend), Black (backend)
- **Security**: Bandit (Python), npm audit
- **Type Checking**: TypeScript, mypy

### Testing Strategy
- **Unit Tests**: Jest (frontend), pytest (backend)
- **Integration Tests**: Playwright for E2E
- **Load Testing**: Locust for API endpoints
- **ML Testing**: Custom accuracy benchmarks

## API Design

### REST Endpoints
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh

POST   /api/images/upload
GET    /api/images/{id}
GET    /api/images/history

POST   /api/geolocation/predict
GET    /api/geolocation/results/{id}

GET    /api/admin/metrics
GET    /api/admin/users
```

### WebSocket Events
```
connect     -> { "type": "auth", "token": "..." }
processing  <- { "type": "status", "progress": 0.5 }
complete    <- { "type": "result", "data": {...} }
error       <- { "type": "error", "message": "..." }
```

## CrewAI Multi-Agent Pipeline

1. **Image Preprocessing**
   - EXIF data extraction
   - Resolution normalization
   - Feature extraction

2. **Agent Orchestration (CrewAI + GPT-4o-mini)**
   - Geographic Analyst Agent: Primary location reasoning
   - Visual Analysis Agent: Image feature extraction and landmarks
   - Environmental Agent: Terrain, vegetation, climate analysis
   - Cultural Context Agent: Architecture, signage, cultural markers
   - Validation Agent: Cross-reference and confidence scoring
   - Research Agent: External data gathering via MCP tools

3. **MCP Tool Integration**
   - External geographic databases
   - Weather and climate APIs
   - Satellite imagery services
   - Cultural and historical databases

4. **Result Aggregation**
   - Multi-agent consensus building
   - Confidence calibration across agents
   - Location refinement through agent collaboration

## Performance Targets

- **Accuracy**: 50m precision in urban areas
- **Latency**: <3s for single image
- **Throughput**: 100 requests/minute
- **Availability**: 99.9% uptime
- **Storage**: Efficient S3 lifecycle policies

## Security Considerations

- JWT authentication with refresh tokens
- Rate limiting per user/IP
- Input validation and sanitization
- CORS configuration
- SSL/TLS encryption
- AWS IAM roles for service access

## Future Enhancements

1. **Phase 2**: Video stream processing (RTSP)
2. **Phase 3**: Mobile applications
3. **Phase 4**: Offline capability
4. **Phase 5**: Custom model training