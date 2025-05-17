from database import get_db, engine
from models import User, Ticket, Comment, UserRole, TicketStatus
import bcrypt

def create_test_data():
    db = next(get_db())

    try:
        # Очищаем таблицы в правильном порядке
        db.query(Comment).delete()
        db.query(Ticket).delete()
        db.query(User).delete()
        db.commit()

        # Создаем тестовых пользователей
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

        db.add_all([admin, technician, client1, client2])
        db.commit()

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

        db.add_all([ticket1, ticket2])
        db.commit()

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

        db.add_all([comment1, comment2])
        db.commit()

        print("Тестовые данные успешно добавлены!")

    except Exception as e:
        db.rollback()
        print(f"Ошибка при добавлении тестовых данных: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()