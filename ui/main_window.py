from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal

from ui.title_bar import TitleBar
from ui.left_panel import LeftPanel
from ui.chat_panel import ChatPanel
from ui.bottom_bar import BottomBar
from ui.settings_panel import SettingsPanel

from modules.speech import SpeechRecognizer
from modules.tts import TTSEngine
from modules.commands import CommandProcessor
from modules.system_ctrl import SystemController
from modules.wake_word import WakeWordDetector
from modules.system_monitor import SystemMonitor
from modules.web_search import WebSearchEngine
from modules.music_player import MusicPlayer
from modules.reminder import ReminderManager
from modules.file_analyzer import FileAnalyzer
from database.db_manager import DatabaseManager


# ----------------------------
# Background worker thread
# Runs commands without blocking UI
# ----------------------------
class CommandWorker(QThread):
    result_ready = Signal(dict)

    def __init__(self, commands, text, parent=None):
        super().__init__(parent)
        self.commands = commands
        self.text = text

    def run(self):
        try:
            result = self.commands.process(self.text)
            self.result_ready.emit(result)
        except Exception as e:
            self.result_ready.emit({
                'action': 'response',
                'response': (
                    f"Sorry, something went wrong: {e}"
                )
            })


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Aria — Intelligent Virtual Assistant"
        )
        self.setMinimumSize(950, 620)
        self.resize(1100, 680)

        self._command_worker = None

        self.db = DatabaseManager()
        self.session_id = self.db.start_session()
        saved = self.db.get_setting('dark_mode', 'true')
        self.is_dark_mode = saved == 'true'

        self.speech = SpeechRecognizer()
        self.tts = TTSEngine()
        self.commands = CommandProcessor()
        self.system = SystemController()
        self.wake_word = WakeWordDetector()
        self.sys_monitor = SystemMonitor()
        self.web_search = WebSearchEngine()
        self.music = MusicPlayer()
        self.reminder = ReminderManager()
        self.reminder.reminder_triggered.connect(
            self.on_reminder_triggered
        )
        self.file_analyzer = FileAnalyzer()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.left_panel = LeftPanel(self)
        body_layout.addWidget(self.left_panel)

        self.chat_panel = ChatPanel(self)
        body_layout.addWidget(self.chat_panel)

        self.settings_panel = SettingsPanel(self)
        self.settings_panel.hide()
        self.settings_panel.settings_changed.connect(
            self.on_settings_changed
        )
        body_layout.addWidget(self.settings_panel)

        main_layout.addWidget(body)

        self.bottom_bar = BottomBar(self)
        main_layout.addWidget(self.bottom_bar)

        self.apply_full_theme()
        self.connect_modules()

        QTimer.singleShot(1000, self._start_monitor)
        QTimer.singleShot(500, self._startup_speak)
        QTimer.singleShot(100, self._check_brain_status)

    # ----------------------------
    # Brain Status
    # ----------------------------
    def _check_brain_status(self):
        if hasattr(self.commands, 'brain'):
            if self.commands.brain.is_loading():
                self.title_bar.set_status(
                    "Loading AI...", "#4FD1FF"
                )
                QTimer.singleShot(
                    2000, self._check_brain_ready
                )

    def _check_brain_ready(self):
        if hasattr(self.commands, 'brain'):
            if self.commands.brain.is_loading():
                QTimer.singleShot(
                    2000, self._check_brain_ready
                )
            else:
                self.title_bar.set_status(
                    "Active", "#3DDC97"
                )

    def _start_monitor(self):
        self.sys_monitor.start(
            on_update=self.on_system_update
        )

    def _startup_speak(self):
        self.left_panel.start_talking()
        self.tts.speak(
            "Hello! I am Aria, your intelligent "
            "virtual assistant. How can I help?",
            on_finish=self.left_panel.stop_talking
        )


    # ----------------------------
    # Connect Modules
    # ----------------------------
    def connect_modules(self):
        # mic button only — send/enter handled
        # inside chat_panel._dispatch → handle_command
        self.chat_panel.mic_btn.mousePressEvent = \
            lambda e: self.on_mic_clicked()

        self.bottom_bar.buttons[0].clicked.connect(
            lambda: self.chat_panel.add_aria_message(
                "Which app would you like to open? "
                "Type: open chrome"
            )
        )
        self.bottom_bar.buttons[1].clicked.connect(
            self._open_file_search
        )
        self.bottom_bar.buttons[2].clicked.connect(
            self.toggle_settings
        )
        self.bottom_bar.buttons[3].clicked.connect(
            self.bottom_bar.open_clipboard
        )
        self.bottom_bar.buttons[4].clicked.connect(
            self.bottom_bar.open_help
        )

    def _open_file_search(self):
        self.chat_panel.add_aria_message(
            "What file would you like to find? "
            "Type: find file resume"
        )
        self.chat_panel.text_input.setFocus()

    def toggle_settings(self):
        if self.settings_panel.isHidden():
            self.settings_panel.show()
        else:
            self.settings_panel.hide()

    def on_settings_changed(self, settings):
        dark = settings.get('dark_mode', True)
        self.is_dark_mode = dark
        self.db.save_setting(
            'dark_mode',
            'true' if dark else 'false'
        )
        self.apply_full_theme()
        if hasattr(self.commands, 'lang'):
            self.commands.lang.set_language(
                settings.get('language', 'English')
            )
        self.chat_panel.add_aria_message(
            "✅ Settings saved!"
        )

    # ----------------------------
    # Handle Command — THREADED
    # Grok/web search run in background
    # UI never freezes
    # ----------------------------
    def handle_command(self, text):
        self.title_bar.set_status(
            "Processing...", "#FFB84D"
        )
        self.chat_panel.show_typing()

        # Kill any previous worker
        if self._command_worker is not None:
            self._command_worker.quit()
            self._command_worker = None

        # Run command in background thread
        worker = CommandWorker(self.commands, text)
        worker.result_ready.connect(
            self._on_command_result
        )
        worker.finished.connect(
            lambda: self._cleanup_worker(worker)
        )
        self._command_worker = worker
        worker.start()

    def _cleanup_worker(self, worker):
        if self._command_worker is worker:
            self._command_worker = None

    def _on_command_result(self, result):
        self.chat_panel.hide_typing()

        response = result.get('response', '')
        action = result.get('action', '')

        self.db.log_command(
            command_text=result.get('text', ''),
            command_type=action,
            aria_response=response,
            status="success"
        )

        if action == 'music_play':
            self._play_song(
                result.get('song_name', '')
            )
            return
        if action == 'music_random':
            self._play_random_song()
            return
        if action == 'music_stop':
            self.music.stop()
            self.chat_panel.add_aria_message(
                "⏹ Song stopped."
            )
            self._speak("Song stopped.")
            return
        if action == 'music_pause':
            msg = self.music.pause()
            self.chat_panel.add_aria_message(
                f"⏸ {msg}"
            )
            self._speak(msg)
            return
        if action == 'music_resume':
            msg = self.music.resume()
            self.chat_panel.add_aria_message(
                f"▶ {msg}"
            )
            self._speak(msg)
            return
        if action == 'reminder':
            msg = self.reminder.parse_and_add(
                result.get('text', '')
            )
            if msg:
                self.chat_panel.add_aria_message(
                    f"⏰ {msg}"
                )
                self._speak(msg)
            else:
                self.chat_panel.add_aria_message(
                    "Try: remind me in 5 minutes "
                    "to drink water."
                )
            return
        if action == 'web_search':
            self._do_web_search(
                result.get('query', '')
            )
            return

        # Execute system action
        self.execute_action(action, '')

        # Show response
        if response:
            self.chat_panel.add_aria_message(response)
            self.left_panel.start_talking()
            self.tts.speak(
                # Strip ✦ tag for speech
                response.split('\n\n✦')[0],
                on_start=lambda: self.title_bar
                .set_status("Speaking...", "#4FD1FF"),
                on_finish=self._on_speak_finish
            )

        if action == 'exit':
            QTimer.singleShot(3000, self.close)

    def on_reminder_triggered(self, message):
        self.chat_panel.add_aria_message(
            f"🔔 {message}"
        )
        self._speak(message)

    def analyze_file(self, file_path):
        self.title_bar.set_status(
            "Analyzing...", "#4FD1FF"
        )
        self.file_analyzer.analyze(
            file_path,
            on_result=self._on_file_analyzed,
            on_error=self._on_file_error,
            on_progress=lambda m: self.title_bar
            .set_status(m[:30], "#4FD1FF")
        )

    def _on_file_analyzed(self, result):
        self.chat_panel.hide_typing()
        self.title_bar.set_status(
            "Active", "#3DDC97"
        )
        self.chat_panel.add_aria_message(result)
        self._speak(
            "I have analyzed the file."
        )

    def _on_file_error(self, error):
        self.chat_panel.hide_typing()
        self.title_bar.set_status(
            "Active", "#3DDC97"
        )
        self.chat_panel.add_aria_message(error)

    def _play_song(self, song_name):
        self.chat_panel.add_aria_message(
            f"🔍 Searching for '{song_name}'..."
        )
        self.title_bar.set_status(
            "Searching...", "#4FD1FF"
        )
        self.music.play_song(
            query=song_name,
            on_found=self._on_song_found,
            on_not_found=self._on_song_not_found,
            on_progress=self._on_song_progress,
            on_finished=self._on_song_finished
        )

    def _play_random_song(self):
        self.chat_panel.add_aria_message(
            "🎲 Picking a random song..."
        )
        self.title_bar.set_status(
            "Searching...", "#4FD1FF"
        )
        self.music.play_random(
            on_found=self._on_song_found,
            on_not_found=self._on_song_not_found,
            on_progress=self._on_song_progress,
            on_finished=self._on_song_finished
        )

    def _on_song_found(self, message):
        self.title_bar.set_status(
            "🎵 Playing", "#3DDC97"
        )
        self.chat_panel.add_aria_message(message)
        self._speak(message)

    def _on_song_not_found(self, message):
        self.title_bar.set_status(
            "Active", "#3DDC97"
        )
        self.chat_panel.add_aria_message(message)
        self._speak(
            "Sorry, I could not find that song."
        )

    def _on_song_progress(self, message):
        self.title_bar.set_status(
            message[:30], "#4FD1FF"
        )

    def _on_song_finished(self):
        self.title_bar.set_status(
            "Active", "#3DDC97"
        )
        self.chat_panel.add_aria_message(
            "✅ Song finished."
        )

    def _do_web_search(self, query):
        self.chat_panel.add_aria_message(
            f"🔍 Searching for '{query}'..."
        )
        self.chat_panel.show_typing()
        self.title_bar.set_status(
            "Searching...", "#4FD1FF"
        )
        self.web_search.search(
            query=query,
            on_result=self._on_search_result,
            on_error=self._on_search_error
        )

    def _on_search_result(self, result):
        self.chat_panel.hide_typing()
        self.title_bar.set_status(
            "Active", "#3DDC97"
        )
        self.chat_panel.add_aria_message(result)
        short = result[:200] + "..." \
            if len(result) > 200 else result
        self.left_panel.start_talking()
        self.tts.speak(
            short,
            on_start=lambda: self.title_bar
            .set_status("Speaking...", "#4FD1FF"),
            on_finish=self._on_speak_finish
        )

    def _on_search_error(self, error):
        self.chat_panel.hide_typing()
        self.title_bar.set_status(
            "Active", "#3DDC97"
        )
        self.chat_panel.add_aria_message(error)

    def _speak(self, text):
        self.left_panel.start_talking()
        self.tts.speak(
            text.split('\n\n✦')[0],
            on_start=lambda: self.title_bar
            .set_status("Speaking...", "#4FD1FF"),
            on_finish=self._on_speak_finish
        )

    def _on_speak_finish(self):
        self.left_panel.stop_talking()
        self.title_bar.set_status(
            "Active", "#3DDC97"
        )

    def execute_action(self, action, text):
        action_map = {
            'volume_up': self.system.volume_up,
            'volume_down': self.system.volume_down,
            'volume_mute': self.system.volume_mute,

            'wifi_on': self.system.wifi_on,
            'wifi_off': self.system.wifi_off,

            'bluetooth_on': self.system.bluetooth_on,
            'bluetooth_off': self.system.bluetooth_off,

            'brightness_up': self.system.brightness_up,
            'brightness_down': self.system.brightness_down,

            'screenshot': self.system.take_screenshot,
            'battery': self.system.get_battery,

            'open_settings': self.system.open_settings,
            'empty_recycle_bin': self.system.empty_recycle_bin,
            'open_powershell': self.system.open_powershell,
}
        if action in action_map:
            result = action_map[action]()
            self.chat_panel.add_aria_message(result)
        elif action == 'lock':
            self.system.lock_screen()
        elif action == 'sleep':
            self.system.sleep()
        elif action == 'shutdown':
            self.system.shutdown()
        elif action == 'restart':
            self.system.restart()
        elif action == "open_powershell":
            self.system.open_powershell()
        elif action == "empty_recycle_bin":
            self.system.empty_recycle_bin()
        elif action == "settings":
            self.system.open_settings()

    # ----------------------------
    # Voice
    # ----------------------------
    def on_mic_clicked(self):
        self.chat_panel.mic_overlay.show_overlay()
        if not self.left_panel.is_listening:
            self.left_panel.toggle_listening()
        self.title_bar.set_status(
            "Say 'Hey Aria'...", "#FFB84D"
        )
        self.wake_word.start_once(
            on_detected=self.on_wake_word_detected,
            on_error=lambda e: print(f"Wake: {e}")
        )

    def on_wake_word_detected(self):
        self.title_bar.set_status(
            "Listening...", "#4FD1FF"
        )
        self.chat_panel.add_aria_message(
            "Yes? I am listening! 😊"
        )
        self.left_panel.start_talking()
        self.tts.speak(
            "Yes, I am listening!",
            on_finish=self._after_wake_response
        )

    def _after_wake_response(self):
        self.left_panel.stop_talking()
        self.speech.start_listening(
            on_text=self.on_voice_received,
            on_start=self.on_listen_start,
            on_stop=self.on_listen_stop,
            on_error=self.on_voice_error
        )

    def on_voice_received(self, text):
        self.chat_panel.stop_overlay()
        if self.left_panel.is_listening:
            self.left_panel.toggle_listening()
        self.speech.stop_listening()
        self.chat_panel.add_user_message(text)
        self.handle_command(text)

    def on_listen_start(self):
        self.title_bar.set_status(
            "Listening...", "#4FD1FF"
        )
        self.left_panel.face.set_listening(True)

    def on_listen_stop(self):
        self.title_bar.set_status(
            "Active", "#3DDC97"
        )
        self.left_panel.face.set_listening(False)

    def on_voice_error(self, error):
        self.chat_panel.stop_overlay()
        if self.left_panel.is_listening:
            self.left_panel.toggle_listening()
        self.speech.stop_listening()
        self.chat_panel.hide_typing()
        if error and "did not hear" \
                not in error.lower():
            self.chat_panel.add_aria_message(error)
        self.title_bar.set_status(
            "Active", "#3DDC97"
        )

    def on_system_update(self, stats):
        self.left_panel.monitor.update_stats(stats)
        if stats['cpu'] >= 90:
            self.title_bar.set_status(
                "CPU High!", "#FF5F57"
            )

    # ----------------------------
    # Theme
    # ----------------------------
    def apply_full_theme(self):
        if self.is_dark_mode:
            self._apply_cyan_theme()
        else:
            self._apply_light_theme()

    def _apply_cyan_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0B1020;
                color: #EAF2FF;
                font-family: 'Outfit';
                font-size: 13px;
            }
            QScrollArea {
                border: none;
                background-color: #0B1020;
            }
            QScrollBar:vertical {
                width: 4px;
                background: #0B1020;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #2A3555;
                border-radius: 2px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QLineEdit {
                background-color: #12182B;
                border: 1px solid #2A3555;
                border-radius: 12px;
                padding: 8px 16px;
                color: #EAF2FF;
            }
            QLineEdit:focus {
                border-color: #4FD1FF;
            }
        """)
        self.title_bar.setStyleSheet("""
            TitleBar {
                background-color: #0B1020;
                border-bottom: 1px solid #2A3555;
            }
        """)
        self.title_bar.theme_btn.setText("◑ Theme")
        self.title_bar.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #12182B;
                border: 1px solid #2A3555;
                border-radius: 15px;
                font-family: 'Outfit';
                font-size: 11px;
                color: #4FD1FF;
                padding: 0 14px;
            }
            QPushButton:hover {
                background-color: #1A2238;
                border-color: #4FD1FF;
            }
        """)
        self.left_panel.setStyleSheet("""
            LeftPanel {
                background-color: #0D1425;
                border-right: 1px solid #2A3555;
            }
        """)
        self.left_panel.update_theme(True)
        self.chat_panel.chat_container\
            .setStyleSheet(
            "background-color: #0B1020;"
        )
        self.chat_panel.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0B1020;
            }
            QScrollBar:vertical {
                width: 4px; background: #0B1020;
            }
            QScrollBar::handle:vertical {
                background: #2A3555;
                border-radius: 2px;
            }
        """)
        self.chat_panel.text_input.setStyleSheet("""
            QLineEdit {
                background-color: #12182B;
                border: 1px solid #2A3555;
                border-radius: 12px;
                padding: 8px 18px;
                font-family: 'Outfit';
                font-size: 13px;
                color: #EAF2FF;
            }
            QLineEdit:focus {
                border-color: #4FD1FF;
                background-color: #1A2238;
            }
        """)
        self.chat_panel.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4FD1FF;
                border: none; border-radius: 12px;
                font-family: 'Outfit';
                font-size: 13px; font-weight: 700;
                color: #0B1020; padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #38B6E8;
            }
        """)
        self.bottom_bar.setStyleSheet("""
            BottomBar {
                background-color: #0D1425;
                border-top: 1px solid #2A3555;
            }
        """)
        for btn in self.bottom_bar.buttons:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #12182B;
                    border: 1px solid #2A3555;
                    border-radius: 10px;
                    font-family: 'Outfit';
                    font-size: 12px;
                    color: #93A4C3;
                    padding: 0 14px;
                }
                QPushButton:hover {
                    background-color: #1A2238;
                    border-color: #4FD1FF;
                    color: #4FD1FF;
                }
                QPushButton:pressed {
                    background-color: #0D1425;
                }
            """)

    def _apply_light_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F0F4FF;
                color: #1A2238;
                font-family: 'Outfit';
                font-size: 13px;
            }
            QScrollArea {
                border: none;
                background-color: #F0F4FF;
            }
            QScrollBar:vertical {
                width: 4px;
                background: #F0F4FF;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #C5D2F0;
                border-radius: 2px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #C5D2F0;
                border-radius: 12px;
                padding: 8px 16px;
                color: #1A2238;
            }
            QLineEdit:focus {
                border-color: #4FD1FF;
            }
        """)
        self.title_bar.setStyleSheet("""
            TitleBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #C5D2F0;
            }
        """)
        self.title_bar.theme_btn.setText("☀ Light")
        self.title_bar.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #EEF2FF;
                border: 1px solid #C5D2F0;
                border-radius: 15px;
                font-family: 'Outfit';
                font-size: 11px;
                color: #4169E1;
                padding: 0 14px;
            }
            QPushButton:hover {
                border-color: #4FD1FF;
                color: #0099CC;
            }
        """)
        self.left_panel.setStyleSheet("""
            LeftPanel {
                background-color: #F8FAFF;
                border-right: 1px solid #C5D2F0;
            }
        """)
        self.left_panel.update_theme(False)
        self.chat_panel.chat_container\
            .setStyleSheet(
            "background-color: #F0F4FF;"
        )
        self.chat_panel.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F0F4FF;
            }
            QScrollBar:vertical {
                width: 4px; background: #F0F4FF;
            }
            QScrollBar::handle:vertical {
                background: #C5D2F0;
                border-radius: 2px;
            }
        """)
        self.chat_panel.text_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #C5D2F0;
                border-radius: 12px;
                padding: 8px 18px;
                font-family: 'Outfit';
                font-size: 13px;
                color: #1A2238;
            }
            QLineEdit:focus {
                border-color: #4FD1FF;
            }
        """)
        self.chat_panel.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4FD1FF;
                border: none; border-radius: 12px;
                font-family: 'Outfit';
                font-size: 13px; font-weight: 700;
                color: #0B1020; padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #38B6E8;
            }
        """)
        self.bottom_bar.setStyleSheet("""
            BottomBar {
                background-color: #FFFFFF;
                border-top: 1px solid #C5D2F0;
            }
        """)
        for btn in self.bottom_bar.buttons:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #EEF2FF;
                    border: 1px solid #C5D2F0;
                    border-radius: 10px;
                    font-family: 'Outfit';
                    font-size: 12px;
                    color: #4169E1;
                    padding: 0 14px;
                }
                QPushButton:hover {
                    background-color: #DDEEFF;
                    border-color: #4FD1FF;
                    color: #0099CC;
                }
            """)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.db.save_setting(
            'dark_mode',
            'true' if self.is_dark_mode else 'false'
        )
        self.apply_full_theme()

    def closeEvent(self, event):
        try:
            self.left_panel.stop_all()
        except Exception:
            pass
        try:
            self.speech.stop_listening()
        except Exception:
            pass
        try:
            self.tts.stop()
        except Exception:
            pass
        try:
            self.wake_word.stop()
        except Exception:
            pass
        try:
            self.sys_monitor.stop()
        except Exception:
            pass
        try:
            self.web_search.stop()
        except Exception:
            pass
        try:
            self.music.stop()
        except Exception:
            pass
        try:
            self.db.end_session(self.session_id)
            self.db.close()
        except Exception:
            pass
        event.accept()