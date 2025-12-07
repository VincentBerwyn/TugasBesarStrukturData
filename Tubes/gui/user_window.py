# gui/user_window.py
import sys

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QFrame, QScrollArea, QGridLayout, QApplication, QSizePolicy, QMessageBox,
    QListWidget, QListWidgetItem, QAbstractItemView
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from controllers.shared import shared_song_controller
from structures.double_linked_list import DoubleLinkedList
from structures.stack import Stack
from structures.queue import Queue
from structures.song import Song

# --------------------------
# Tema dark sederhana
# --------------------------
DARK_STYLE = """
    QWidget {
        background-color: #0f0f0f;
        color: #e9e9e9;
        font-family: Arial;
    }
    QLineEdit {
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 8px;
        color: #e9e9e9;
    }
    QLabel#title {
        color: #ffffff;
    }
    QPushButton.play {
        background-color: #1db954;
        color: white;
        border-radius: 8px;
        padding: 8px 12px;
    }
    QPushButton.icon {
        background-color: #2e2e2e;
        color: #ffffff;
        border-radius: 12px;
        padding: 8px;
    }
    QFrame#sidebarFrame {
        background-color: #121212;
        border-right: 1px solid #252525;
    }
    QFrame#playerBar {
        background-color: #0b0b0b;
        border-top: 1px solid #222;
    }
"""

