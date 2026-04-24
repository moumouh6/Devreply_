# DevReplay API

A FastAPI backend for DevReplay, a developer journal application that helps developers document their learning experiences, challenges, and insights. The API provides CRUD operations for journal entries and integrates with OpenAI for AI-powered answers to development questions.

## Features

- **Journal Entries Management**: Create, read, and manage developer journal entries
- **Tag-based Organization**: Organize entries with tags for easy filtering
- **AI Integration**: Get AI-powered answers using OpenAI's GPT models
- **SQLite Database**: Lightweight database for development and production
- **CORS Support**: Ready for frontend integration
- **Automatic Summaries**: Generate summaries and tips for entries

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **SQLite**: Database for data persistence
- **OpenAI API**: Integration for AI-powered responses
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running the application

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd Devreply_
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DATABASE_URL=sqlite:///./devreplay.db
   ```

   Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Running the Application

### Development Mode

Run the server locally:
```bash
python main.py
```

The API will be available at `http://127.0.0.1:8000`

### Using Uvicorn directly

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Entries

#### Create Entry
- **POST** `/entries/`
- **Body:**
  ```json
  {
    "title": "Learning React Hooks",
    "content": "Today I learned about useState and useEffect...",
    "tags": "react,hooks,frontend",
    "summary": "Optional custom summary",
    "tip": "Optional tip",
    "question": "Optional question for AI"
  }
  ```

#### Get All Entries
- **GET** `/entries/`
- **Response:** Array of all entries

#### Get Single Entry
- **GET** `/entries/{entry_id}`
- **Response:** Single entry object or error if not found

#### Get AI Answer for Entry
- **POST** `/entries/{entry_id}/ai/`
- **Description:** Uses the entry's content as a prompt to get AI-generated answers
- **Response:**
  ```json
  {
    "answer": "AI-generated response based on the entry content"
  }
  ```

## Database

The application uses SQLite by default (`devreplay.db`). The database schema is automatically created when the application starts.

### Database Schema

**Entries Table:**
- `id`: Primary key (Integer)
- `title`: Entry title (String)
- `content`: Main content (String)
- `summary`: Auto-generated or custom summary (String)
- `tip`: Helpful tip (String)
- `created_at`: Timestamp (DateTime)
- `tags`: Comma-separated tags (String)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key (required) | None |
| `DATABASE_URL` | Database connection URL | `sqlite:///./devreplay.db` |

## Frontend Integration

This API is designed to work with the DevReplay React frontend. The frontend makes requests to:

- `http://127.0.0.1:8000/entries/` for CRUD operations
- CORS is configured to allow requests from any origin

## Development

### Project Structure

```
Devreply_/
├── main.py           # Main FastAPI application
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── database.py       # Database configuration
├── crud.py          # CRUD operations
├── requirements.txt  # Python dependencies
├── alembic.ini      # Database migration config
├── devreplay.db     # SQLite database
└── README.md        # This file
```

### Additional Scripts

- `check_db.py`: Check database contents
- `clean_db.py`: Clean/reset database

### API Documentation

When running the server, visit `http://127.0.0.1:8000/docs` for interactive API documentation powered by Swagger UI.

## Deployment

### Production Considerations

1. **Database**: Use PostgreSQL or MySQL for production instead of SQLite
2. **Environment Variables**: Securely manage API keys
3. **HTTPS**: Enable HTTPS in production
4. **Rate Limiting**: Consider implementing rate limiting for AI endpoints
5. **Error Handling**: Add comprehensive error handling and logging

### Docker Deployment (Example)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.

## Support

If you encounter any issues or have questions:

1. Check the API documentation at `/docs`
2. Review the code comments
3. Ensure your OpenAI API key is valid and has credits
4. Check the database file exists and has proper permissions</content>
<parameter name="filePath">C:\Users\ALEM\Desktop\to do\Devreply_\README.md