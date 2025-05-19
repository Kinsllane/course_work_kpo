from PyQt6.QtWidgets import (
    QDialog, QTableView, QVBoxLayout, QPushButton,
    QMessageBox, QHeaderView, QInputDialog, QLineEdit,
    QFormLayout, QComboBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User, UserRole
import bcrypt


class UserTableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            user = self._data[index.row()]
            return [
                user.id,
                user.username,
                user.full_name,
                user.role.value
            ][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None


class UserEditDialog(QDialog):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Редактирование пользователя" if user else "Новый пользователь")

        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.full_name_input = QLineEdit()
        self.role_combo = QComboBox()
        self.role_combo.addItems([role.value for role in UserRole])

        if user:
            self.username_input.setText(user.username)
            self.full_name_input.setText(user.full_name)
            self.role_combo.setCurrentText(user.role.value)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addRow("Логин:", self.username_input)
        layout.addRow("Пароль:", self.password_input)
        layout.addRow("Полное имя:", self.full_name_input)
        layout.addRow("Роль:", self.role_combo)
        layout.addWidget(self.button_box)

        self.setLayout(layout)


class UserManagementDialog(QDialog):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.initUI()
        self.load_users()

    def initUI(self):
        self.setWindowTitle("Управление пользователями")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_user)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_user)

        layout.addWidget(self.table)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.delete_btn)

        self.setLayout(layout)
        # Добавляем кнопки изменения роли`
        self.btn_promote_admin = QPushButton("Сделать админом")
        self.btn_promote_tech = QPushButton("Сделать техником")
        self.btn_demote = QPushButton("Сделать клиентом")

        self.btn_promote_admin.clicked.connect(lambda: self.change_role(UserRole.ADMIN))
        self.btn_promote_tech.clicked.connect(lambda: self.change_role(UserRole.TECHNICIAN))
        self.btn_demote.clicked.connect(lambda: self.change_role(UserRole.CLIENT))

        # Добавляем в layout
        layout.addWidget(self.btn_promote_admin)
        layout.addWidget(self.btn_promote_tech)
        layout.addWidget(self.btn_demote)

    def change_role(self, new_role):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя")
            return

        user_id = self.table.model()._data[selected[0].row()].id

        if user_id == self.current_user.id:
            QMessageBox.warning(self, "Ошибка", "Нельзя изменить свою роль")
            return

        db = next(get_db())
        try:
            user = db.query(User).get(user_id)
            user.role = new_role
            db.commit()

            role_name = {
                UserRole.ADMIN: "администратор",
                UserRole.TECHNICIAN: "техник",
                UserRole.CLIENT: "клиент"
            }.get(new_role)

            QMessageBox.information(
                self,
                "Успех",
                f"Пользователь {user.username} теперь {role_name}"
            )
            self.load_users()

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")

    def load_users(self):
        db = next(get_db())
        users = db.query(User).order_by(User.id).all()

        model = UserTableModel(users, ["ID", "Логин", "Полное имя", "Роль"])
        self.table.setModel(model)
        self.table.resizeColumnsToContents()

    def add_user(self):
        dialog = UserEditDialog()
        if dialog.exec():
            try:
                username = dialog.username_input.text()
                password = dialog.password_input.text()
                full_name = dialog.full_name_input.text()
                role = dialog.role_combo.currentText()

                if not all([username, password, full_name]):
                    QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения")
                    return

                db = next(get_db())

                if db.query(User).filter(User.username == username).first():
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
                    return

                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

                new_user = User(
                    username=username,
                    password_hash=hashed_pw,
                    full_name=full_name,
                    role=UserRole(role)
                )

                db.add(new_user)
                db.commit()
                self.load_users()
                QMessageBox.information(self, "Успех", "Пользователь успешно создан")

            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка создания пользователя: {str(e)}")

    def delete_user(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления")
            return

        index = selected[0].row()
        user_id = self.table.model()._data[index].id

        if user_id == self.current_user.id:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить текущего пользователя")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить этого пользователя?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                db = next(get_db())
                user = db.query(User).get(user_id)
                db.delete(user)
                db.commit()
                self.load_users()
                QMessageBox.information(self, "Успех", "Пользователь успешно удален")
            except IntegrityError:
                db.rollback()
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    "Нельзя удалить пользователя с существующими заявками"
                )
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")