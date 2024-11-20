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
   
2. Setup a virtual enviroment
python -m venv venv
source venv/bin/activate

3.Install dependencies:

pip install -r requirements.txt
Set environment variables in a .env file.

Run the application:

uvicorn main:app --reload
