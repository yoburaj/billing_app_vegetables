from fastapi import FastAPI
from app.database.database import Base, engine
from app.api.v1.router_v1 import router as api_v1_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vegetable Billing App")

app.include_router(api_v1_router)
