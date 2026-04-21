from fastapi import APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import Candidate, Employee, Onboarding
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./hrcontrol.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()


class DashboardResponse(BaseModel):
    total_candidates: int
    total_employees: int
    candidates_approved: int
    avg_onboarding_percentage: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/api/dashboard", response_model=DashboardResponse)
def get_dashboard():
    print("API CALL OK: GET /api/dashboard")
    db = next(get_db())
    try:
        # Total candidates
        total_candidates = db.query(Candidate).count()
        
        # Total employees
        total_employees = db.query(Employee).count()
        
        # Candidates approved (statut = "ACCEPTÉ" or status = "APPROVED")
        candidates_approved = db.query(Candidate).filter(
            (Candidate.statut == "ACCEPTÉ") | (getattr(Candidate, 'status', 'PENDING') == "APPROVED")
        ).count()
        
        # Average onboarding percentage
        onboarding_list = db.query(Onboarding).all()
        if onboarding_list:
            total_progression = 0
            for onboarding in onboarding_list:
                completed = sum([
                    onboarding.contrat_signe,
                    onboarding.email_cree,
                    onboarding.materiel_attribue,
                    onboarding.formation_completee
                ])
                progression = (completed / 4) * 100
                total_progression += progression
            avg_onboarding_percentage = total_progression / len(onboarding_list)
        else:
            avg_onboarding_percentage = 0.0
        
        return DashboardResponse(
            total_candidates=total_candidates,
            total_employees=total_employees,
            candidates_approved=candidates_approved,
            avg_onboarding_percentage=round(avg_onboarding_percentage, 2)
        )
    except Exception as e:
        print(f"Error in dashboard: {e}")
        # Return default values on error
        return DashboardResponse(
            total_candidates=0,
            total_employees=0,
            candidates_approved=0,
            avg_onboarding_percentage=0.0
        )
    finally:
        db.close()
