# gui/admin_window.py

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from structures.song import Song
from controllers.shared import shared_song_controller

STYLE_SHEET = """
QWidget {
    background-color: #121212;
    color: #b3b3b3;
    font-family: Arial;
}
QLineEdit {
    padding: 6px;
    background: #1f1f1f;
    border: 1px solid #333;
    border-radius: 6px;
    color: white;
}
QPushButton {
    background-color: #1db954;
    color: black;
    padding: 8px;
    border-radius: 6px;
}
QPushButton:hover {
    background-color: #1ed760;
}
"""

class AdminWindow(QMainWindow):
    """GUI Admin — CRUD lagu menggunakan shared_song_controller."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Panel Musik")
        self.setGeometry(200, 100, 900, 650)
        self.setStyleSheet(STYLE_SHEET)

        # Shared controller (data tetap tersimpan setelah logout)
        self.song_controller = shared_song_controller

        self._setup_ui()
        self._load_table()

    # -------------------------------------------------------------
    # SETUP UI
    # -------------------------------------------------------------
    def _setup_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QHBoxLayout()
        title = QLabel("Library Lagu (Admin)")
        title.setFont(QFont("Arial", 22, 700))

        btn_logout = QPushButton("Logout")
        btn_logout.setStyleSheet("background:#e63946; color:white;")
        btn_logout.clicked.connect(self._logout)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_logout)
        layout.addLayout(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Judul", "Artis", "Genre", "Vibes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        # Buttons
        buttons = QHBoxLayout()

        btn_add = QPushButton("Tambah Lagu")
        btn_edit = QPushButton("Edit Lagu")
        btn_delete = QPushButton("Hapus Lagu")

        btn_add.clicked.connect(self._show_add_form)
        btn_edit.clicked.connect(self._edit_song)
        btn_delete.clicked.connect(self._delete_song)

        buttons.addWidget(btn_add)
        buttons.addWidget(btn_edit)
        buttons.addWidget(btn_delete)
        buttons.addStretch()

        layout.addLayout(buttons)

        self.setCentralWidget(widget)

    # -------------------------------------------------------------
    # TABLE LOAD
    # -------------------------------------------------------------
    def _load_table(self):
        songs = self.song_controller.get_all_songs()
        self.table.setRowCount(len(songs))

        for idx, s in enumerate(songs):
            self.table.setItem(idx, 0, QTableWidgetItem(s.judul))
            self.table.setItem(idx, 1, QTableWidgetItem(s.artis))
            self.table.setItem(idx, 2, QTableWidgetItem(s.genre))
            self.table.setItem(idx, 3, QTableWidgetItem(s.vibes))

    # -------------------------------------------------------------
    # ADD SONG
    # -------------------------------------------------------------
    def _show_add_form(self):
        self._open_form(mode="add")

    # -------------------------------------------------------------
    # EDIT SONG
    # -------------------------------------------------------------
    def _edit_song(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Pilih lagu yang ingin diedit.")
            return

        self._open_form(mode="edit", index=row)

    # -------------------------------------------------------------
    # FORM POPUP
    # -------------------------------------------------------------
    def _open_form(self, mode="add", index=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Tambah / Edit Lagu")
        dialog.setStyleSheet(STYLE_SHEET)
        form = QFormLayout(dialog)

        inp_judul = QLineEdit()
        inp_artis = QLineEdit()
        inp_genre = QLineEdit()
        inp_vibes = QLineEdit()

        # Isi data lama saat edit
        if mode == "edit":
            old = self.song_controller.get_song_at(index)
            inp_judul.setText(old.judul)
            inp_artis.setText(old.artis)
            inp_genre.setText(old.genre)
            inp_vibes.setText(old.vibes)

        form.addRow("Judul", inp_judul)
        form.addRow("Artis", inp_artis)
        form.addRow("Genre", inp_genre)
        form.addRow("Vibes", inp_vibes)

        btn_save = QPushButton("Simpan")
        form.addWidget(btn_save)

        # SAVE ACTION
        btn_save.clicked.connect(
            lambda: self._save(dialog, mode, index, inp_judul, inp_artis, inp_genre, inp_vibes)
        )

        dialog.exec()

    # -------------------------------------------------------------
    def _save(self, dialog, mode, index, judul, artis, genre, vibes):
        if not all([judul.text(), artis.text(), genre.text(), vibes.text()]):
            QMessageBox.warning(self, "Error", "Semua kolom harus diisi.")
            return

        if mode == "add":
            new_song = Song(judul.text(), artis.text(), genre.text(), vibes.text())
            self.song_controller.add_song(new_song)
        else:
            self.song_controller.update_song(index, judul.text(), artis.text(), genre.text(), vibes.text())

        dialog.close()
        self._load_table()

    # -------------------------------------------------------------
    # DELETE SONG
    # -------------------------------------------------------------
    def _delete_song(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Pilih lagu yang ingin dihapus.")
            return

        self.song_controller.delete_song(row)
        self._load_table()

    # -------------------------------------------------------------
    # LOGOUT
    # -------------------------------------------------------------
    def _logout(self):
        from gui.login_window import LoginWindow
        self.close()
        self.login = LoginWindow()
        self.login.show()


# ---- TEST ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AdminWindow()
    win.show()
    sys.exit(app.exec())