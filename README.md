# DevReplay API

A journaling API for developers built with FastAPI and SQLite.

## Features

- Create journal entries with title, content, and tags
- Get all entries with optional filtering by tag or keyword
- Get specific entries by ID
- Automatic summary and tip generation (simulated)

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

- `POST /entries/` - Create a new entry
- `GET /entries/` - Get all entries (with optional tag/keyword filtering)
- `GET /entries/{entry_id}` - Get a specific entry by ID

## Example Usage

Create a new entry:
```bash
curl -X POST "http://localhost:8000/entries/" -H "Content-Type: application/json" -d '{
    "title": "My First Entry",
    "content": "Today I learned about FastAPI...",
    "tags": ["python", "fastapi", "learning"]
}'
```

Get all entries:
```bash
curl "http://localhost:8000/entries/"
```

Get entries with tag filter:
```bash
curl "http://localhost:8000/entries/?tag=python"
``` 