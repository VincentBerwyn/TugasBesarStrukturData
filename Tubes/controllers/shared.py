# controllers/shared.py

from controllers.lagu_controller import SongController
from gui.initial_data import INITIAL_SONGS

# hanya dibuat sekali
shared_song_controller = SongController(initial_data=INITIAL_SONGS)