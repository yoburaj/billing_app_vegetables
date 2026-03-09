from fastapi import FastAPI
from app.database.database import Base, engine
from app.models import bill, customer, inventory, user, vegetable # Import models for registration
from app.api.v1.router_v1 import router as api_v1_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="App")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)
