from database import SessionLocal
from models import Candidate, Employee, Onboarding
from datetime import datetime

db = SessionLocal()

# Add test candidates
test_candidates = [
    {"name": "Jean Dupont", "email": "jean.dupont@example.com"},
    {"name": "Marie Martin", "email": "marie.martin@example.com"},
    {"name": "Pierre Durand", "email": "pierre.durand@example.com"}
]

for cand in test_candidates:
    existing = db.query(Candidate).filter(Candidate.email == cand["email"]).first()
    if not existing:
        candidate = Candidate(
            name=cand["name"],
            email=cand["email"],
            statut="EN_ATTENTE",
            status="EN_ATTENTE",
            score=50,
            commentaire="Candidat de test",
            created_at=datetime.now()
        )
        db.add(candidate)
        print(f"Added candidate: {cand['name']}")

# Add test employees
test_employees = [
    {"name": "Sophie Bernard", "email": "sophie.bernard@example.com"},
    {"name": "Lucas Petit", "email": "lucas.petit@example.com"}
]

for emp in test_employees:
    existing = db.query(Employee).filter(Employee.email == emp["email"]).first()
    if not existing:
        employee = Employee(
            name=emp["name"],
            email=emp["email"],
            date_embauche="2024-01-15",
            statut="ACTIF",
            score=75,
            created_at=datetime.now()
        )
        db.add(employee)
        db.flush()  # Flush to get the ID
        # Add onboarding for the employee
        onboarding = Onboarding(
            employee_id=employee.id,
            contrat_signe=True,
            email_cree=True,
            materiel_attribue=False,
            formation_completee=False
        )
        db.add(onboarding)
        print(f"Added employee: {emp['name']}")
    else:
        # Add onboarding if missing
        onboarding = db.query(Onboarding).filter(Onboarding.employee_id == existing.id).first()
        if not onboarding:
            onboarding = Onboarding(
                employee_id=existing.id,
                contrat_signe=True,
                email_cree=True,
                materiel_attribue=False,
                formation_completee=False
            )
            db.add(onboarding)

db.commit()
db.close()
print("Test data added successfully!")
