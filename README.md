# Terra Mystica 🌍

AI-powered geolocation service that identifies the geographic location of outdoor images within 50-meter accuracy using state-of-the-art machine learning techniques.

![Terra Mystica](https://img.shields.io/badge/Terra-Mystica-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-supported-blue?style=for-the-badge)
![ARM64](https://img.shields.io/badge/ARM64-compatible-orange?style=for-the-badge)

## ✨ Features

- **🎯 Pinpoint Accuracy**: 50-meter precision using GeoCLIP and ensemble methods
- **⚡ Lightning Fast**: Results in under 3 seconds
- **🔄 Real-time Processing**: WebSocket updates for upload progress
- **🗺️ Interactive Maps**: Mapbox GL JS visualization
- **🎨 Modern UI**: Next.js 14 with Midnight Aurora theme
- **🔐 Secure**: JWT authentication and AWS S3 storage
- **📊 Analytics**: Comprehensive admin dashboard
- **🔄 Scalable**: Docker containerized with Kubernetes support

## 🏗️ Architecture

```
Frontend (Next.js 14)     Backend (FastAPI)        Infrastructure
├── TypeScript            ├── Python 3.11         ├── Docker Compose
├── Tailwind CSS          ├── UV Package Manager  ├── AWS S3
├── Zustand               ├── PostgreSQL          ├── OpenSearch
├── React Query           ├── Redis + Celery      ├── NVIDIA GPU Support
├── Mapbox GL JS          ├── WebSockets          └── ArgoCD (Production)
└── Midnight Aurora Theme └── GeoCLIP ML Model
```

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** with Compose V2
- **Git** for version control
- **M1 Mac** or **x86_64** system support
- **8GB+ RAM** recommended
- **NVIDIA GPU** (optional, for ML acceleration)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/oldhero5/terra-mystica.git
cd terra-mystica

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # or your preferred editor
```

### 2. Start Development Environment

```bash
# For systems WITH GPU support
docker-compose up -d

# For systems WITHOUT GPU (M1 Mac, CPU-only)
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### 3. Install Pre-commit Hooks

```bash
# Install pre-commit (one-time setup)
pip install pre-commit
pre-commit install

# Or using Docker
docker run --rm -v $(pwd):/workspace python:3.11 sh -c "cd /workspace && pip install pre-commit && pre-commit install"
```

### 4. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js application |
| Backend API | http://localhost:8000 | FastAPI with docs |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Flower | http://localhost:5555 | Celery task monitoring |
| OpenSearch | http://localhost:9200 | Search and analytics |

## 🛠️ Development

### Backend Development

```bash
# Enter backend directory
cd backend

# Install dependencies (if not using Docker)
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r pyproject.toml

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Code quality checks
ruff check .
black .
mypy .
```

### Frontend Development

```bash
# Enter frontend directory
cd frontend

# Install dependencies (if not using Docker)
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint and format
npm run lint
npm run lint:fix
```

### Pre-commit Hooks

The project uses comprehensive pre-commit hooks for code quality:

```bash
# Run hooks manually
pre-commit run --all-files

# Skip hooks (emergency only)
git commit -m "fix: emergency fix" --no-verify
```

**Configured Hooks:**
- **Python**: Black, Ruff, isort, mypy, Bandit, Safety
- **JavaScript/TypeScript**: ESLint, Prettier
- **General**: YAML lint, secrets detection, conventional commits
- **Docker**: Hadolint for Dockerfile linting

## 🐳 Docker Services

### Core Services

| Service | Image | Platform | Description |
|---------|-------|----------|-------------|
| postgres | postgres:15-alpine | linux/arm64 | Primary database |
| redis | redis:7-alpine | linux/arm64 | Message broker & cache |
| opensearch | opensearchproject/opensearch:2.8.0 | linux/arm64 | Search & analytics |
| backend | Custom (Python 3.11) | linux/arm64 | FastAPI application |
| frontend | Custom (Node 18) | linux/arm64 | Next.js application |
| celery-worker | Custom (Python 3.11) | linux/arm64 | Background tasks |
| celery-beat | Custom (Python 3.11) | linux/arm64 | Task scheduler |
| flower | Custom (Python 3.11) | linux/arm64 | Task monitoring |

### Health Checks

All services include health checks for reliability:

```bash
# Check service health
docker-compose ps

# View service logs
docker-compose logs backend
docker-compose logs frontend

# Restart specific service
docker-compose restart backend
```

## 🎨 Midnight Aurora Theme

The application features a custom **Midnight Aurora** theme with cosmic aesthetics:

### Color Palette

```css
--primary: hsl(280, 100%, 70%);     /* Aurora Purple */
--secondary: hsl(160, 100%, 50%);   /* Aurora Green */
--background: hsl(230, 40%, 10%);   /* Deep Blue-Black */
--foreground: hsl(210, 40%, 98%);   /* Off-White */
--accent: hsl(190, 90%, 50%);       /* Aurora Teal */
```

### Alternative Themes

Two additional themes are available in `CLAUDE.md`:
- **Northern Depths**: Deep ocean aesthetic
- **Cosmic Dusk**: Space nebula vibes

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql://terra_user:password@postgres:5432/terra_mystica

# ML Configuration
GEOCL IP_MODEL_PATH=/app/models/geocl ip
ENABLE_GPU=true

# AWS (for production)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=terra-mystica-images

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token
```

### GPU Support

For NVIDIA GPU acceleration:

```bash
# Install NVIDIA Container Toolkit
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_health.py

# Run tests in Docker
docker-compose exec backend pytest
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# E2E tests (requires Playwright setup)
npx playwright test
```

### Load Testing

```bash
# Install Locust
pip install locust

# Run load tests
cd backend
locust -f tests/load_test.py --host=http://localhost:8000
```

## 📚 API Documentation

### Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```bash
# Health check
GET /health

# Authentication
POST /api/v1/auth/register
POST /api/v1/auth/login

# Image upload
POST /api/v1/images/upload

# Geolocation prediction
POST /api/v1/geolocation/predict
```

## 🚀 Deployment

### Development

Already configured! Just run:

```bash
docker-compose up -d
```

### Production (AWS + Kubernetes)

See deployment configuration in:
- `infrastructure/terraform/` - AWS infrastructure
- `infrastructure/k8s/` - Kubernetes manifests
- GitHub Issues #20-22 for deployment pipeline

## 🔍 Monitoring

### Development Monitoring

- **Health checks**: http://localhost:8000/health
- **Flower (Celery)**: http://localhost:5555
- **Docker logs**: `docker-compose logs -f`

### Production Monitoring

- **Prometheus + Grafana**: System metrics
- **CloudWatch**: AWS infrastructure
- **Structured logging**: JSON format with correlation IDs

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'feat: add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Create** a Pull Request

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: add new geolocation method
fix: resolve memory leak in model loading
docs: update API documentation
test: add integration tests for auth
```

## 📋 GitHub Issues

Development is tracked through 22 detailed GitHub issues organized in 6 epics:

1. **Infrastructure & Development Environment** (Issues #1-3)
2. **Backend Core Development** (Issues #4-7)
3. **ML Pipeline Implementation** (Issues #8-10)
4. **Frontend Development** (Issues #11-16)
5. **Integration & Testing** (Issues #17-19)
6. **Deployment & Operations** (Issues #20-22)

See `GH_Issues.md` for complete details.

## 🐛 Troubleshooting

### Common Issues

**Docker Build Fails on M1 Mac:**
```bash
# Ensure you're using the override file
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

**Backend Won't Start:**
```bash
# Check environment variables
docker-compose exec backend env | grep DATABASE_URL

# Check service dependencies
docker-compose ps
```

**Frontend Build Errors:**
```bash
# Clear Next.js cache
docker-compose exec frontend rm -rf .next
docker-compose restart frontend
```

**Pre-commit Hooks Failing:**
```bash
# Update hooks
pre-commit autoupdate

# Run specific hook
pre-commit run black --all-files
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **GeoCLIP** for the primary geolocation model
- **Next.js** and **FastAPI** communities
- **Mapbox** for mapping services
- **OpenSearch** for search capabilities

---

**Terra Mystica** - Discover the world through AI-powered geolocation ✨