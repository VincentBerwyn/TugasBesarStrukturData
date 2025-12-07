# gui/login_window.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from controllers.auth import check_login
from controllers.shared import shared_song_controller


class LoginPopup(QFrame):
    """
    Widget kotak login putih
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 350)
        self.setStyleSheet("""
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 10px;
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(15)

        # Judul
        title_label = QLabel("Login")
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        main_layout.addSpacing(10)

        # Username
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan username")
        self._style_input(self.username_input)

        main_layout.addWidget(username_label)
        main_layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Masukkan password")
        self._style_input(self.password_input)

        main_layout.addWidget(password_label)
        main_layout.addWidget(self.password_input)

        main_layout.addSpacing(20)

        # Tombol Login
        self.login_button = QPushButton("Login")
        self.login_button.setFixedSize(QSize(100, 35))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.login_button)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

    def _style_input(self, line_edit):
        line_edit.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #28a745;
                padding: 5px 0;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #0056b3;
            }
        """)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #aaaaaa;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        center_layout = QHBoxLayout()
        center_layout.addStretch()

        self.login_popup = LoginPopup()
        center_layout.addWidget(self.login_popup)
        center_layout.addStretch()

        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        # Tombol close X
        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(24, 24)
        self.close_button.setFont(QFont("Arial", 10))
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ccc;
                color: #555;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                color: black;
            }
        """)
        self.close_button.clicked.connect(self.close)

        # Connect button
        self.login_popup.login_button.clicked.connect(self.do_login)

        # Enter untuk login
        self.login_popup.password_input.returnPressed.connect(self.do_login)
        self.login_popup.username_input.returnPressed.connect(self.do_login)

    def do_login(self):
        username = self.login_popup.username_input.text()
        password = self.login_popup.password_input.text()

        role = check_login(username, password)

        if role is None:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah!")
            return

        # Import di sini untuk mencegah circular import
        if role == "admin":
            from gui.admin_window import AdminWindow
            self.win = AdminWindow()
            
        else:
            from gui.user_window import UserWindow
            self.win = UserWindow()

        self.win.show()
        self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        popup_x = (self.width() - self.login_popup.width()) // 2
        popup_y = (self.height() - self.login_popup.height()) // 2

        self.close_button.move(
            popup_x + self.login_popup.width() - 12,
            popup_y - 12
        )