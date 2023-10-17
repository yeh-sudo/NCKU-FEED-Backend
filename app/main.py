"""main module"""

from fastapi import FastAPI
from dotenv import load_dotenv
from .routers import auth

load_dotenv()

app = FastAPI()
app.include_router(auth.router)
