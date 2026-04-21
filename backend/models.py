from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    statut = Column(String(50), default="ANALYSE")
    status = Column(String(50), default="PENDING")
    score = Column(Integer, default=0)
    commentaire = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    date_embauche = Column(String(50), nullable=False)
    statut = Column(String(50), default="ACTIF")
    date_naissance = Column(String(50), nullable=True)
    statut_familial = Column(String(50), nullable=True)
    poste = Column(String(255), nullable=True)
    departement = Column(String(255), nullable=True)
    niveau = Column(String(50), nullable=True)
    salaire_base = Column(Float, nullable=True)
    prime = Column(Float, nullable=True)
    transport = Column(Float, nullable=True)
    assurance = Column(Float, nullable=True)
    autres_avantages = Column(Text, nullable=True)
    score = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)

    onboarding = relationship("Onboarding", back_populates="employee", uselist=False)


class Onboarding(Base):
    __tablename__ = "onboarding"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    contrat_signe = Column(Boolean, default=False)
    email_cree = Column(Boolean, default=False)
    materiel_attribue = Column(Boolean, default=False)
    formation_completee = Column(Boolean, default=False)

    employee = relationship("Employee", back_populates="onboarding")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
