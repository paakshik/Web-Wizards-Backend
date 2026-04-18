from sqlmodel import SQLModel, create_engine, Session
from app.config import DATABASE_URL

db_url = DATABASE_URL.replace(
    "postgresql://",
    "postgresql+psycopg2://"
)

engine = create_engine(db_url, echo=False)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)