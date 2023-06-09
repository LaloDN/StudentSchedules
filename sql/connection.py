from sqlalchemy.orm import sessionmaker

def db_connection():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close() 