# gui/playlist_window.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from controllers.shared import shared_song_controller
from structures.double_linked_list import DoubleLinkedList
from structures.song import Song


class PlaylistWindow(QWidget):
    """
    Jendela untuk mengelola playlist (DoubleLinkedList).
    - Tambah lagu ke playlist (dari pencarian).
    - Hapus lagu dari playlist.
    - Play lagu (kembali ke UserWindow).
    """

    def __init__(self, dll_playlist: DoubleLinkedList, on_playlist_updated, parent=None):
        super().__init__(parent)

        self.active_playlist = dll_playlist
        self.controller = shared_song_controller
        self.on_playlist_updated = on_playlist_updated

        # Window settings
        self.setWindowTitle("Playlist Manager")
        self.setGeometry(220, 120, 1000, 700)

        self._setup_ui()
        self._load_playlist_content(self.active_playlist)

    # ==============================================================
    # UI SETUP
    # ==============================================================
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        # ==========================================================
        # 1. SEARCH AREA (add to playlist)
        # ==========================================================
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame { background-color: #1a1a1a; border-radius: 12px; padding: 15px; }
        """)
        root.addWidget(search_frame)

        v = QVBoxLayout(search_frame)
        v.setSpacing(10)

        lbl_search = QLabel("🔍 Cari Lagu untuk Ditambahkan")
        lbl_search.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        v.addWidget(lbl_search)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search songs by title or artist...")
        self.search_input.textChanged.connect(self._search_songs)
        self.search_input.setMinimumHeight(35)
        v.addWidget(self.search_input)

        # Scroll area search results
        self.search_results_scroll = QScrollArea()
        self.search_results_scroll.setWidgetResizable(True)
        self.search_results_scroll.setStyleSheet("border: none;")

        self.search_results_content = QFrame()
        self.search_results_grid = QGridLayout(self.search_results_content)
        self.search_results_grid.setSpacing(15)

        self.search_results_scroll.setWidget(self.search_results_content)
        v.addWidget(self.search_results_scroll, 1)

        # initial songs
        self._load_search_results(self.controller.get_all_songs())

        # ==========================================================
        # 2. Playlist Content
        # ==========================================================
        playlist_frame = QFrame()
        playlist_frame.setStyleSheet("""
            QFrame { background-color: #1a1a1a; border-radius: 12px; padding: 15px; }
        """)
        root.addWidget(playlist_frame, 1)

        v2 = QVBoxLayout(playlist_frame)
        v2.setSpacing(10)

        lbl_playlist = QLabel("🎵 Playlist Kamu (DLL)")
        lbl_playlist.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        v2.addWidget(lbl_playlist)

        self.playlist_scroll = QScrollArea()
        self.playlist_scroll.setWidgetResizable(True)
        self.playlist_scroll.setStyleSheet("border: none;")

        self.playlist_content = QFrame()
        self.playlist_vbox = QVBoxLayout(self.playlist_content)
        self.playlist_vbox.setSpacing(8)
        self.playlist_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.playlist_scroll.setWidget(self.playlist_content)
        v2.addWidget(self.playlist_scroll, 1)

    # ==============================================================
    # SEARCH LOGIC
    # ==============================================================
    def _search_songs(self, keyword):
        songs = self.controller.search(keyword) if keyword else self.controller.get_all_songs()
        self._load_search_results(songs)

    def _load_search_results(self, songs):
        # Clear previous grid
        for i in reversed(range(self.search_results_grid.count())):
            w = self.search_results_grid.itemAt(i).widget()
            if w:
                w.deleteLater()

        col, row = 0, 0
        for song in songs:
            card = self._song_card_add(song)
            self.search_results_grid.addWidget(card, row, col)

            col += 1
            if col >= 2:
                col = 0
                row += 1

    def _song_card_add(self, song: Song):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background-color: #222; border-radius: 8px; }
            QFrame:hover { background-color: #2f2f2f; }
        """)

        h = QHBoxLayout(frame)
        h.setContentsMargins(10, 10, 10, 10)

        # Thumbnail
        img = QLabel("💿")
        img.setFixedSize(40, 40)
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setStyleSheet("background:#333; border-radius:4px;")
        h.addWidget(img)

        # Info
        v = QVBoxLayout()
        lbl_title = QLabel(song.judul)
        lbl_artist = QLabel(song.artis)
        lbl_artist.setStyleSheet("color:#bdbdbd; font-size:11px;")
        v.addWidget(lbl_title)
        v.addWidget(lbl_artist)

        h.addLayout(v)
        h.addStretch()

        # Add button
        btn_add = QPushButton("Add")
        btn_add.setStyleSheet("background:#1db954; padding:5px 10px; border-radius:5px;")
        btn_add.clicked.connect(lambda _, s=song: self._add_song_to_playlist(s))
        h.addWidget(btn_add)

        return frame

    # ==============================================================
    # PLAYLIST CONTENT LOGIC
    # ==============================================================
    def _load_playlist_content(self, dll: DoubleLinkedList):
        # clear
        for i in reversed(range(self.playlist_vbox.count())):
            w = self.playlist_vbox.itemAt(i).widget()
            if w:
                w.deleteLater()

        node = dll.head
        index = 1

        while node:
            song = node.data
            item = self._playlist_item(index, song)
            self.playlist_vbox.addWidget(item)

            index += 1
            node = node.next

        self.playlist_vbox.addStretch()

    def _playlist_item(self, index, song: Song):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background:#2b2b2b; border-radius:6px; }
        """)

        h = QHBoxLayout(frame)
        h.setContentsMargins(10, 5, 10, 5)

        lbl_no = QLabel(f"{index}.")
        lbl_no.setFixedWidth(30)
        h.addWidget(lbl_no)

        info = QLabel(f"<b>{song.judul}</b> - {song.artis}")
        h.addWidget(info)
        h.addStretch()

        # PLAY BUTTON
        btn_play = QPushButton("▶️")`
        btn_play.setFixedWidth(40)
        btn_play.setStyleSheet("background:#1db954; bo`rder-radius:5px;")
        btn_play.clicked.connect(lambda _, s=song: self._play_and_close(s))
        h.addWidget(btn_play)

        # REMOVE BUTTON
        btn_remove = QPushButton("🗑")
        btn_remove.setFixedWidth(35)
        btn_remove.setStyleSheet("background:#444; border-radius:5px;")
        btn_remove.clicked.connect(lambda _, s=song: self._remove_song(s))
        h.addWidget(btn_remove)

        return frame

    # ==============================================================
    # BUTTON ACTIONS
    # ==============================================================
    def _add_song_to_playlist(self, song: Song):
        self.active_playlist.add_last(song)
        self._load_playlist_content(self.active_playlist)
        self.on_playlist_updated()
        print(f"[Playlist] Added: {song.judul}")

    def _remove_song(self, song: Song):
        self.active_playlist.remove_by_data(song)
        self._load_playlist_content(self.active_playlist)
        self.on_playlist_updated()
        print(f"[Playlist] Removed: {song.judul}")

    def _play_and_close(self, song: Song):
        # Pastikan UserWindow memiliki method _play_song
        parent = self.parent()
        if parent and hasattr(parent, "_play_song"):
            parent._play_song(song)

        print(f"[Playlist] Play: {song.judul}")
        self.close()