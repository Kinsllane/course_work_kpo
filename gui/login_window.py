from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFormLayout, QTabWidget
from gui.main_window import MainWindow
from auth import authenticate_user, register_user
from models import UserRole


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.initUI()
        self.set_style()  # Применяем стили

    def set_style(self):
        self.setStyleSheet("""
            /* Общие настройки */
            QWidget {
                font-family: 'Segoe UI', system-ui;
                background-color: #2E3440;
                color: #E5E9F0;
                font-size: 14px;
                border-radius: 10px;
            }

            /* Заголовки */
            QLabel {
                font-size: 16px;
                font-weight: 500;
                color: #D8DEE9;
                padding: 8px 0;
            }

            /* Вкладки */
            QTabWidget::pane {
                border: none;
            }

            QTabBar::tab {
                background-color: #3B4252;
                color: #E5E9F0;
                padding: 12px 24px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                margin-right: 4px;
                font-weight: 500;
                transition: all 0.3s ease;
            }

            QTabBar::tab:hover {
                background-color: #4C566A;
                color: #D8DEE9;
            }

            QTabBar::tab:selected {
                background-color: #2E3440;
                color: #FFFFFF;
                border-bottom: 2px solid #81A1C1;
            }

            /* Поля ввода */
            QLineEdit {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 10px;
                padding: 12px;
                color: #E5E9F0;
                min-width: 200px;
            }

            QLineEdit:focus {
                border-color: #81A1C1;
                background-color: #434C5E;
            }

            /* Кнопки */
            QPushButton {
                background-color: #81A1C1;
                color: #E5E9F0;
                border: 1px solid #81A1C1;
                border-radius: 10px;
                padding: 10px 20px;
                min-width: 120px;
                font-size: 16px;
                transition: all 0.3s ease;
            }

            QPushButton:hover {
                background-color: #5E81AC;
                border-color: #5E81AC;
                transform: translateY(-2px);
            }

            QPushButton:pressed {
                background-color: #434C5E;
                border-color: #434C5E;
                transform: translateY(0);
            }

            /* Сообщения об ошибках */
            QMessageBox {
                background-color: #3B4252;
                color: #E5E9F0;
                border-radius: 10px;
            }

            /* Всплывающие окна (Message Box) */
            QMessageBox QLabel {
                font-size: 16px;
                font-weight: 500;
            }
        """)

    def initUI(self):
        self.setWindowTitle('Авторизация / Регистрация')
        self.setMinimumSize(400, 300)
        tabs = QTabWidget()
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
