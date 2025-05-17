from database import get_db
from models import User
import bcrypt

def authenticate_user(username: str, password: str):
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return False
    return user

def create_user(username: str, password: str, full_name: str, role: str):
    db = next(get_db())
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = User(
        username=username,
        password_hash=hashed_password,
        full_name=full_name,
        role=role
    )
    db.add(new_user)
    db.commit()
    return new_user