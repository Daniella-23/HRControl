from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models import Employee, Onboarding
from database import get_db
from events import emit_event, handle_event

router = APIRouter()


class EmployeeCreate(BaseModel):
    name: str
    email: str
    date_embauche: str
    statut: str = "ACTIF"
    date_naissance: Optional[str] = None
    statut_familial: Optional[str] = None
    poste: Optional[str] = None
    departement: Optional[str] = None
    niveau: Optional[str] = None
    salaire_base: Optional[float] = None
    prime: Optional[float] = None
    transport: Optional[float] = None
    assurance: Optional[float] = None
    autres_avantages: Optional[str] = None
    score: int = 50


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    date_embauche: Optional[str] = None
    statut: Optional[str] = None
    date_naissance: Optional[str] = None
    statut_familial: Optional[str] = None
    poste: Optional[str] = None
    departement: Optional[str] = None
    niveau: Optional[str] = None
    salaire_base: Optional[float] = None
    prime: Optional[float] = None
    transport: Optional[float] = None
    assurance: Optional[float] = None
    autres_avantages: Optional[str] = None
    score: Optional[int] = None


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    date_embauche: str
    statut: str
    date_naissance: Optional[str]
    statut_familial: Optional[str]
    poste: Optional[str]
    departement: Optional[str]
    niveau: Optional[str]
    salaire_base: Optional[float]
    prime: Optional[float]
    transport: Optional[float]
    assurance: Optional[float]
    autres_avantages: Optional[str]
    score: Optional[int] = 50
    created_at: str

    class Config:
        from_attributes = True


@router.post("/api/employees", response_model=EmployeeResponse)
def create_employee(employee: EmployeeCreate):
    print("SCORE REÇU (CREATE):", employee.score)
    db = next(get_db())
    try:
        # Check if email already exists
        existing = db.query(Employee).filter(Employee.email == employee.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        db_employee = Employee(
            name=employee.name,
            email=employee.email,
            date_embauche=employee.date_embauche,
            statut=employee.statut,
            date_naissance=employee.date_naissance,
            statut_familial=employee.statut_familial,
            poste=employee.poste,
            departement=employee.departement,
            niveau=employee.niveau,
            salaire_base=employee.salaire_base,
            prime=employee.prime,
            transport=employee.transport,
            assurance=employee.assurance,
            autres_avantages=employee.autres_avantages,
            score=employee.score
        )
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        
        # Create onboarding record for new employee
        db_onboarding = Onboarding(employee_id=db_employee.id)
        db.add(db_onboarding)
        db.commit()
        
        # Emit event for employee creation
        event = emit_event("employee_created", f"Employé {db_employee.name} créé", db)
        handle_event(event)
        
        return EmployeeResponse(
            id=db_employee.id,
            name=db_employee.name,
            email=db_employee.email,
            date_embauche=db_employee.date_embauche,
            statut=db_employee.statut,
            date_naissance=db_employee.date_naissance,
            statut_familial=db_employee.statut_familial,
            poste=db_employee.poste,
            departement=db_employee.departement,
            niveau=db_employee.niveau,
            salaire_base=db_employee.salaire_base,
            prime=db_employee.prime,
            transport=db_employee.transport,
            assurance=db_employee.assurance,
            autres_avantages=db_employee.autres_avantages,
            score=db_employee.score,
            created_at=db_employee.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/api/employees", response_model=list[EmployeeResponse])
def get_employees():
    print("API CALL OK: GET /api/employees")
    db = next(get_db())
    try:
        employees = db.query(Employee).all()
        if not employees:
            return []
        return [
            EmployeeResponse(
                id=e.id,
                name=e.name,
                email=e.email,
                date_embauche=e.date_embauche,
                statut=e.statut,
                date_naissance=e.date_naissance,
                statut_familial=e.statut_familial,
                poste=e.poste,
                departement=e.departement,
                niveau=e.niveau,
                salaire_base=e.salaire_base,
                prime=e.prime,
                transport=e.transport,
                assurance=e.assurance,
                autres_avantages=e.autres_avantages,
                created_at=e.created_at.isoformat()
            )
            for e in employees
        ]
    finally:
        db.close()


@router.get("/api/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int):
    db = next(get_db())
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return EmployeeResponse(
            id=employee.id,
            name=employee.name,
            email=employee.email,
            date_embauche=employee.date_embauche,
            statut=employee.statut,
            date_naissance=employee.date_naissance,
            statut_familial=employee.statut_familial,
            poste=employee.poste,
            departement=employee.departement,
            niveau=employee.niveau,
            salaire_base=employee.salaire_base,
            prime=employee.prime,
            transport=employee.transport,
            assurance=employee.assurance,
            autres_avantages=employee.autres_avantages,
            created_at=employee.created_at.isoformat()
        )
    except HTTPException:
        raise
    finally:
        db.close()


@router.put("/api/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, employee: EmployeeUpdate):
    update_data = employee.model_dump(exclude_unset=True)
    print("DATA REÇUE (UPDATE):", update_data)
    print("SCORE REÇU (UPDATE):", update_data.get('score', 'Non envoyé'))
    
    db = next(get_db())
    try:
        db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Filter out NULL values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Secure score validation
        if 'score' in update_data:
            try:
                score = int(update_data['score'])
                score = max(0, min(100, score))
                update_data['score'] = score
                print("SCORE VALIDÉ:", score)
            except (ValueError, TypeError):
                update_data['score'] = 50
                print("SCORE INVALIDE, DÉFAUT 50")
        
        print("UPDATE_DATA (après filtrage NULL):", update_data)
        
        for key, value in update_data.items():
            setattr(db_employee, key, value)
        
        db.commit()
        db.refresh(db_employee)
        
        emit_event("employee_updated", f"Employé {db_employee.name} modifié", db)
        
        print("SCORE FINAL EN BASE:", db_employee.score)
        
        return EmployeeResponse(
            id=db_employee.id,
            name=db_employee.name,
            email=db_employee.email,
            date_embauche=db_employee.date_embauche,
            statut=db_employee.statut,
            date_naissance=db_employee.date_naissance,
            statut_familial=db_employee.statut_familial,
            poste=db_employee.poste,
            departement=db_employee.departement,
            niveau=db_employee.niveau,
            salaire_base=db_employee.salaire_base,
            prime=db_employee.prime,
            transport=db_employee.transport,
            assurance=db_employee.assurance,
            autres_avantages=db_employee.autres_avantages,
            score=db_employee.score,
            created_at=db_employee.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("ERREUR UPDATE:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.delete("/api/employees/{employee_id}")
def delete_employee(employee_id: int):
    db = next(get_db())
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Capture employee name before deletion
        employee_name = employee.name
        
        # Delete associated onboarding
        onboarding = db.query(Onboarding).filter(Onboarding.employee_id == employee_id).first()
        if onboarding:
            db.delete(onboarding)
        
        db.delete(employee)
        db.commit()
        
        emit_event("employee_deleted", f"Employé {employee_name} supprimé", db)
        
        return {"message": "Employee deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
