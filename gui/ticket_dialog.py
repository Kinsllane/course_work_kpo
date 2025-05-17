from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QTextEdit, QComboBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from database import get_db
from models import Ticket, TicketStatus


class TicketDialog(QDialog):
    def __init__(self, user, ticket=None):
        super().__init__()
        self.user = user
        self.ticket = ticket
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Новая заявка" if not self.ticket else "Редактирование заявки")
        layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.description_input = QTextEdit()
        self.status_combo = QComboBox()
        self.status_combo.addItems([s.value for s in TicketStatus])
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high"])

        # Запрет изменения статуса для клиентов
        if self.user.role == 'client':
            self.status_combo.setEnabled(False)

        # Кнопки
        btn_box = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_ticket)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)

        # Добавление элементов
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
        self.title_input.setText(self.ticket.title)
        self.description_input.setText(self.ticket.description)
        self.status_combo.setCurrentText(self.ticket.status.value)
        self.priority_combo.setCurrentText(self.ticket.priority)

    def save_ticket(self):
        db = next(get_db())

        try:
            if not self.ticket:  # Новая заявка
                new_ticket = Ticket(
                    title=self.title_input.text(),
                    description=self.description_input.toPlainText(),
                    status=self.status_combo.currentText(),
                    priority=self.priority_combo.currentText(),
                    client_id=self.user.id
                )
                db.add(new_ticket)
            else:  # Редактирование
                self.ticket.title = self.title_input.text()
                self.ticket.description = self.description_input.toPlainText()
                self.ticket.status = self.status_combo.currentText()
                self.ticket.priority = self.priority_combo.currentText()

            db.commit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
            db.rollback()