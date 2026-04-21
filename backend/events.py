# Event System for HRControl
# Persistent event storage in database

from fastapi import APIRouter
from sqlalchemy.orm import Session
from models import Event
from database import get_db

router = APIRouter()


def emit_event(event_type: str, message: str, db: Session):
    """
    Emit an event and save it to database
    """
    event = Event(
        type=event_type,
        message=message
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    print("EVENT AJOUTÉ:", event_type, "-", message)
    return event


def handle_event(event):
    """
    Handle an event and trigger appropriate actions
    """
    if event.type == "employee_created":
        print("→ Trigger: Onboarding process started")
    
    elif event.type == "evaluation_submitted":
        print("→ Trigger: Approval process started")
    
    elif event.type == "score_updated":
        print("→ Trigger: Turnover risk recalculation")
    
    elif event.type == "onboarding_completed":
        print("→ Trigger: Employee fully onboarded")


def get_events():
    """
    Get all logged events from database (for internal use)
    """
    db = next(get_db())
    try:
        events = db.query(Event).order_by(Event.created_at.desc()).limit(50).all()
        return events
    finally:
        db.close()


@router.get("/api/events")
def get_events_api():
    """
    API endpoint to get all logged events from database
    """
    db = next(get_db())
    try:
        events = db.query(Event).order_by(Event.created_at.desc()).limit(50).all()
        return [
            {
                "type": e.type,
                "message": e.message,
                "date": e.created_at.strftime("%d/%m/%Y %H:%M")
            }
            for e in events
        ]
    finally:
        db.close()
