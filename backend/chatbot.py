# HR Chatbot
# Simple chatbot connected to existing data (employees, turnover, events)

from fastapi import APIRouter
from employees import get_employees
from turnover import get_turnover
from events import get_events

router = APIRouter()


@router.post("/api/chat")
def chat(message: dict):
    text = message.get("message", "").lower()

    try:
        # 🔎 TURNOVER
        if "risque" in text or "risk" in text:
            data = get_turnover()
            high = [e for e in data if e["risque"] == "high"]
            return {"reply": f"{len(high)} employés à risque élevé"}

        # 👥 EMPLOYEES
        if "combien" in text or "nombre" in text:
            employees = get_employees()
            return {"reply": f"{len(employees)} employés au total"}

        # 📜 EVENTS
        if "événement" in text or "event" in text:
            events = get_events()
            return {"reply": f"{len(events)} événements enregistrés"}

        return {"reply": "Je peux aider sur : employés, risques, événements"}

    except Exception as e:
        return {"reply": f"Erreur: {str(e)}"}
