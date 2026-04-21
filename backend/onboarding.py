from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import Onboarding, Employee
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./hrcontrol.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()


class OnboardingUpdate(BaseModel):
    contrat_signe: bool
    email_cree: bool
    materiel_attribue: bool
    formation_completee: bool


class OnboardingResponse(BaseModel):
    id: int
    employee_id: int
    contrat_signe: bool
    email_cree: bool
    materiel_attribue: bool
    formation_completee: bool
    progression: float
    employee_name: str

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/api/onboarding/{employee_id}", response_model=OnboardingResponse)
def get_onboarding(employee_id: int):
    db = next(get_db())
    try:
        onboarding = db.query(Onboarding).filter(Onboarding.employee_id == employee_id).first()
        if not onboarding:
            raise HTTPException(status_code=404, detail="Onboarding not found")
        
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        employee_name = employee.name if employee else "Unknown"
        
        # Calculate progression percentage
        completed = sum([
            onboarding.contrat_signe,
            onboarding.email_cree,
            onboarding.materiel_attribue,
            onboarding.formation_completee
        ])
        progression = (completed / 4) * 100
        
        return OnboardingResponse(
            id=onboarding.id,
            employee_id=onboarding.employee_id,
            contrat_signe=onboarding.contrat_signe,
            email_cree=onboarding.email_cree,
            materiel_attribue=onboarding.materiel_attribue,
            formation_completee=onboarding.formation_completee,
            progression=progression,
            employee_name=employee_name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/api/onboarding", response_model=list[OnboardingResponse])
def get_all_onboarding():
    print("API CALL OK: GET /api/onboarding")
    db = next(get_db())
    try:
        onboarding_list = db.query(Onboarding).all()
        if not onboarding_list:
            return []
        result = []
        for onboarding in onboarding_list:
            employee = db.query(Employee).filter(Employee.id == onboarding.employee_id).first()
            employee_name = employee.name if employee else "Unknown"
            
            completed = sum([
                onboarding.contrat_signe,
                onboarding.email_cree,
                onboarding.materiel_attribue,
                onboarding.formation_completee
            ])
            progression = (completed / 4) * 100
            
            result.append(OnboardingResponse(
                id=onboarding.id,
                employee_id=onboarding.employee_id,
                contrat_signe=onboarding.contrat_signe,
                email_cree=onboarding.email_cree,
                materiel_attribue=onboarding.materiel_attribue,
                formation_completee=onboarding.formation_completee,
                progression=progression,
                employee_name=employee_name
            ))
        return result
    finally:
        db.close()


@router.put("/api/onboarding/{employee_id}", response_model=OnboardingResponse)
def update_onboarding(employee_id: int, onboarding_update: OnboardingUpdate):
    db = next(get_db())
    try:
        onboarding = db.query(Onboarding).filter(Onboarding.employee_id == employee_id).first()
        if not onboarding:
            raise HTTPException(status_code=404, detail="Onboarding not found")
        
        onboarding.contrat_signe = onboarding_update.contrat_signe
        onboarding.email_cree = onboarding_update.email_cree
        onboarding.materiel_attribue = onboarding_update.materiel_attribue
        onboarding.formation_completee = onboarding_update.formation_completee
        
        db.commit()
        db.refresh(onboarding)
        
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        employee_name = employee.name if employee else "Unknown"
        
        completed = sum([
            onboarding.contrat_signe,
            onboarding.email_cree,
            onboarding.materiel_attribue,
            onboarding.formation_completee
        ])
        progression = (completed / 4) * 100
        
        return OnboardingResponse(
            id=onboarding.id,
            employee_id=onboarding.employee_id,
            contrat_signe=onboarding.contrat_signe,
            email_cree=onboarding.email_cree,
            materiel_attribue=onboarding.materiel_attribue,
            formation_completee=onboarding.formation_completee,
            progression=progression,
            employee_name=employee_name
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
