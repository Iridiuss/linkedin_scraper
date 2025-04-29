import os
import time
from sqlalchemy import (create_engine, Column, String, Text, Enum, Integer,
                        BigInteger, DateTime, Numeric, func)
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv(".env")

MYSQL_URL = os.getenv("MYSQL_URL", "mysql+pymysql://root:root@mysql:3306/leads")
ENGINE = create_engine(MYSQL_URL, pool_pre_ping=True, pool_recycle=280, connect_args={"connect_timeout": 10})
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False)
Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source = Column(String(32))
    external_id = Column(String(128))
    city = Column(String(64))
    title = Column(Text)
    body = Column(Text)
    contact_name = Column(String(128))
    email = Column(String(128))
    phone = Column(String(32))
    rate = Column(Numeric(10, 2))
    posted_at = Column(DateTime)
    scraped_at = Column(DateTime, server_default=func.now())
    recency_score = Column(Integer)
    contact_score = Column(Integer)
    relevance = Column(Integer)
    total_score = Column(Integer)
    status = Column(Enum("new", "emailed", "replied", "dead", "Hot", "Warm", "Cold",
                        name="status_enum"), default="new")
    thread_id = Column(String(128))
    model_version = Column(String(64))

# Add retry logic for database initialization
def init_db():
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(ENGINE)
            print("Database tables created successfully!")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Failed to initialize database after multiple attempts")
                raise

if __name__ == "__main__":
    init_db() 