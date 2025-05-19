from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QTextEdit, QComboBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from database import get_db
from models import Ticket, TicketStatus, UserRole


class TicketDialog(QDialog):
    def __init__(self, user, ticket=None):
        super().__init__()
        self.user = user
        self.ticket = ticket
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Новая заявка" if not self.ticket else "Редактирование заявки")
        layout = QVBoxLayout()

        # Поля формы
        self.title_input = QLineEdit()
        self.description_input = QTextEdit()
        self.status_combo = QComboBox()
        self.status_combo.addItems([s.value for s in TicketStatus])
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high"])

        # Техник может менять только статус и приоритет
        if self.user.role == UserRole.TECHNICIAN:
            self.title_input.setReadOnly(True)
            self.description_input.setReadOnly(True)

        # Клиент не может менять статус
        if self.user.role == UserRole.CLIENT:
            self.status_combo.setEnabled(False)

        # Кнопки
        btn_box = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_ticket)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)

        # Добавляем элементы
        layout.addWidget(QLabel("Заголовок:"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Описание:"))
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("Статус:"))
        layout.addWidget(self.status_combo)
        layout.addWidget(QLabel("Приоритет:"))
        layout.addWidget(self.priority_combo)
        layout.addLayout(btn_box)

        self.setLayout(layout)

        if self.ticket:
            self.load_data()

    def load_data(self):
        """Заполняем форму данными из существующей заявки"""
        self.title_input.setText(self.ticket.title)
        self.description_input.setPlainText(self.ticket.description)
        self.status_combo.setCurrentText(self.ticket.status.value)
        self.priority_combo.setCurrentText(self.ticket.priority or "medium")

    def save_ticket(self):
        db = next(get_db())
        try:
            if not self.ticket:  # Создание новой заявки
                new_ticket = Ticket(
                    title=self.title_input.text(),
                    description=self.description_input.toPlainText(),
                    status=TicketStatus(self.status_combo.currentText()),
                    priority=self.priority_combo.currentText(),
                    client_id=self.user.id
                )
                db.add(new_ticket)
                db.commit()
                self.accept()
                return

            # Для существующей заявки:
            # 1. Получаем свежую версию из БД
            db_ticket = db.query(Ticket).get(self.ticket.id)
            if not db_ticket:
                raise ValueError("Заявка не найдена в базе данных")

            # 2. Фиксируем изменения
            old_status = db_ticket.status

            db_ticket.title = self.title_input.text()
            db_ticket.description = self.description_input.toPlainText()
            db_ticket.status = TicketStatus(self.status_combo.currentText())
            db_ticket.priority = self.priority_combo.currentText()

            # 3. Автоназначение техника
            if (self.user.role == UserRole.TECHNICIAN and
                    db_ticket.status == TicketStatus.IN_PROGRESS and
                    not db_ticket.technician_id):
                db_ticket.technician_id = self.user.id

            db.commit()
            self.accept()

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()


    def send_status_notification(self, old_status):
        """Отправляет уведомление об изменении статуса (заглушка)"""
        print(f"Статус изменен с {old_status} на {self.ticket.status}")  # Для теста
        # Здесь будет реальная логика отправки email (пока просто логируем)