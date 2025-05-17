from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from gui.main_window import MainWindow
from auth import authenticate_user


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.main_window = None  # Критически важная переменная
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Авторизация')
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = QPushButton('Войти')
        login_btn.clicked.connect(self.handle_login)

        layout.addWidget(QLabel('Логин:'))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel('Пароль:'))
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def handle_login(self):
        try:
            username = self.username_input.text()
            password = self.password_input.text()

            user = authenticate_user(username, password)

            if user:
                # Правильное создание и сохранение главного окна
                self.main_window = MainWindow(user)
                self.main_window.show()

                # Скрываем окно входа вместо закрытия
                self.hide()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Неверные учетные данные')

        except Exception as e:
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Произошла критическая ошибка:\n{str(e)}'
            )
            # Для отладки можно вывести traceback
            import traceback
            print(traceback.format_exc())