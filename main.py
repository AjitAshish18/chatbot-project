from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import nlp_model

# Lifespan event to handle startup and shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check if model files exist; if not, train them automatically
    if not os.path.exists(nlp_model.MODEL_FILE) or not os.path.exists(nlp_model.VECTORIZER_FILE):
        print("Model files not found. Initiating training on startup...")
        nlp_model.train_model()
    else:
        print("Model files found. NLP Engine ready for inference.")
    yield
    # Shutdown logic (if any) goes here

# Initialize FastAPI application
app = FastAPI(title="Customer Service Chatbot API", lifespan=lifespan)

# Configure CORS Middleware (CRITICAL for allowing the vanilla JS frontend to communicate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (e.g., local files, Live Server)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Pydantic schema for validating incoming request payload
class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    """Simple health check endpoint."""
    return {"status": "API is running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Accepts user message, passes it to the NLP engine, 
    and returns the predicted response and intent details.
    """
    result = nlp_model.get_response(request.message)
    return result
