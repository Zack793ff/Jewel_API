from sqlmodel import Session, create_engine
from sqlmodel import Session



eng = r'\Users\user\Jewels_project\database.db'
sqlite_url = f'sqlite:///{eng}'

engine = create_engine(sqlite_url, echo=True)

# Dependency function to get a new session for each request
def get_session():
    with Session(engine) as session:
        yield session