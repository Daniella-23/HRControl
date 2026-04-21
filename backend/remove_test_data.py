from database import SessionLocal
from models import Candidate, Employee, Onboarding

db = SessionLocal()

# Remove test candidates
test_emails = [
    "jean.dupont@example.com",
    "marie.martin@example.com",
    "pierre.durand@example.com"
]

for email in test_emails:
    candidate = db.query(Candidate).filter(Candidate.email == email).first()
    if candidate:
        db.delete(candidate)
        print(f"Deleted test candidate: {candidate.name}")

# Remove test employees
test_employee_emails = [
    "sophie.bernard@example.com",
    "lucas.petit@example.com"
]

for email in test_employee_emails:
    employee = db.query(Employee).filter(Employee.email == email).first()
    if employee:
        # Remove associated onboarding
        onboarding = db.query(Onboarding).filter(Onboarding.employee_id == employee.id).first()
        if onboarding:
            db.delete(onboarding)
        db.delete(employee)
        print(f"Deleted test employee: {employee.name}")

db.commit()
db.close()
print("Test data removed successfully!")
