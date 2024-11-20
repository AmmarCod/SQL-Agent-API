# SQL Agent API

This is a FastAPI-based project that allows querying a SQL database using OpenAI's GPT-4.

## Features

- Query SQL databases using natural language.
- Integrated with OpenAI GPT-4 for intelligent query generation.
- Includes retry logic for SQLAlchemy connection errors.

## How to Run

1. Clone the repository:
   ```bash
   https://github.com/AmmarCod/SQL-Agent-API.git
   

2. Setup a virtual enviroment:
   ```bash
   python -m venv venv
   venv/scripts/activate

4. Install dependencies:
   ```bash
   pip install -r requirements.txt

5. Set environment variables in a .env file.

6. Run the application:
   ```bash
    uvicorn main:app --reload


