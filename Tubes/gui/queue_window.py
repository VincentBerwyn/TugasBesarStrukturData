# gui/queue_window.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from structures.queue import Queue
from structures.song import Song

class QueueWindow(QWidget):
    def __init__(self, queue: Queue, play_callback):
        """
        queue        : objek Queue dari shared controller
        play_callback: fungsi untuk memutar lagu (dari UserWindow)
        """
        super().__init__()
        self.setWindowTitle("Music Player - Antrian Lagu")
        self.setGeometry(150, 80, 700, 800)

        self.queue_data = queue
        self.play_callback = play_callback  # bisa dipanggil saat Play Next

        # Layout utama
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Header
        header = QLabel("🎵 Antrian Lagu")
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #1ED760;")
        main_layout.addWidget(header)

        # Scroll area untuk daftar lagu
        self.scroll_widget = QWidget()
        self.song_list_layout = QVBoxLayout(self.scroll_widget)
        self.song_list_layout.setContentsMargins(0, 0, 0, 0)
        self.song_list_layout.setSpacing(10)
        self.song_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.scroll_widget)
        scroll_area.setFrameShape(scroll_area.Shape.NoFrame)
        main_layout.addWidget(scroll_area)

        self.refresh_queue_ui()

    # -------------------------
    # Buat ulang daftar lagu
    # -------------------------
    def refresh_queue_ui(self):
        # hapus semua widget dulu
        while self.song_list_layout.count():
            item = self.song_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        songs = self.queue_data.to_list()  # Queue -> list
        for index, song in enumerate(songs):
            is_now_playing = (index == 0)
            card = self.create_song_card(song, is_now_playing)
            self.song_list_layout.addWidget(card)

    # -------------------------
    # Buat card lagu
    # -------------------------
    def create_song_card(self, song: Song, is_now_playing=False):
        frame = QWidget()
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        frame.setFixedHeight(80)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Icon kiri
        icon = QLabel("▶️" if is_now_playing else "🎵")
        icon.setFixedSize(30, 30)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"color: {'#1ED760' if is_now_playing else '#FFFFFF'};")
        layout.addWidget(icon)

        # Info tengah
        info_layout = QVBoxLayout()
        title_label = QLabel(song.judul)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        artist_label = QLabel(song.artis)
        artist_label.setFont(QFont("Arial", 10))
        artist_label.setStyleSheet("color: #B3B3B3;")
        info_layout.addWidget(title_label)
        info_layout.addWidget(artist_label)
        layout.addLayout(info_layout)
        layout.addStretch()

        # Tombol kanan jika bukan lagu yang sedang diputar
        if not is_now_playing:
            # Hapus
            btn_delete = QPushButton("🗑️")
            btn_delete.setFixedSize(35, 35)
            btn_delete.clicked.connect(lambda _, s=song: self.remove_song(s))
            layout.addWidget(btn_delete)

            # Putar selanjutnya
            btn_next = QPushButton("⏭️")
            btn_next.setFixedSize(35, 35)
            btn_next.setStyleSheet("color: #1ED760;")
            btn_next.clicked.connect(lambda _, s=song: self.move_song_next(s))
            layout.addWidget(btn_next)

        return frame

    # -------------------------
    # Hapus lagu dari queue
    # -------------------------
    def remove_song(self, song: Song):
        temp = []
        removed = False
        while not self.queue_data.is_empty():
            s = self.queue_data.dequeue()
            if s == song and not removed:
                removed = True
                continue
            temp.append(s)
        for s in temp:
            self.queue_data.enqueue(s)
        self.refresh_queue_ui()

    # -------------------------
    # Pindahkan lagu ke posisi Putar Selanjutnya
    # -------------------------
    def move_song_next(self, song: Song):
        temp = []
        moved = False
        # simpan lagu pertama (sedang diputar)
        first_song = self.queue_data.dequeue() if not self.queue_data.is_empty() else None

        while not self.queue_data.is_empty():
            s = self.queue_data.dequeue()
            if s == song and not moved:
                temp.insert(0, s)  # taruh setelah lagu pertama
                moved = True
            else:
                temp.append(s)

        if first_song:
            self.queue_data.enqueue(first_song)
        for s in temp:
            self.queue_data.enqueue(s)

        self.refresh_queue_ui()

        # Opsional: langsung putar lagu selanjutnya
        if self.play_callback:
            self.play_callback(song)