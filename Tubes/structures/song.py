# structures/song.py

class Song:
    def __init__(self, judul, artis, genre, vibes):
        self.judul = judul
        self.artis = artis
        self.genre = genre
        self.vibes = vibes

    def to_dict(self):
        return {
            "judul": self.judul,
            "artis": self.artis,
            "genre": self.genre,
            "vibes": self.vibes
        }

    def __str__(self):
        # jangan pakai self.id karena tidak disimpan di objek ini
        return f"{self.judul} - {self.artis} ({self.genre}, {self.vibes})"