# --------------------------
# UserWindow
# --------------------------
class UserWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player - User")
        self.setGeometry(120, 60, 1200, 780)
        self.setStyleSheet(DARK_STYLE)

        self.controller = shared_song_controller
        self.playlist = DoubleLinkedList()
        self.queue = Queue()       # antrian
        self.history = Stack()

        self.favorites = set()
        self.is_playing = False

        all_songs = self.controller.get_all_songs()
        for s in all_songs:
            self.playlist.add_last(s)
        self.playlist.current = None

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = self._sidebar()
        root.addWidget(self.sidebar)

        content_container = QFrame()
        content_vbox = QVBoxLayout(content_container)
        content_vbox.setContentsMargins(18, 18, 18, 8)
        content_vbox.setSpacing(12)

        self.content = self._content_dashboard(all_songs)
        content_vbox.addWidget(self.content, 1)

        self.player_bar = self._player_bar()
        content_vbox.addWidget(self.player_bar, 0)

        root.addWidget(content_container, 1)

    # --------------------------
    # Sidebar
    # --------------------------
    def _sidebar(self):
        frame = QFrame()
        frame.setObjectName("sidebarFrame")
        frame.setFixedWidth(180)

        v = QVBoxLayout(frame)
        v.setContentsMargins(18, 18, 12, 18)
        v.setSpacing(10)

        title = QLabel("🎵 MUSIC")
        title.setObjectName("title")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1db954;")
        v.addWidget(title)

        items = [
            ("🏠 Home", self._action_home),
            ("🔍 Search", self._action_search),
            ("🎶 Playlist", self._action_playlist),
            ("➕ Antrian", self._show_queue_content),
            ("❤️ Favorites", self._open_favorites_window),
            ("⏳ History", self._open_history_window),
        ]
        for txt, func in items:
            btn = QPushButton(txt)
            btn.setStyleSheet("text-align:left; font-size:14px; color:#bdbdbd; padding:6px; background:none; border:none;")
            btn.clicked.connect(func)
            v.addWidget(btn)

        v.addStretch()
        return frame

    # --------------------------
    # Content dashboard
    # --------------------------
    def _content_dashboard(self, initial_songs):
        content = QFrame()
        v = QVBoxLayout(content)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(10)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search songs...")
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self._on_search_text)

        btn_search = QPushButton("Search")
        btn_search.setFixedWidth(100)
        btn_search.setProperty("class", "play")
        btn_search.clicked.connect(self._do_search)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_search)
        v.addLayout(search_layout)

        title_layout = QHBoxLayout()
        title_lbl = QLabel("🎧 Playlist")
        title_lbl.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_layout.addWidget(title_lbl)
        title_layout.addStretch()

        self.btn_shuffle = QPushButton("Shuffle Off")
        self.btn_shuffle.setFixedWidth(110)
        self.btn_shuffle.setProperty("class", "icon")
        self.btn_shuffle.clicked.connect(self._toggle_shuffle)

        self.btn_repeat = QPushButton("Repeat: Off")
        self.btn_repeat.setFixedWidth(110)
        self.btn_repeat.setProperty("class", "icon")
        self.btn_repeat.clicked.connect(self._cycle_repeat)

        title_layout.addWidget(self.btn_shuffle)
        title_layout.addWidget(self.btn_repeat)
        v.addLayout(title_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        scroll_content = QFrame()
        self.grid = QGridLayout(scroll_content)
        self.grid.setContentsMargins(8, 8, 8, 8)
        self.grid.setHorizontalSpacing(24)
        self.grid.setVerticalSpacing(24)
        scroll.setWidget(scroll_content)
        v.addWidget(scroll, 1)

        self._load_playlist_grid(initial_songs)
        return content

    # --------------------------
    # Player bar
    # --------------------------
    def _player_bar(self):
        bar = QFrame()
        bar.setObjectName("playerBar")
        bar.setFixedHeight(90)

        h = QHBoxLayout(bar)
        h.setContentsMargins(20, 12, 20, 12)
        h.setSpacing(14)

        self.btn_prev = QPushButton("⏮")
        self.btn_play = QPushButton("▶️")
        self.btn_next = QPushButton("⏭")

        self.btn_prev.setProperty("class", "icon")
        self.btn_play.setProperty("class", "icon")
        self.btn_next.setProperty("class", "icon")

        self.btn_prev.setFixedSize(46, 46)
        self.btn_play.setFixedSize(46, 46)
        self.btn_next.setFixedSize(46, 46)

        self.btn_prev.clicked.connect(self._prev)
        self.btn_next.clicked.connect(self._next)
        self.btn_play.clicked.connect(self._play_or_pause)

        self.lbl_now = QLabel("Tidak ada lagu diputar")
        self.lbl_now.setFont(QFont("Arial", 12))

        h.addWidget(self.btn_prev)
        h.addWidget(self.btn_play)
        h.addWidget(self.btn_next)
        h.addSpacing(20)
        h.addWidget(self.lbl_now)
        h.addStretch()

        return bar

    # --------------------------
    # Grid & Card
    # --------------------------
    def _load_playlist_grid(self, songs):
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        MAX_COLS = 4
        col = 0
        row = 0

        for s in songs:
            card = self._song_card(s)
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= MAX_COLS:
                col = 0
                row += 1

    def _song_card(self, song: Song):
        frame = QFrame()
        frame.setFixedSize(260, 220)
        frame.setStyleSheet("""
            QFrame {
                background-color: #161616;
                border-radius: 12px;
            }
            QFrame:hover {
                background-color: #1f1f1f;
            }
        """)

        v = QVBoxLayout(frame)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(8)

        img = QLabel("💿  [ALBUM]")
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setFixedHeight(100)
        img.setStyleSheet("background-color:#2b2b2b; border-radius:8px;")

        title = QLabel(song.judul)
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")

        artist = QLabel(song.artis)
        artist.setStyleSheet("color: #bdbdbd; font-size: 11px;")

        btn_row = QHBoxLayout()
        btn_play = QPushButton("▶️ Play")
        btn_play.setProperty("class", "play")
        btn_play.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_play.clicked.connect(lambda _, s=song: self._play_song_from_card(s))

        btn_q = QPushButton("➕ Tambah ke Antrian")
        btn_q.setProperty("class", "icon")
        btn_q.setFixedSize(120, 32)
        btn_q.clicked.connect(lambda _, s=song: self._add_to_queue(s))

        btn_fav = QPushButton("♡" if (song.judul, song.artis) not in self.favorites else "♥")
        btn_fav.setProperty("class", "icon")
        btn_fav.setFixedSize(40, 32)
        btn_fav.clicked.connect(lambda _, b=btn_fav, s=song: self._toggle_favorite(b, s))

        btn_row.addWidget(btn_play)
        btn_row.addWidget(btn_q)
        btn_row.addWidget(btn_fav)

        v.addWidget(img)
        v.addSpacing(6)
        v.addWidget(title)
        v.addWidget(artist)
        v.addStretch()
        v.addLayout(btn_row)

        return frame

    # --------------------------
    # Search
    # --------------------------
    def _on_search_text(self, text):
        songs = self.controller.get_all_songs() if text.strip() == "" else self.controller.search(text)
        self._load_playlist_grid(songs)

    def _do_search(self):
        key = self.search_input.text().strip()
        songs = self.controller.search(key) if key else self.controller.get_all_songs()
        self._load_playlist_grid(songs)

    # --------------------------
    # Sidebar actions
    # --------------------------
    def _action_home(self):
        self._load_playlist_grid(self.controller.get_all_songs())

    def _action_search(self):
        self.search_input.setFocus()

    def _action_playlist(self):
        self._load_playlist_grid(self.playlist.to_list())

    # --------------------------
    # Antrian
    # --------------------------
    def _show_queue_content(self):
        # Kosongkan grid
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # QListWidget untuk antrian
        self.queue_list = QListWidget()
        self.queue_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.queue_list.setStyleSheet("""
            QListWidget {
                background-color: #161616;
                color: #e9e9e9;
                border-radius: 12px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #1db954;
            }
        """)

        # Masukkan item antrian
        temp = []
        while not self.queue.is_empty():
            s = self.queue.dequeue()
            temp.append(s)
            self.queue_list.addItem(f"{s.judul} - {s.artis}")
        for s in temp:
            self.queue.enqueue(s)

        self.grid.addWidget(self.queue_list, 0, 0)

    def _update_queue_order(self):
        new_queue = Queue()
        for i in range(self.queue_list.count()):
            text = self.queue_list.item(i).text()
            judul, artis = text.split(" - ")
            for song in self.playlist.to_list():
                if song.judul == judul and song.artis == artis:
                    new_queue.enqueue(song)
                    break
        self.queue = new_queue

    def _add_to_queue(self, song):
        self.queue.enqueue(song)
        QMessageBox.information(self, "Tambah ke Antrian", f"'{song.judul}' telah ditambahkan ke antrian.")

    # --------------------------
    # Riwayat / Favorit
    # --------------------------
    def _open_history_window(self):
        items = []
        temp = Stack()
        while not self.history.is_empty():
            s = self.history.pop()
            items.append(f"{s.judul} - {s.artis}")
            temp.push(s)
        while not temp.is_empty():
            self.history.push(temp.pop())
        text = "\n".join(items) if items else "Belum ada riwayat"
        QMessageBox.information(self, "History", text)

    def _toggle_favorite(self, btn, song):
        key = (song.judul, song.artis)
        if key in self.favorites:
            self.favorites.remove(key)
            btn.setText("♡")
            QMessageBox.information(self, "Favorites", f"'{song.judul}' dihapus dari favorit.")
        else:
            self.favorites.add(key)
            btn.setText("♥")
            QMessageBox.information(self, "Favorites", f"'{song.judul}' ditambahkan ke favorit.")

    def _open_favorites_window(self):
        if not self.favorites:
            QMessageBox.information(self, "Favorites", "Belum ada favorit.")
            return
        lines = [f"{t[0]} - {t[1]}" for t in self.favorites]
        QMessageBox.information(self, "Favorites", "\n".join(lines))

    # --------------------------
    # Playback
    # --------------------------
    def _play_song_from_card(self, song: Song):
        self.playlist.jump_to_song(song)
        if not self.playlist.current or self.playlist.current.data != song:
            self.playlist.add_last(song)
            self.playlist.current = self.playlist.tail
        self.history.push(song)
        self.is_playing = True
        self.btn_play.setText("⏸️")
        self.lbl_now.setText(f"Now Playing: {song.judul} - {song.artis}")

    def _play_song(self, song: Song):
        if self.playlist.current and self.playlist.current.data == song:
            self.lbl_now.setText(f"Now Playing: {song.judul} - {song.artis}")
            self.is_playing = True
            self.btn_play.setText("⏸️")
            return
        self.history.push(song)
        self.lbl_now.setText(f"Now Playing: {song.judul} - {song.artis}")
        self.is_playing = True
        self.btn_play.setText("⏸️")
        node = self.playlist.head
        found = None
        while node:
            if node.data == song:
                found = node
                break
            node = node.next
        if not found:
            self.playlist.add_last(song)
            found = self.playlist.tail
        self.playlist.current = found

    def _play_or_pause(self):
        if not self.playlist.current:
            first = self.playlist.play_first()
            if first:
                self._play_song(first)
            return
        if self.is_playing:
            cur = self.playlist.current.data
            self.lbl_now.setText(f"Paused: {cur.judul}")
            self.btn_play.setText("▶️")
            self.is_playing = False
        else:
            cur = self.playlist.current.data
            self.lbl_now.setText(f"Now Playing: {cur.judul} - {cur.artis}")
            self.btn_play.setText("⏸️")
            self.is_playing = True

    def _next(self):
        nxt = self.playlist.next_song_smart()
        if nxt:
            self.history.push(nxt)
            self.is_playing = True
            self.btn_play.setText("⏸️")
            self.lbl_now.setText(f"Now Playing: {nxt.judul} - {nxt.artis}")
            return
        QMessageBox.information(self, "Info", "Tidak ada lagu berikutnya.")

    def _prev(self):
        prev = self.playlist.prev_song_smart()
        if prev:
            self.history.push(prev)
            self.is_playing = True
            self.btn_play.setText("⏸️")
            self.lbl_now.setText(f"Now Playing: {prev.judul} - {prev.artis}")
            return
        QMessageBox.information(self, "Info", "Tidak ada lagu sebelumnya.")

    # --------------------------
    # Shuffle / Repeat
    # --------------------------
    def _toggle_shuffle(self):
        new_state = not getattr(self.playlist, "shuffle", False)
        self.playlist.enable_shuffle(new_state)
        self.btn_shuffle.setText("Shuffle On" if new_state else "Shuffle Off")

    def _cycle_repeat(self):
        cur = getattr(self.playlist, "repeat_mode", 0)
        nxt = (cur + 1) % 3
        self.playlist.set_repeat_mode(nxt)
        txt = "Off" if nxt == 0 else ("All" if nxt == 1 else "One")
        self.btn_repeat.setText(f"Repeat: {txt}")

# --------------------------
# Run app standalone
# --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = UserWindow()
    w.show()
    sys.exit(app.exec())