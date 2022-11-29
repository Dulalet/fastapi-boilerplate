import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URI = settings.DATABASE_URL

env = os.getenv("ENVIRONMENT")
if env == "development":
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
