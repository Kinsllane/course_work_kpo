from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QFormLayout, QTabWidget
)
from gui.main_window import MainWindow
from auth import authenticate_user, register_user
from models import UserRole


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Авторизация / Регистрация')
        self.setGeometry(300, 300, 400, 300)

        # Создаем вкладки
        tabs = QTabWidget()

        # Вкладка входа
        login_tab = QWidget()
        login_layout = QVBoxLayout()

        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = QPushButton('Войти')
        login_btn.clicked.connect(self.handle_login)

        login_layout.addWidget(QLabel('Логин:'))
        login_layout.addWidget(self.login_username)
        login_layout.addWidget(QLabel('Пароль:'))
        login_layout.addWidget(self.login_password)
        login_layout.addWidget(login_btn)
        login_tab.setLayout(login_layout)

        # Вкладка регистрации
        register_tab = QWidget()
        register_layout = QFormLayout()

        self.reg_username = QLineEdit()
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_fullname = QLineEdit()

        register_btn = QPushButton('Зарегистрироваться')
        register_btn.clicked.connect(self.handle_register)

        register_layout.addRow('Логин:', self.reg_username)
        register_layout.addRow('Пароль:', self.reg_password)
        register_layout.addRow('Полное имя:', self.reg_fullname)
        register_layout.addRow(register_btn)
        register_tab.setLayout(register_layout)

        # Добавляем вкладки
        tabs.addTab(login_tab, "Вход")
        tabs.addTab(register_tab, "Регистрация")

        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

    def handle_login(self):
        try:
            username = self.login_username.text()
            password = self.login_password.text()

            user = authenticate_user(username, password)

            if user:
                self.main_window = MainWindow(user)
                self.main_window.show()
                self.hide()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Неверные учетные данные')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка авторизации: {str(e)}')
            import traceback
            print(traceback.format_exc())

    def handle_register(self):
        try:
            username = self.reg_username.text()
            password = self.reg_password.text()
            fullname = self.reg_fullname.text()

            if not all([username, password, fullname]):
                QMessageBox.warning(self, 'Ошибка', 'Все поля обязательны')
                return

            user = register_user(username, password, fullname, UserRole.CLIENT)
            if user:
                QMessageBox.information(self, 'Успех', 'Регистрация завершена')
                self.login_username.setText(username)
                # Переключаем на вкладку входа
                for i in range(self.layout().count()):
                    if isinstance(self.layout().itemAt(i).widget(), QTabWidget):
                        self.layout().itemAt(i).widget().setCurrentIndex(0)
                        break
            else:
                QMessageBox.warning(self, 'Ошибка', 'Пользователь уже существует')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка регистрации: {str(e)}')