from PyQt6.QtWidgets import (
    QDialog, QTableView, QVBoxLayout, QPushButton,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User, UserRole


class UserManagementDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_users()

    def initUI(self):
        self.setWindowTitle("Управление пользователями")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_user)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_user)

        layout.addWidget(self.table)
        layout.addWidget(add_btn)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def load_users(self):
        db = next(get_db())
        users = db.query(User).all()

        # Создание модели таблицы (можно использовать QStandardItemModel)
        # ... реализация модели ...

    def add_user(self):
        # Реализация диалога добавления
        pass

    def delete_user(self):
        # Удаление выбранного пользователя
        pass