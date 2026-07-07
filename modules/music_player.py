import os
import random
from PySide6.QtCore import QThread, Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

SUPPORTED_FORMATS = [
    '.mp3', '.mp4', '.wav', '.flac',
    '.ogg', '.m4a', '.aac', '.wma',
    '.mkv', '.avi', '.mov'
]

SEARCH_LOCATIONS = [
    os.path.join(os.path.expanduser('~'), 'Music'),
    os.path.join(os.path.expanduser('~'), 'Downloads'),
    os.path.join(os.path.expanduser('~'), 'Desktop'),
    os.path.join(os.path.expanduser('~'), 'Videos'),
    os.path.join(os.path.expanduser('~'), 'Documents'),
    r'D:\\',
    r'D:\Songs',
    r'D:\Music',
    r'D:\Downloads',
    r'E:\\',
    r'E:\Songs',
    r'E:\Music',
    r'C:\Users\Public\Music',
]


class SongSearchThread(QThread):
    song_found = Signal(str, str)
    song_not_found = Signal(str)
    search_progress = Signal(str)

    def __init__(
        self, query=None,
        random_mode=False, parent=None
    ):
        super().__init__(parent)
        self.query = query.lower().strip() \
            if query else None
        self.random_mode = random_mode

    def run(self):
        if self.random_mode:
            self.search_progress.emit(
                "Picking a random song from your PC..."
            )
            self._find_random_song()
        else:
            self.search_progress.emit(
                f"Searching for "
                f"'{self.query}'..."
            )
            self._find_specific_song()

    # ----------------------------
    # Find Random Song
    # ----------------------------
    def _find_random_song(self):
        all_songs = []

        for location in SEARCH_LOCATIONS:
            if not os.path.exists(location):
                continue
            try:
                for root, dirs, files in \
                        os.walk(location):
                    dirs[:] = [
                        d for d in dirs
                        if not d.startswith('.')
                    ]
                    for file in files:
                        ext = os.path.splitext(
                            file
                        )[1].lower()
                        if ext in SUPPORTED_FORMATS:
                            full_path = os.path.join(
                                root, file
                            )
                            all_songs.append(
                                (full_path, file)
                            )
            except Exception:
                continue

        if all_songs:
            # Pick random song
            path, name = random.choice(all_songs)
            self.song_found.emit(path, name)
        else:
            self.song_not_found.emit("random song")

    # ----------------------------
    # Find Specific Song
    # ----------------------------
    def _find_specific_song(self):
        found_files = []

        for location in SEARCH_LOCATIONS:
            if not os.path.exists(location):
                continue
            try:
                for root, dirs, files in \
                        os.walk(location):
                    dirs[:] = [
                        d for d in dirs
                        if not d.startswith('.')
                    ]
                    for file in files:
                        ext = os.path.splitext(
                            file
                        )[1].lower()
                        if ext not in \
                                SUPPORTED_FORMATS:
                            continue
                        if self._matches(
                            self.query,
                            file.lower()
                        ):
                            full_path = os.path.join(
                                root, file
                            )
                            found_files.append(
                                (full_path, file)
                            )
            except Exception:
                continue

        if found_files:
            best = self._best_match(found_files)
            self.song_found.emit(best[0], best[1])
        else:
            self.song_not_found.emit(self.query)

    def _matches(self, query, filename):
        name = os.path.splitext(
            filename
        )[0].lower()
        name_clean = name.replace(
            '-', ' '
        ).replace('_', ' ').replace(
            '.', ' '
        ).strip()
        query_clean = query.replace(
            '-', ' '
        ).replace('_', ' ').strip()

        if query_clean in name_clean:
            return True

        query_words = query_clean.split()
        if all(
            w in name_clean for w in query_words
        ):
            return True

        if len(query_words) > 0:
            matches = sum(
                1 for w in query_words
                if w in name_clean
            )
            if matches / len(query_words) >= 0.6:
                return True

        return False

    def _best_match(self, files):
        scored = []
        for path, name in files:
            name_lower = name.lower()
            score = 0
            if self.query in name_lower:
                score += 100
            score -= len(name) * 0.1
            ext = os.path.splitext(name)[1].lower()
            if ext == '.mp3':
                score += 10
            elif ext == '.flac':
                score += 8
            scored.append((score, path, name))
        scored.sort(reverse=True)
        return (scored[0][1], scored[0][2])


