from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models import Candidate, Employee, Onboarding
from database import get_db
from events import emit_event
from datetime import datetime

router = APIRouter()


class CandidateCreate(BaseModel):
    name: str
    email: str


class CandidateStatusUpdate(BaseModel):
    statut: Optional[str] = None
    status: Optional[str] = None


class CandidateEvaluation(BaseModel):
    score: int
    commentaire: str


class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    statut: str
    status: Optional[str] = None
    score: int
    commentaire: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.post("/api/candidates", response_model=CandidateResponse)
def create_candidate(candidate: CandidateCreate):
    db = next(get_db())
    try:
        # Check if email already exists
        existing = db.query(Candidate).filter(Candidate.email == candidate.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        db_candidate = Candidate(
            name=candidate.name,
            email=candidate.email,
            statut="ANALYSE",
            score=0
        )
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)
        
        # Emit event for candidate creation
        emit_event("candidate_created", f"Candidat {db_candidate.name} ajouté", db)
        
        return CandidateResponse(
            id=db_candidate.id,
            name=db_candidate.name,
            email=db_candidate.email,
            statut=db_candidate.statut,
            score=db_candidate.score,
            commentaire=db_candidate.commentaire,
            created_at=db_candidate.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/api/candidates", response_model=list[CandidateResponse])
def get_candidates():
    print("API CALL OK: GET /api/candidates")
    db = next(get_db())
    try:
        candidates = db.query(Candidate).all()
        if not candidates:
            return []
        return [
            CandidateResponse(
                id=c.id,
                name=c.name,
                email=c.email,
                statut=c.statut,
                status=getattr(c, 'status', 'PENDING'),
                score=c.score,
                commentaire=c.commentaire,
                created_at=c.created_at.isoformat()
            )
            for c in candidates
        ]
    finally:
        db.close()


@router.put("/api/candidates/{candidate_id}/status", response_model=CandidateResponse)
def update_candidate_status(candidate_id: int, status_update: CandidateStatusUpdate):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Use status if provided, otherwise use statut for backward compatibility
        new_status = status_update.status or status_update.statut
        
        # Update both statut and status for compatibility
        candidate.statut = new_status
        if hasattr(candidate, 'status'):
            candidate.status = new_status
        
        db.commit()
        db.refresh(candidate)
        
        return CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            statut=candidate.statut,
            status=getattr(candidate, 'status', candidate.statut),
            score=candidate.score,
            commentaire=candidate.commentaire,
            created_at=candidate.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.put("/api/candidates/{candidate_id}/evaluate", response_model=CandidateResponse)
def evaluate_candidate(candidate_id: int, evaluation: CandidateEvaluation):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        candidate.score = evaluation.score
        candidate.commentaire = evaluation.commentaire
        db.commit()
        db.refresh(candidate)
        
        return CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            statut=candidate.statut,
            score=candidate.score,
            commentaire=candidate.commentaire,
            created_at=candidate.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/api/candidates/{candidate_id}")
def delete_candidate(candidate_id: int):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        db.delete(candidate)
        db.commit()
        return {"message": "Candidate deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.put("/api/candidates/{candidate_id}/convert-to-employee")
def convert_candidate_to_employee(candidate_id: int):
    from models import Employee, Onboarding
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Check if employee with same email already exists
        existing_employee = db.query(Employee).filter(Employee.email == candidate.email).first()
        if existing_employee:
            # Employee already exists, just delete the candidate
            db.delete(candidate)
            db.commit()
            return {"message": "Candidate removed (employee already exists)", "employee_id": existing_employee.id}
        
        # Create employee from candidate
        employee = Employee(
            name=candidate.name,
            email=candidate.email,
            date_embauche=candidate.created_at.strftime("%Y-%m-%d"),
            statut="ACTIF",
            score=candidate.score,
            created_at=candidate.created_at
        )
        
        db.add(employee)
        db.commit()
        db.refresh(employee)
        
        # Create onboarding record for new employee
        onboarding = Onboarding(employee_id=employee.id)
        db.add(onboarding)
        db.commit()
        
        # Delete the candidate
        db.delete(candidate)
        db.commit()
        
        return {"message": "Candidate converted to employee successfully", "employee_id": employee.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.put("/api/candidates/{candidate_id}/plan-interview")
def plan_interview(candidate_id: int):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        candidate.statut = "ENTRETIEN"
        db.commit()
        
        return {"message": "Interview planned successfully", "statut": candidate.statut}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.put("/api/candidates/{candidate_id}/accept")
def accept_candidate(candidate_id: int):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        candidate.statut = "ACCEPTÉ"
        db.commit()
        
        return {"message": "Candidate accepted successfully", "statut": candidate.statut}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.put("/api/candidates/{candidate_id}/reject")
def reject_candidate(candidate_id: int):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        candidate.statut = "REJETÉ"
        db.commit()
        
        return {"message": "Candidate rejected successfully", "statut": candidate.statut}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/api/candidates/generate-evaluation")
def generate_ai_evaluation():
    import random
    
    comments = [
        "Profil intéressant avec un bon potentiel",
        "Bon candidat mais manque d'expérience terrain",
        "Très bon profil, adapté au poste",
        "Profil moyen nécessitant un encadrement",
        "Excellent candidat avec de solides compétences",
        "Candidat prometteur avec une bonne formation",
        "Profil solide mais nécessite plus d'expérience",
        "Très bon potentiel pour le poste proposé"
    ]
    
    score = random.randint(50, 95)
    commentaire = random.choice(comments)
    
    return {
        "score": score,
        "commentaire": commentaire
    }


@router.post("/api/candidates/{candidate_id}/approve")
def approve_candidate(candidate_id: int):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Update candidate status
        candidate.status = "APPROVED"
        db.commit()
        
        # Create new employee from candidate
        new_employee = Employee(
            name=candidate.name,
            email=candidate.email,
            date_embauche=datetime.now().strftime("%Y-%m-%d"),
            statut="ACTIF",
            score=candidate.score
        )
        
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        
        # Create onboarding record for new employee
        onboarding = Onboarding(employee_id=new_employee.id)
        db.add(onboarding)
        db.commit()
        
        # Emit event for candidate approval
        emit_event("candidate_approved", f"Candidat {candidate.name} approuvé et ajouté comme employé", db)
        
        return {"message": "Candidate approved and converted to employee successfully", "employee_id": new_employee.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/api/candidates/{candidate_id}/reject")
def reject_candidate_workflow(candidate_id: int):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Update candidate status
        candidate.status = "REJECTED"
        db.commit()
        
        # Emit event for candidate rejection
        emit_event("candidate_rejected", f"Candidat {candidate.name} rejeté", db)
        
        return {"message": "Candidate rejected successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
