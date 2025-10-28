from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine("postgresql://user:password@wegwijs-postgresql:5432/postgres")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency
def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()
