from fastapi import APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import Employee
from database import get_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class TalentResponse(BaseModel):
    nom: str
    email: str
    performance: str
    potentiel: str


def get_performance(score):
    """
    Calculate performance based on score
    """
    if score >= 80:
        return "high"
    elif score >= 50:
        return "medium"
    else:
        return "low"


def get_potential(niveau):
    """
    Calculate potential based on niveau (seniority level)
    """
    niveau = (niveau or "").lower()
    
    if niveau in ["senior", "lead"]:
        return "high"
    elif niveau in ["confirmé", "intermédiaire"]:
        return "medium"
    else:
        return "low"


@router.get("/api/talent", response_model=list[TalentResponse])
def get_talent():
    db = next(get_db())
    try:
        logger.info("Fetching employees for talent grid")
        employees = db.query(Employee).all()
        logger.info(f"Found {len(employees)} employees")
        
        if not employees:
            logger.info("No employees found, returning empty list")
            return []
        
        talent_list = []
        for employee in employees:
            try:
                # Use real score from database
                score = employee.score if employee.score is not None else 50
                
                # Calculate performance based on score
                performance = get_performance(score)
                
                # Calculate potential based on niveau
                potentiel = get_potential(employee.niveau)
                
                # Debug logging
                logger.info(f"{employee.name} | score={score} | perf={performance} | potentiel={potentiel}")
                
                talent_list.append(
                    TalentResponse(
                        nom=employee.name,
                        email=employee.email,
                        performance=performance,
                        potentiel=potentiel
                    )
                )
            except Exception as e:
                logger.error(f"Error processing employee {employee.id}: {str(e)}")
                continue
        
        logger.info(f"Returning {len(talent_list)} talent records")
        return talent_list
    except Exception as e:
        logger.error(f"Error in get_talent: {str(e)}")
        return []
    finally:
        db.close()
