from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QToolBar, QStatusBar, QWidget, QVBoxLayout,
    QComboBox, QHBoxLayout, QDateEdit, QLabel, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation
from sqlalchemy import func

from database import get_db
from models import Ticket, TicketStatus, UserRole
from ticket_dialog import TicketDialog

from gui.user_management import UserManagementDialog

from report_dialog import ReportDialog
from report_generator import ReportGenerator


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.initUI()
        self.load_tickets()
        self.init_admin_tools()

    def init_admin_tools(self):
        if self.user.role == UserRole.ADMIN:
            admin_toolbar = QToolBar("Администрирование")
            self.addToolBar(Qt.ToolBarArea.RightToolBarArea, admin_toolbar)

            manage_users_btn = QPushButton("Управление пользователями")
            manage_users_btn.setIcon(QIcon('icons/users.png'))
            manage_users_btn.clicked.connect(self.open_user_management)
            admin_toolbar.addWidget(manage_users_btn)

            report_btn = QPushButton("Отчеты")
            report_btn.setIcon(QIcon('icons/report.png'))
            report_btn.clicked.connect(self.open_report_dialog)
            admin_toolbar.addWidget(report_btn)

    def init_technician_tools(self):
        if self.user.role == UserRole.TECHNICIAN:
            toolbar = self.addToolBar("Отчеты")
            report_btn = QPushButton("Мои отчеты")
            report_btn.setIcon(QIcon('icons/report.png'))
            report_btn.clicked.connect(self.open_report_dialog)
            toolbar.addWidget(report_btn)

    def open_report_dialog(self):
        dialog = ReportDialog(self.user)
        if dialog.exec():
            start_date = dialog.start_date.date().toPyDate()
            end_date = dialog.end_date.date().toPyDate()
            report_format = dialog.format_combo.currentText()

            generator = ReportGenerator(self.user, start_date, end_date)
            tickets = generator.get_tickets()

            if not tickets:
                QMessageBox.warning(self, "Ошибка", "Нет данных для выбранного периода")
                return

            if report_format == "PDF":
                generator.generate_pdf(tickets)
            elif report_format == "Excel":
                generator.generate_excel(tickets)
            else:
                generator.generate_csv(tickets)

            QMessageBox.information(
                self,
                "Успех",
                f"Отчет сохранен как: {generator.filename}"
            )

    def open_user_management(self):
        dialog = UserManagementDialog(self.user)
        dialog.exec()

    def open_edit_dialog(self):
        # Получаем выбранную строку в таблице
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите заявку для редактирования")
            return

        try:
            # Получаем ID заявки из первого столбца выбранной строки
            ticket_id = int(self.table.item(selected[0].row(), 0).text())

            # Создаем новую сессию БД
            db = next(get_db())

            # Получаем заявку из БД
            ticket = db.query(Ticket).get(ticket_id)
            if not ticket:
                QMessageBox.warning(self, "Ошибка", "Заявка не найдена")
                db.close()
                return

            # Проверяем, является ли текущий пользователь владельцем заявки (для CLIENT)
            if self.user.role == UserRole.CLIENT and ticket.client_id != self.user.id:
                QMessageBox.warning(self, "Ошибка", "Вы не можете редактировать чужую заявку!")
                db.close()
                return

            # Создаем копию данных для редактирования
            ticket_data = {
                'id': ticket.id,
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'client_id': ticket.client_id,
                'technician_id': ticket.technician_id,
                'created_at': ticket.created_at,
                'updated_at': ticket.updated_at
            }
            db.expunge(ticket)  # Отвязываем оригинальный объект от сессии
            db.close()

            # Создаем новый объект для редактирования
            ticket_to_edit = Ticket(**ticket_data)

            # Открываем диалог редактирования
            dialog = TicketDialog(self.user, ticket_to_edit)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_tickets()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть заявку для редактирования:\n{str(e)}")
            import traceback
            print(traceback.format_exc())
            if 'db' in locals():  # Закрываем сессию, если она есть
                db.close()

    def set_style(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #2e3436;  /* Темный фон */
                color: #dcdfe1;  /* Светлый серый текст */
            }

            QLabel {
                font-size: 14px;
                color: #dcdfe1;  /* Светлый серый текст для меток */
            }

            QLineEdit, QTextEdit, QComboBox {
                background-color: #3c4346;  /* Темный фон для полей ввода */
                border: 1px solid #666666;  /* Темно-серая граница */
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                color: #dcdfe1;  /* Светлый текст */
            }

            QLineEdit:focus, QTextEdit:focus {
                border-color: #3faffa;  /* Голубой цвет при фокусе */
            }

            QPushButton {
                background-color: #444c56;  /* Темно-серый цвет кнопки */
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }

            QPushButton:hover {
                background-color: #556273;  /* Светлее при наведении */
            }

            QPushButton:disabled {
                background-color: #7d7f7f;  /* Серый для неактивных кнопок */
                cursor: not-allowed;
            }

            QTableWidget {
                background-color: #333b3f;  /* Темный фон для таблицы */
                border: 1px solid #555555;  /* Темная граница */
                border-radius: 5px;
                font-size: 14px;
                color: #dcdfe1;  /* Светлый текст в таблице */
            }

            QTableWidgetItem {
                padding: 8px;
                border-bottom: 1px solid #444444;  /* Тонкая темная линия между строками */
            }

            QTableWidget::item:selected {
                background-color: #556273;  /* Светло-серый для выделенной строки */
            }

            QStatusBar {
                background-color: #2c3338;  /* Темный фон для статус бара */
                font-size: 14px;
                color: #dcdfe1;  /* Светлый текст */
            }

            QToolBar {
                background-color: #444c56;  /* Темная панель инструментов */
                border-radius: 5px;
                font-size: 16px;
            }

            QToolBar QToolButton {
                background-color: #444c56;
                border-radius: 5px;
                color: white;
            }

            QToolBar QToolButton:hover {
                background-color: #556273;
            }

            QTabWidget::pane {
                border: none;
            }

            QTabWidget::tab-bar {
                alignment: center;
            }

            QTabBar::tab {
                background-color: #444c56;  /* Темная вкладка */
                color: white;
                padding: 10px;
                border-radius: 5px;
            }

            QTabBar::tab:hover {
                background-color: #556273;  /* Светлее при наведении */
            }

            QTabBar::tab:selected {
                background-color: #556273;  /* Выделенная вкладка */
            }
        """)

    def add_animation(self):
        # Применяем анимацию к кнопке для создания новой заявки
        animation = QPropertyAnimation(self.new_ticket_btn, b"geometry")
        animation.setDuration(300)
        animation.setStartValue(self.new_ticket_btn.geometry())
        animation.setEndValue(self.new_ticket_btn.geometry().adjusted(0, 0, 0, 10))
        animation.start()



    def initUI(self):
        self.setWindowTitle('Система управления заявками')
        self.setGeometry(100, 100, 800, 600)

        # Таблица заявок
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([ 'ID', 'Заголовок', 'Статус', 'Приоритет', 'Дата создания', 'Техник' ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Панель инструментов
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Кнопка "Редактировать"
        edit_btn = QPushButton('Редактировать')
        edit_btn.setIcon(QIcon('icons/draw.png'))
        edit_btn.clicked.connect(self.open_edit_dialog)
        toolbar.addWidget(edit_btn)

        # Кнопка "Новая заявка"
        self.new_ticket_btn = QPushButton('Новая заявка')
        self.new_ticket_btn.setIcon(QIcon('icons/plus.png'))
        self.new_ticket_btn.clicked.connect(self.open_new_ticket_dialog)
        toolbar.addWidget(self.new_ticket_btn)

        if self.user.role == UserRole.TECHNICIAN:
            self.assign_btn = QPushButton("Взять заявку")
            self.assign_btn.setIcon(QIcon('icons/assign.png'))
            self.assign_btn.clicked.connect(self.assign_ticket)
            toolbar.addWidget(self.assign_btn)

        # Центральный виджет
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Статус бар
        self.statusBar().showMessage(f'Вход выполнен как: {self.user.full_name} ({self.user.role})')
        self.setup_filters()
        self.set_style()
        self.add_animation()

    def assign_ticket(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return

        ticket_id = int(self.table.item(selected[0].row(), 0).text())
        db = next(get_db())
        ticket = db.query(Ticket).get(ticket_id)

        if ticket.technician_id:
            QMessageBox.warning(self, "Ошибка", "Заявка уже назначена")
            return

        ticket.technician_id = self.user.id
        ticket.status = TicketStatus.IN_PROGRESS
        db.commit()

        self.load_tickets()
        QMessageBox.information(self, "Успех", "Вы взяли заявку!")

    def setup_filters(self):
        filter_widget = QWidget()
        layout = QHBoxLayout()

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все"] + [s.value for s in TicketStatus])
        self.status_filter.currentTextChanged.connect(self.load_tickets)

        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.dateChanged.connect(self.load_tickets)

        layout.addWidget(QLabel("Статус:"))
        layout.addWidget(self.status_filter)
        layout.addWidget(QLabel("Дата создания:"))
        layout.addWidget(self.date_filter)

        filter_widget.setLayout(layout)
        self.table.parentWidget().layout().insertWidget(0, filter_widget)

    def load_tickets(self):
        try:
            db = next(get_db())
            query = db.query(Ticket)

            # Применяем фильтры
            if self.status_filter.currentText() != "Все":
                status = TicketStatus(self.status_filter.currentText())
                query = query.filter(Ticket.status == status)

            if self.date_filter.date():
                date = self.date_filter.date().toPyDate()
                query = query.filter(func.date(Ticket.created_at) == date)

            # Для клиентов показываем только их заявки
            if self.user.role == UserRole.CLIENT:
                query = query.filter(Ticket.client_id == self.user.id)

            tickets = query.order_by(Ticket.created_at.desc()).all()

            # Заполняем таблицу
            self.table.setRowCount(len(tickets))
            for row, ticket in enumerate(tickets):
                # Основные данные
                self.table.setItem(row, 0, QTableWidgetItem(str(ticket.id)))
                self.table.setItem(row, 1, QTableWidgetItem(ticket.title))

                # Статус с цветовым выделением
                status_item = QTableWidgetItem(ticket.status.value)
                if ticket.status == TicketStatus.OPEN:
                    status_item.setBackground(QColor(255, 230, 230))  # Красный
                elif ticket.status == TicketStatus.IN_PROGRESS:
                    status_item.setBackground(QColor(255, 255, 200))  # Желтый
                elif ticket.status == TicketStatus.CLOSED:
                    status_item.setBackground(QColor(230, 255, 230))  # Зеленый
                self.table.setItem(row, 2, status_item)

                # Приоритет
                priority_item = QTableWidgetItem(ticket.priority or "")
                self.table.setItem(row, 3, priority_item)

                # Дата создания
                created_at = ticket.created_at.strftime("%d.%m.%Y %H:%M") if ticket.created_at else ""
                self.table.setItem(row, 4, QTableWidgetItem(created_at))

                # Техник с выделением "своих" заявок
                technician_name = ticket.technician.full_name if ticket.technician else "Не назначен"
                tech_item = QTableWidgetItem(technician_name)
                if ticket.technician_id == self.user.id:
                    tech_item.setBackground(QColor(220, 240, 255))  # Голубой
                self.table.setItem(row, 5, tech_item)

            # Автоматическое растягивание столбцов
            self.table.resizeColumnsToContents()

            # Статус бар
            ticket_count = len(tickets)
            message = f"Найдено заявок: {ticket_count}"
            if self.user.role == UserRole.CLIENT:
                message += f" (Ваших: {ticket_count})"
            self.statusBar().showMessage(message, 3000)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заявки: {str(e)}")
            self.statusBar().showMessage("Ошибка загрузки данных", 5000)
        finally:
            db.close()

    def open_new_ticket_dialog(self):
        dialog = TicketDialog(self.user)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.load_tickets()  # Обновляем список заявок
                self.statusBar().showMessage("Заявка успешно создана!", 3000)

                # Прокручиваем таблицу к новой заявке
                if self.table.rowCount() > 0:
                    self.table.scrollToBottom()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось обновить данные: {str(e)}")
