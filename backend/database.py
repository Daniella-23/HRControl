# Database configuration
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./backend/hrcontrol.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def migrate_database():
    """
    Run automatic migrations to add missing columns
    """
    db = SessionLocal()
    try:
        # Check if status column exists in candidates table
        result = db.execute(text("PRAGMA table_info(candidates)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'status' not in columns:
            print("Adding status column to candidates table...")
            db.execute(text("ALTER TABLE candidates ADD COLUMN status VARCHAR DEFAULT 'PENDING'"))
            db.commit()
            print("Status column added successfully")
    except Exception as e:
        print(f"Migration error: {e}")
        db.rollback()
    finally:
        db.close()


# Run migrations on import
migrate_database()


def get_db():
    """
    Get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
