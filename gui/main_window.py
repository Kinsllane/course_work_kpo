
from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QToolBar, QStatusBar, QWidget, QVBoxLayout,
    QComboBox, QHBoxLayout, QDateEdit, QLabel, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QDate
from sqlalchemy import func

from database import get_db
from models import Ticket, TicketStatus
from ticket_dialog import TicketDialog


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.initUI()
        self.load_tickets()

    def initUI(self):
        self.setWindowTitle('Система управления заявками')
        self.setGeometry(100, 100, 800, 600)

        # Таблица заявок
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Заголовок', 'Статус', 'Приоритет', 'Дата создания', 'Техник'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Панель инструментов
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        new_ticket_btn = QPushButton('Новая заявка')
        new_ticket_btn.clicked.connect(self.open_new_ticket_dialog)
        toolbar.addWidget(new_ticket_btn)

        # Центральный виджет
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Статус бар
        self.statusBar().showMessage(f'Вход выполнен как: {self.user.full_name} ({self.user.role})')
        self.setup_filters()

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
        db = next(get_db())
        query = db.query(Ticket)

        # Применяем фильтры
        if self.status_filter.currentText() != "Все":
            query = query.filter(Ticket.status == self.status_filter.currentText())

        if self.date_filter.date():
            date = self.date_filter.date().toPyDate()
            query = query.filter(func.date(Ticket.created_at) == date)

        tickets = query.all()

        self.table.setRowCount(0)
        for row, ticket in enumerate(tickets):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(ticket.id)))
            self.table.setItem(row, 1, QTableWidgetItem(ticket.title))
            self.table.setItem(row, 2, QTableWidgetItem(ticket.status.value))
            self.table.setItem(row, 3, QTableWidgetItem(ticket.priority))
            self.table.setItem(row, 4, QTableWidgetItem(ticket.created_at.strftime("%d.%m.%Y %H:%M")))
            self.table.setItem(row, 5, QTableWidgetItem(ticket.technician.full_name if ticket.technician else ""))

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

            tickets = query.order_by(Ticket.created_at.desc()).all()

            self.table.setRowCount(len(tickets))
            for row, ticket in enumerate(tickets):
                self.table.setItem(row, 0, QTableWidgetItem(str(ticket.id)))
                self.table.setItem(row, 1, QTableWidgetItem(ticket.title))
                self.table.setItem(row, 2, QTableWidgetItem(ticket.status.value))
                self.table.setItem(row, 3, QTableWidgetItem(ticket.priority or ""))
                self.table.setItem(row, 4, QTableWidgetItem(
                    ticket.created_at.strftime("%d.%m.%Y %H:%M") if ticket.created_at else ""
                ))
                technician_name = ticket.technician.full_name if ticket.technician else ""
                self.table.setItem(row, 5, QTableWidgetItem(technician_name))

            self.statusBar().showMessage(f"Найдено заявок: {len(tickets)}", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заявки: {str(e)}")
            self.statusBar().showMessage("Ошибка загрузки данных", 5000)

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