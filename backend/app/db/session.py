from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

data_dir = settings.data_dir
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///./"):
    db_path = data_dir / "leafai.db"
    db_url = f"sqlite:///{db_path}"

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
