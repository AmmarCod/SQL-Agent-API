import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from sqlalchemy.exc import OperationalError, SQLAlchemyError
# from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from sqlalchemy import create_engine
from langchain_community.llms import OpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI, OpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities.sql_database import SQLDatabase

# Set up OpenAI API key

import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Database credentials from .env
server = os.getenv("DATABASE_SERVER")
database = os.getenv("DATABASE_NAME")
username = os.getenv("DATABASE_USER")
password = os.getenv("DATABASE_PASSWORD")
driver = "ODBC Driver 17 for SQL Server"
driver_encoded = driver.replace(" ", "+")
db_url = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}"
    f"?driver={driver_encoded}"
    "&Encrypt=yes"
    "&TrustServerCertificate=no"
)

# Initialize the SQLDatabase object
sql_database = SQLDatabase.from_uri(
    db_url,
    include_tables=["table1", "table2"],  # Ensures this view is available
    schema="schema",
    view_support=True
)

llm = ChatOpenAI(model_name="gpt-4-1106-preview")
toolkit = SQLDatabaseToolkit(db=sql_database, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)

# Function to calculate token cost
def calculate_cost(input_tokens, output_tokens, model="gpt-4"):
    # Define token costs for different models
    token_costs = {
        "gpt-4": {"input": 0.03, "output": 0.06},  # Example costs per 1K tokens
        "gpt-3.5": {"input": 0.02, "output": 0.04}
    }
    input_cost = (input_tokens / 1000) * token_costs[model]["input"]
    output_cost = (output_tokens / 1000) * token_costs[model]["output"]
    total_cost = input_cost + output_cost
    return total_cost

# FastAPI app setup
app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str
    # cost: float

@app.post("/ask", response_model=QuestionResponse)
async def ask_database(request: QuestionRequest):
    question = request.question
    retries = 2  # Number of retries
    for attempt in range(retries + 1):  # Try up to `retries` + 1 times
        try:
            # Calculate input tokens
            input_tokens = len(question.split())
            # Execute the query using the agent
            answer = agent_executor.run(question)
            # Calculate output tokens
            output_tokens = len(answer.split())
            return QuestionResponse(answer=answer)
        except (OperationalError, SQLAlchemyError) as conn_err:
            if attempt < retries:
                time.sleep(2)  # Wait for 2 seconds before retrying
                print(f"Retrying connection... Attempt {attempt + 1} of {retries}")
            else:
                raise HTTPException(status_code=500, detail=f"Connection error after {retries + 1} attempts: {str(conn_err)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Test endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Shipergy SQL Agent API! Use the /ask endpoint to ask questions about the database."}
