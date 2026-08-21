# Backend API

This directory contains the Python Flask REST API for SecondSpin.

## Prerequisites

- Python 3.9+
- MongoDB Atlas cluster or local MongoDB instance

## Local Setup

1. **Virtual Environment**: 
   From the repository root, create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Environment Variables**:
   Copy `.env.example` to `.env` in the repository root and update the variables as needed.
   
## Running the Development Server

Start the Flask application from the repository root:

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

*(Alternatively, you can run `python -m backend.app`)*

## Testing

Run tests using pytest from the repository root:
```bash
pytest tests/
```

## Conventions
- Keep route logic in `routes.py` (or separate route files once models are introduced).
- Keep application configuration in `config.py`.
- Ensure no sensitive information is logged.
