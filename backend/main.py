from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import candidates
import employees
import onboarding
import dashboard
import talent
import turnover
import events
import chatbot
import report

DATABASE_URL = "sqlite:///./backend/hrcontrol.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="HRControl API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(candidates.router)
app.include_router(employees.router)
app.include_router(onboarding.router)
app.include_router(dashboard.router)
app.include_router(talent.router)
app.include_router(turnover.router)
app.include_router(events.router)
app.include_router(chatbot.router)
app.include_router(report.router)


@app.on_event("startup")
def startup_event():
    # Create database tables
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "HRControl API - Gérez vos ressources humaines simplement."}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
