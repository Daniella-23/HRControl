from fastapi import APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import Employee
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./hrcontrol.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()


class TurnoverResponse(BaseModel):
    nom: str
    email: str
    score: int
    risque: str
    action: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/api/turnover", response_model=list[TurnoverResponse])
def get_turnover():
    db = next(get_db())
    try:
        logger.info("Fetching employees for turnover")
        employees = db.query(Employee).all()
        logger.info(f"Found {len(employees)} employees")
        
        if not employees:
            logger.info("No employees found, returning empty list")
            return []
        
        turnover_list = []
        for employee in employees:
            try:
                # Get score from database, default to 50 if NULL
                score = employee.score if employee.score is not None else 50
                
                # Validate score
                try:
                    score = int(score)
                except (ValueError, TypeError):
                    score = 50
                
                score = max(0, min(100, score))
                
                logger.info(f"Employee {employee.name} - Score: {score}")
                
                # Calculate risk based on score
                if score < 50:
                    risque = "high"
                elif score <= 75:
                    risque = "medium"
                else:
                    risque = "low"
                
                # Calculate action based on score
                if score < 50:
                    action = "Intervention RH urgente"
                elif score <= 75:
                    action = "Suivi recommandé"
                else:
                    action = "Employé stable"
                
                turnover_list.append(
                    TurnoverResponse(
                        nom=employee.name,
                        email=employee.email,
                        score=score,
                        risque=risque,
                        action=action
                    )
                )
            except Exception as e:
                logger.error(f"Error processing employee {employee.id}: {str(e)}")
                continue
        
        logger.info(f"Returning {len(turnover_list)} turnover records")
        return turnover_list
    except Exception as e:
        logger.error(f"Error in get_turnover: {str(e)}")
        return []
    finally:
        db.close()
