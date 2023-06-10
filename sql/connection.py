from sqlalchemy.orm import sessionmaker
from sql.definition import engine

def db_connection():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close() 