# report_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QDateEdit, QComboBox, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import QDate


class ReportDialog(QDialog):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Генерация отчета")
        layout = QVBoxLayout()

        # Период
        period_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())

        period_layout.addWidget(QLabel("С:"))
        period_layout.addWidget(self.start_date)
        period_layout.addWidget(QLabel("По:"))
        period_layout.addWidget(self.end_date)

        # Формат
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF", "Excel", "CSV"])

        # Кнопки
        btn_generate = QPushButton("Сгенерировать")
        btn_generate.clicked.connect(self.generate_report)

        layout.addLayout(period_layout)
        layout.addWidget(QLabel("Формат:"))
        layout.addWidget(self.format_combo)
        layout.addWidget(btn_generate)

        self.setLayout(layout)

    def generate_report(self):
        # Выбор файла
        file_filter = ""
        if self.format_combo.currentText() == "PDF":
            file_filter = "PDF Files (*.pdf)"
        elif self.format_combo.currentText() == "Excel":
            file_filter = "Excel Files (*.xlsx)"
        else:
            file_filter = "CSV Files (*.csv)"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчет",
            f"report_{QDate.currentDate().toString('yyyyMMdd')}",
            file_filter
        )

        if not file_path:
            return

        # Добавить эту часть для генерации отчета
        from report_generator import ReportGenerator
        from database import get_db
        from models import Ticket

        try:
            # Получаем даты
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            # Создаем генератор отчетов
            generator = ReportGenerator(self.user, start_date, end_date)

            # Получаем данные
            tickets = generator.get_tickets()

            if not tickets:
                QMessageBox.warning(self, "Ошибка", "Нет данных для выбранного периода")
                return

            # Генерируем отчет
            if self.format_combo.currentText() == "PDF":
                generator.generate_pdf(tickets, file_path)
            elif self.format_combo.currentText() == "Excel":
                generator.generate_excel(tickets, file_path)
            else:
                generator.generate_csv(tickets, file_path)

            # Уведомляем пользователя
            QMessageBox.information(
                self,
                "Успех",
                f"Отчет успешно сохранен:\n{file_path}"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сгенерировать отчет:\n{str(e)}"
            )