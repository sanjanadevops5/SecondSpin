# SecondSpin ♻️

**The Campus-Exclusive Marketplace for College Students**

## Purpose
SecondSpin is a dedicated, secure, and intuitive marketplace designed specifically for college students. It provides a platform to seamlessly buy, sell, and exchange pre-owned items—such as textbooks, electronics, bicycles, and hostel essentials—within their trusted college community. 

## Context
College students frequently need to buy course materials and living essentials for short-term use, and later need to sell them when they graduate or finish a semester. Generic marketplaces (like Craigslist or Facebook Marketplace) lack campus-specific trust, involve logistical hurdles for item handover, and often expose students to scams. SecondSpin solves this by restricting access to verified students, enabling safe, on-campus transactions.

## Product Architecture Snapshot
- **Backend:** Python Flask REST API
- **Database:** MongoDB Atlas
- **Frontends:** 
  - Responsive Web Application
  - Flutter Mobile Application (iOS & Android)

*(Both frontends consume the exact same Flask REST API and MongoDB database).*

## Current Status
**Phase 1: Engineering Foundation — Complete.** Repository structure, Python virtual environment, Flask REST API boilerplate, error handlers, CORS, logging, blueprint routing, and automated testing foundation are established and passing all checks. No marketplace business logic is implemented yet.

## Future Considerations
While our immediate focus is on delivering a robust MVP for a single campus, SecondSpin is architected with scalability in mind. Future features may include AI-based product recommendations, ML price predictions, QR-based transaction verification, and expansion to a multi-campus network.

---

## Local Setup and Development

### Prerequisites
- Python 3.9+
- MongoDB Atlas cluster (or local MongoDB)

### Repository Structure
- `backend/`: Python Flask REST API
- `web/`: Responsive Web Application (Planned)
- `mobile/`: Flutter Mobile Application (Planned)
- `database/`: Database scripts and schemas (Planned)
- `tests/`: Automated test suite
- `docs/`: Foundational product documentation

### Installation
1. Clone the repository.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Configure environment:
   Copy `.env.example` to `.env` and fill in your values. Do not commit `.env`.

### Running the Backend
From the root directory:

**Windows (Command Prompt):**
```cmd
set FLASK_APP=backend.app
set FLASK_ENV=development
flask run
```

**Windows (PowerShell):**
```powershell
$env:FLASK_APP="backend.app"
$env:FLASK_ENV="development"
flask run
```

**macOS / Linux:**
```bash
export FLASK_APP=backend.app
export FLASK_ENV=development
flask run
```

*(Alternatively, you can just run `python -m backend.app` on any platform).*

The health endpoint will be available at `http://127.0.0.1:5000/api/health`.

### Running Tests
Execute the independent test suite using pytest from the repository root:
```bash
pytest tests/
```

---

### Documentation
For detailed product specifications, architecture, and development plans, please refer to the `docs/` directory:
- [Product Requirements Document (PRD)](docs/PRD.md)
- [Project Scope](docs/PROJECT_SCOPE.md)
- [Features List](docs/FEATURES.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Development Plan](docs/DEVELOPMENT_PLAN.md)
