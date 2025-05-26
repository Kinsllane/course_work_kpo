from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Ticket, TicketStatus, Comment, UserRole
import bcrypt
from datetime import datetime

# Строка подключения для PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:10052006@localhost/support_db"  # Замените на ваше имя пользователя и пароль

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание всех таблиц в базе данных
Base.metadata.create_all(bind=engine)

def create_sample_data():
    session = SessionLocal()

    try:
        # Очищаем таблицы в правильном порядке
        session.query(Comment).delete()
        session.query(Ticket).delete()
        session.query(User).delete()
        session.commit()

        # Создаем тестовых пользователей с хешированием паролей
        admin = User(
            username="admin",
            password_hash=bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
            full_name="Администратор Системы",
            role=UserRole.ADMIN
        )

        technician = User(
            username="tech1",
            password_hash=bcrypt.hashpw("tech123".encode(), bcrypt.gensalt()).decode(),
            full_name="Иван Техников",
            role=UserRole.TECHNICIAN
        )

        client1 = User(
            username="client1",
            password_hash=bcrypt.hashpw("client123".encode(), bcrypt.gensalt()).decode(),
            full_name="Петр Клиентов",
            role=UserRole.CLIENT
        )

        client2 = User(
            username="client2",
            password_hash=bcrypt.hashpw("client456".encode(), bcrypt.gensalt()).decode(),
            full_name="Анна Пользователева",
            role=UserRole.CLIENT
        )

        session.add_all([admin, technician, client1, client2])
        session.commit()

        # Создаем тестовые заявки
        ticket1 = Ticket(
            title="Не работает принтер",
            description="Принтер HP LaserJet не печатает документы",
            status=TicketStatus.OPEN,
            priority="high",
            client_id=client1.id,
            technician_id=technician.id
        )

        ticket2 = Ticket(
            title="Требуется новый монитор",
            description="Старый монитор мигает и искажает цвета",
            status=TicketStatus.IN_PROGRESS,
            priority="medium",
            client_id=client2.id
        )

        session.add_all([ticket1, ticket2])
        session.commit()

        # Добавляем комментарии
        comment1 = Comment(
            text="Пробовали перезагружать принтер?",
            ticket_id=ticket1.id,
            user_id=technician.id
        )

        comment2 = Comment(
            text="Да, перезагружали - не помогает",
            ticket_id=ticket1.id,
            user_id=client1.id
        )

        session.add_all([comment1, comment2])
        session.commit()

        print("Тестовые данные успешно добавлены!")

    except Exception as e:
        session.rollback()
        print(f"Ошибка при добавлении тестовых данных: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_sample_data()
