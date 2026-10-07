from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import DB_URL

engine = create_engine(DB_URL, connect_args={"options": "-c timezone=utc"})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



if __name__ == '__main__':
    try:
        with engine.connect():
            print('Engine is connected and okay.')
    except Exception as e:
        print('Could not connect to database.')
        print(e)

    try:
        session = SessionLocal()
        session.execute(text('SELECT 1'))
        print("Session: okay")
        session.close()
    except Exception as e:
        print('Could not connect to Session.')
        print(e)