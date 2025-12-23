# Testaurant

An automated testing platform for backend services with multi-organization RBAC support.

## Features

- 🔐 **Multi-Organization RBAC**: Secure isolation with role-based access control
- 🚀 **Multi-Protocol Testing**: REST APIs, SQL databases, and MongoDB
- 🔗 **Data Feed-Forward**: Chain test steps with dynamic data passing
- ✅ **Response Validation**: Automated validation against expected responses
- 📊 **Execution History**: Comprehensive audit logs and execution tracking
- 🌍 **Environment Management**: Support for multiple environments (QA, PREPROD, PROD)

## Architecture

- **Backend**: FastAPI (Python 3.11+) with MongoDB and SQLAlchemy
- **Frontend**: React 19 + TypeScript + Vite
- **Authentication**: Google OAuth 2.0 + JWT
- **Database**: MongoDB (application data), MySQL/PostgreSQL (test targets)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB
- Docker (optional)

### Backend Setup

```bash
cd testaurant_bff
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Frontend Setup

```bash
cd testaurant_ui
npm install
npm run dev
```

### Docker Setup

```bash
docker-compose up -d
```

## Project Structure

```
testaurant/
├── testaurant_bff/          # Backend (FastAPI)
│   ├── app/
│   │   ├── controllers/     # API endpoints
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Business logic
│   │   ├── executors/       # Test executors
│   │   ├── middleware/      # RBAC middleware
│   │   └── main.py          # FastAPI app
│   └── requirements.txt
├── testaurant_ui/           # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── contexts/        # React contexts
│   │   └── main.tsx         # App entry point
│   └── package.json
└── docker-compose.yml
```

## Documentation

See [Implementation Plan](/.gemini/antigravity/brain/7a1c4b8c-bdb2-43da-a25d-e924ab782cea/implementation_plan.md) for detailed architecture and design decisions.

## License

MIT
