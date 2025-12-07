# main.py

import sys
from PyQt6.QtWidgets import QApplication

from gui.login_window import LoginWindow
from controllers.shared import shared_song_controller

# --- optional: inisialisasi data awal (jika belum ada) ---
from structures.song import Song

# --- start aplikasi ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec())