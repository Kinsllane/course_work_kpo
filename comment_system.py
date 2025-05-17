from PyQt6.QtWidgets import (
    QWidget, QTextEdit, QPushButton, QVBoxLayout, QListWidget, QMessageBox, QLabel
)
from database import get_db
from models import Comment


class CommentSystem(QWidget):
    def __init__(self, ticket_id):
        super().__init__()
        self.ticket_id = ticket_id
        self.initUI()
        self.load_comments()

    def initUI(self):
        layout = QVBoxLayout()

        self.comment_list = QListWidget()
        self.comment_input = QTextEdit()
        send_btn = QPushButton("Отправить")
        send_btn.clicked.connect(self.save_comment)

        layout.addWidget(QLabel("Комментарии:"))
        layout.addWidget(self.comment_list)
        layout.addWidget(QLabel("Новый комментарий:"))
        layout.addWidget(self.comment_input)
        layout.addWidget(send_btn)

        self.setLayout(layout)

    def load_comments(self):
        db = next(get_db())
        comments = db.query(Comment).filter(Comment.ticket_id == self.ticket_id).all()

        self.comment_list.clear()
        for comment in comments:
            self.comment_list.addItem(
                f"[{comment.created_at}] {comment.user.full_name}: {comment.text}"
            )

    def save_comment(self):
        text = self.comment_input.toPlainText().strip()
        if not text:
            return

        db = next(get_db())
        try:
            new_comment = Comment(
                text=text,
                ticket_id=self.ticket_id,
                user_id=self.current_user.id
            )
            db.add(new_comment)
            db.commit()
            self.load_comments()
            self.comment_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")