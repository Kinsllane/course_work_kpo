# report_generator.py
from datetime import datetime
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from openpyxl import Workbook
from database import get_db
from models import Ticket, TicketStatus, User, UserRole


class ReportGenerator:
    def __init__(self, user, start_date, end_date):
        self.user = user
        self.start_date = start_date
        self.end_date = end_date

    def generate_pdf(self, tickets, file_path):
        c = canvas.Canvas(file_path, pagesize=A4)  # Используем переданный путь
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 800, f"Отчет ({self.start_date} - {self.end_date})")

        y = 750
        c.setFont("Helvetica", 10)
        for ticket in tickets:
            text = f"{ticket.id} | {ticket.title} | {ticket.status.value}"
            c.drawString(50, y, text)
            y -= 20
            if y < 50:
                c.showPage()
                y = 800
        c.save()

    def generate_excel(self, tickets, file_path):
        wb = Workbook()
        ws = wb.active
        ws.title = "Заявки"
        ws.append(["ID", "Заголовок", "Статус", "Дата"])

        for ticket in tickets:
            ws.append([
                ticket.id,
                ticket.title,
                ticket.status.value,
                ticket.created_at.strftime('%d.%m.%Y')
            ])

        wb.save(file_path)  # Сохраняем по переданному пути

    def generate_csv(self, tickets, file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:  # Используем file_path
            writer = csv.writer(f, delimiter=';')
            writer.writerow(["ID", "Заголовок", "Статус", "Дата"])
            for ticket in tickets:
                writer.writerow([
                    ticket.id,
                    ticket.title,
                    ticket.status.value,
                    ticket.created_at.strftime('%d.%m.%Y')
                ])

    def get_tickets(self):
        db = next(get_db())
        query = db.query(Ticket).filter(
            Ticket.created_at >= self.start_date,
            Ticket.created_at <= self.end_date
        )

        if self.user.role == UserRole.TECHNICIAN:
            query = query.filter(Ticket.technician_id == self.user.id)

        return query.all()