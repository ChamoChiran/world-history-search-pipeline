# App Usage

This folder documents how to run the FastAPI backend and open the static frontend.

## Prerequisites
- Python 3.10+
- Install backend dependencies:

```powershell
python -m pip install -r .\app\backend\requirements.txt
```

If you use Gemini features, set `GEMINI_API_KEY` in your environment before running.

## Run the backend
Start FastAPI (default: port `8000`):

```powershell
python -m uvicorn app.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: `http://localhost:8000/api/v1/docs`
Health check: `http://localhost:8000/health`

## Open the frontend
Open the static page directly:

```powershell
Start-Process .\app\frontend\index.html
```

Alternatively, double-click `app/frontend/index.html` in your file explorer.

