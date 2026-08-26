# EvidenceGraph

EvidenceGraph is an agentic NLP platform for searching multidisciplinary scientific literature and transforming research findings into an evidence graph.

The system will connect research papers, claims, supporting evidence, contradicting evidence, authors, and scientific topics in an explainable graph.

> Current status: Week 1 — project foundation and Dockerized API.

## Project Goals

- Search scientific papers across multiple disciplines.
- Collect results from trusted scientific data providers.
- Extract claims and evidence from paper metadata and abstracts.
- Identify supporting and contradicting findings.
- Build an explainable evidence graph.
- Provide an agent that plans and executes research tasks.
- Present results through an interactive web interface.
- Run locally and in the cloud using Docker.

## Technology Stack

### Backend

- Python 3.12
- FastAPI
- Pydantic Settings
- HTTPX
- Uvicorn

### Planned NLP and Agent Components

- Sentence Transformers
- Retrieval-Augmented Generation
- Agentic research workflow
- Claim and evidence extraction
- Semantic similarity
- Evidence classification

### Infrastructure

- Docker
- Docker Compose
- PostgreSQL
- Git and GitHub

### Scientific Data Providers

- OpenAlex
- Crossref
- Semantic Scholar

## Current API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/api/v1/health` | API health check |
| GET | `/docs` | Swagger documentation |
| GET | `/redoc` | ReDoc documentation |

## Running the Current Version

Create the local environment file:

```bash
copy .env.example .env
```

Build and start the API:

```bash
docker compose up --build
```

After startup, open:

```text
http://localhost:8000
http://localhost:8000/api/v1/health
http://localhost:8000/docs
```

## Project Structure

```text
EvidenceGraph/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── nlp/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
├── data/
├── deploy/
├── docs/
│   └── weeks/
├── scripts/
├── .env.example
├── .gitignore
├── compose.yaml
└── README.md
```

## Six-Week Roadmap

### Week 1 — Foundation

- Project architecture
- Environment configuration
- FastAPI foundation
- Docker setup
- Health endpoint
- Initial documentation

### Week 2 — Scientific Search

- OpenAlex integration
- Crossref integration
- Unified paper schema
- Search and paper-detail endpoints

### Week 3 — NLP Pipeline

- Text normalization
- Claim extraction
- Embedding generation
- Semantic similarity
- Evidence relation classification

### Week 4 — Agent and Evidence Graph

- Agent planning workflow
- Multi-source research
- Evidence aggregation
- Graph construction
- Explainable agent trace

### Week 5 — Web Interface and Evaluation

- React interface
- Research query workflow
- Interactive graph visualization
- Automated and manual evaluation
- Error handling

### Week 6 — Deployment

- Production Docker configuration
- Free cloud deployment
- Testing and performance checks
- Final documentation
- Portfolio and demonstration materials

## Development Status

EvidenceGraph is currently under active development. Features will be added incrementally and documented at the end of each week.