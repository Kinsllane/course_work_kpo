from database import get_db
from models import User, UserRole
import bcrypt

def authenticate_user(username: str, password: str):
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return False
    return user


def register_user(username: str, password: str, full_name: str, role: UserRole = UserRole.CLIENT):
    """Регистрация нового пользователя (только с ролью CLIENT)"""
    db = next(get_db())
    try:
        if db.query(User).filter(User.username == username).first():
            return None

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        new_user = User(
            username=username,
            password_hash=hashed_pw,
            full_name=full_name,
            role=role
        )

        db.add(new_user)
        db.commit()
        return new_user
    except Exception:
        db.rollback()
        raise
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