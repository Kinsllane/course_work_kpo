from database import engine, Base
from models import User, Ticket, Comment

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    print("Database tables created!")