# controllers/lagu_controller.py

from structures.double_linked_list import DoubleLinkedList
from structures.song import Song

class SongController:
    """
    Controller sederhana untuk mengelola koleksi Song menggunakan DoubleLinkedList.
    API yang disediakan mudah dipakai GUI:
      - get_all_songs() -> list[Song]
      - get_song_at(index) -> Song or None
      - search(keyword) -> list[Song]
      - add_song(judul, artis, genre, vibes) -> Song
      - update_song(index, judul, artis, genre, vibes) -> bool
      - delete_song(index) -> bool
    """

    def __init__(self, initial_data=None):
        # gunakan DoubleLinkedList untuk menyimpan Song objects
        self.songs = DoubleLinkedList()
        if initial_data:
            # initial_data bisa berupa list of dict atau list of Song
            for item in initial_data:
                if isinstance(item, Song):
                    self.songs.add_last(item)
                elif isinstance(item, dict):
                    s = Song(item.get("judul"), item.get("artis"), item.get("genre"), item.get("vibes"))
                    self.songs.add_last(s)

    # ---------- helper ----------
    def _to_list(self):
        out = []
        node = self.songs.head
        while node:
            out.append(node.data)
            node = node.next
        return out

    # ---------- public API ----------
    def get_all_songs(self):
        return self._to_list()

    def get_song_at(self, index):
        node = self.songs.get_node(index)
        return node.data if node else None

    def search(self, keyword):
        if not keyword:
            return self.get_all_songs()
        kw = keyword.lower().strip()
        found = []
        node = self.songs.head
        while node:
            s = node.data
            if (kw in s.judul.lower() or
                kw in s.artis.lower() or
                kw in s.genre.lower() or
                kw in s.vibes.lower()):
                found.append(s)
            node = node.next
        return found

    def add_song(self, song):  # <--- terima objek Song
        self.songs.add_last(song)

    def update_song(self, index, judul, artis, genre, vibes):
        node = self.songs.get_node(index)
        if not node:
            return False
        node.data.judul = judul
        node.data.artis = artis
        node.data.genre = genre
        node.data.vibes = vibes
        return True

    def delete_song(self, index):
        return self.songs.delete_at(index)