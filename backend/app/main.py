from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import Base, engine
from app.models import document, line_item, validation_error
from app.controllers.document_controller import router as documents_router
from app.controllers.dashboard_controller import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(documents_router)
app.include_router(dashboard_router)

@app.get("/health")
def health():
    return {"status": "SmartDocs running"}

@app.get("/")
def root():
    return {"message": "API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://smart-docs-ashen.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)