class MusicPlayer:
    def __init__(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)

        self.search_thread = None
        self.current_song = None
        self.is_playing = False

        self.player.playbackStateChanged.connect(
            self._on_state_changed
        )
        self.player.errorOccurred.connect(
            self._on_error
        )

        self._on_found_cb = None
        self._on_not_found_cb = None
        self._on_progress_cb = None
        self._on_finished_cb = None

    # ----------------------------
    # Play specific song by name
    # ----------------------------
    def play_song(
        self, query,
        on_found=None, on_not_found=None,
        on_progress=None, on_finished=None
    ):
        self._set_callbacks(
            on_found, on_not_found,
            on_progress, on_finished
        )
        self.stop()

        self.search_thread = SongSearchThread(
            query=query,
            random_mode=False
        )
        self._connect_thread()
        self.search_thread.start()

    # ----------------------------
    # Play random song
    # ----------------------------
    def play_random(
        self,
        on_found=None, on_not_found=None,
        on_progress=None, on_finished=None
    ):
        self._set_callbacks(
            on_found, on_not_found,
            on_progress, on_finished
        )
        self.stop()

        self.search_thread = SongSearchThread(
            random_mode=True
        )
        self._connect_thread()
        self.search_thread.start()

    def _set_callbacks(
        self, on_found, on_not_found,
        on_progress, on_finished
    ):
        self._on_found_cb = on_found
        self._on_not_found_cb = on_not_found
        self._on_progress_cb = on_progress
        self._on_finished_cb = on_finished

    def _connect_thread(self):
        self.search_thread.song_found.connect(
            self._on_song_found
        )
        self.search_thread.song_not_found.connect(
            self._on_song_not_found
        )
        self.search_thread.search_progress.connect(
            self._on_search_progress
        )

    def _on_song_found(self, path, name):
        self.current_song = name
        self.is_playing = True
        self.player.setSource(
            QUrl.fromLocalFile(path)
        )
        self.player.play()
        clean_name = os.path.splitext(name)[0]
        if self._on_found_cb:
            self._on_found_cb(
                f"🎵 Now playing: {clean_name}"
            )

    def _on_song_not_found(self, query):
        self.is_playing = False
        if self._on_not_found_cb:
            if query == "random song":
                self._on_not_found_cb(
                    "Sorry, I could not find any "
                    "songs on your PC. Please add "
                    "some MP3 files to your Music "
                    "or Downloads folder!"
                )
            else:
                self._on_not_found_cb(
                    f"Sorry, I could not find "
                    f"'{query}' on your PC. "
                    f"Make sure the song is saved "
                    f"in Music, Downloads, Desktop, "
                    f"or D: drive."
                )

    def _on_search_progress(self, msg):
        if self._on_progress_cb:
            self._on_progress_cb(msg)

    def _on_state_changed(self, state):
        from PySide6.QtMultimedia import (
            QMediaPlayer
        )
        if state == QMediaPlayer.StoppedState:
            if self.is_playing:
                self.is_playing = False
                if self._on_finished_cb:
                    self._on_finished_cb()

    def _on_error(self, error, error_string):
        print(f"Media error: {error_string}")
        if self._on_not_found_cb:
            self._on_not_found_cb(
                "Could not play this file. "
                "Try MP3 format."
            )

    def pause(self):
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            return "Song paused."
        return "No song is currently playing."

    def resume(self):
        if not self.is_playing:
            self.player.play()
            self.is_playing = True
            return "Resuming song."
        return "Song is already playing."

    def stop(self):
        self.player.stop()
        self.is_playing = False
        self.current_song = None

    def get_current_song(self):
        if self.current_song:
            return os.path.splitext(
                self.current_song
            )[0]
        return None