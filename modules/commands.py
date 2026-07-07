import os
import datetime
import webbrowser
import subprocess
import importlib.util


class CommandProcessor:
    def __init__(self):
        USER = os.environ.get('USERNAME', '')
        APPDATA = os.environ.get('APPDATA', '')

        self.apps = {
            'chrome': [r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'],
            'google chrome': [r'C:\Program Files\Google\Chrome\Application\chrome.exe'],
            'firefox': [r'C:\Program Files\Mozilla Firefox\firefox.exe'],
            'edge': [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'],
            'notepad': [r'C:\Windows\System32\notepad.exe'],
            'calculator': [r'C:\Windows\System32\calc.exe'],
            'paint': [r'C:\Windows\System32\mspaint.exe'],
            'wordpad': [r'C:\Program Files\Windows NT\Accessories\wordpad.exe'],
            'task manager': [r'C:\Windows\System32\Taskmgr.exe'],
            'file explorer': [r'C:\Windows\explorer.exe'],
            'explorer': [r'C:\Windows\explorer.exe'],
            'control panel': [r'C:\Windows\System32\control.exe'],
            'cmd': [r'C:\Windows\System32\cmd.exe'],
            'command prompt': [r'C:\Windows\System32\cmd.exe'],
            'powershell': [r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'],
            'snipping tool': [r'C:\Windows\System32\SnippingTool.exe'],
            'word': [r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE', r'C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE'],
            'excel': [r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE', r'C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE'],
            'powerpoint': [r'C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE', r'C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE'],
            'vlc': [r'C:\Program Files\VideoLAN\VLC\vlc.exe', r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe'],
            'spotify': [os.path.join(APPDATA, r'Spotify\Spotify.exe')],
            'vs code': [rf'C:\Users\{USER}\AppData\Local\Programs\Microsoft VS Code\Code.exe'],
            'visual studio code': [rf'C:\Users\{USER}\AppData\Local\Programs\Microsoft VS Code\Code.exe'],
        }

        self.folders = {
            'local disk': r'C:\\', 'c drive': r'C:\\', 'c disk': r'C:\\',
            'd drive': r'D:\\', 'e drive': r'E:\\', 'f drive': r'F:\\',
            'downloads': os.path.join(os.path.expanduser('~'), 'Downloads'),
            'documents': os.path.join(os.path.expanduser('~'), 'Documents'),
            'desktop': os.path.join(os.path.expanduser('~'), 'Desktop'),
            'pictures': os.path.join(os.path.expanduser('~'), 'Pictures'),
            'music': os.path.join(os.path.expanduser('~'), 'Music'),
            'videos': os.path.join(os.path.expanduser('~'), 'Videos'),
        }

        # --- Keywords ---
        self.open_keywords = ['open', 'launch', 'start', 'run', 'execute']
        self.close_keywords = ['close', 'quit', 'kill', 'end', 'terminate']
        self.volume_keywords = ['volume', 'sound', 'audio']
        self.time_keywords = ['time', 'what time', 'current time']
        self.date_keywords = ['date', 'what date', 'today', "what's today", 'what day']
        self.shutdown_keywords = ['shutdown', 'shut down', 'turn off computer', 'power off']
        self.restart_keywords = ['restart', 'reboot', 'restart computer']
        self.sleep_keywords = ['sleep mode', 'hibernate', 'put to sleep']
        self.lock_keywords = ['lock screen', 'lock computer', 'lock pc', 'lock the screen']
        self.screenshot_keywords = ['screenshot', 'screen capture', 'capture screen', 'take screenshot']
        self.battery_keywords = ['battery', 'battery status', 'battery level', 'power level', 'battery detail']
        self.settings_keywords = ['open settings','windows settings','system settings','settings']
        self.powershell_keywords = ['open powershell','launch powershell','start powershell','powershell']
        self.recycle_bin_keywords = ['empty recycle bin','clear recycle bin','delete recycle bin','clean recycle bin']
        self.exit_keywords = ['exit aria', 'bye aria', 'goodbye aria', 'close aria', 'quit aria']
        self.weather_keywords = ['weather', 'temperature', 'forecast']
        self.youtube_keywords = ['youtube', 'play on youtube', 'search youtube', 'open youtube']
        self.music_play_keywords = ['play song', 'play the song', 'listen to', 'put on', 'play me']
        self.music_play_random_keywords = ['play a song', 'play something', 'play any song', 'play random', 'shuffle', 'play anything', 'surprise me']
        self.music_stop_keywords = ['stop the song', 'stop song', 'stop the music', 'stop music', 'stop playing', 'end the song', 'end music', 'turn off music']
        self.music_pause_keywords = ['pause song', 'pause the song', 'pause music', 'pause the music']
        self.music_resume_keywords = ['resume song', 'resume music', 'continue playing', 'unpause', 'play again']
        self.reminder_keywords = ['remind me', 'set reminder', 'set a reminder', 'reminder', 'remind me in', 'alarm']
        self.camera_keywords = ['open camera', 'camera app', 'webcam', 'take photo', 'take picture']
        self.clipboard_keywords = ['open clipboard', 'show clipboard', 'clipboard history']

        # --- Open file by name ---
        self.open_file_keywords = [
            'open the document', 'open document',
            'open the file', 'open file named',
            'open the pdf', 'open the image',
            'open the photo', 'open the video',
            'open the word', 'open the excel',
            'open the presentation', 'open the ppt',
            'show me the file', 'show the document',
            'launch the file', 'find and open',
            'open the folder named',
        ]

        # --- New system access keywords ---
        self.process_keywords = ['running processes', 'list processes', 'show processes', 'what is running', 'task list', 'running apps']
        self.kill_process_keywords = ['kill process', 'end process', 'stop process', 'force close', 'kill app', 'terminate process']
        self.system_info_keywords = ['system info', 'system information', 'pc info', 'computer info', 'about my pc', 'hardware info', 'specs', 'my pc specs']
        self.disk_keywords = ['disk usage', 'disk space', 'storage info', 'hard drive space', 'how much space', 'free space', 'storage space']
        self.network_keywords = ['network info', 'network status', 'ip address', 'my ip', 'wifi info', 'internet info', 'connection info']
        self.internet_keywords = ['check internet', 'internet connection', 'am i connected', 'is internet working', 'internet status']
        self.installed_apps_keywords = ['installed apps', 'installed programs', 'list apps', 'what apps', 'installed software']
        self.startup_keywords = ['startup programs', 'startup apps', 'what starts with windows', 'autostart programs']
        self.recent_files_keywords = ['recent files', 'recently opened', 'recent documents', 'last opened files']
        self.env_keywords = ['environment variables', 'env variables', 'system variables']
        self.read_file_keywords = ['read file', 'open file', 'show file contents', 'read the file', 'show me file']
        self.file_info_keywords = ['file info', 'file details', 'about file', 'file properties', 'tell me about file']
        self.clipboard_read_keywords = ['read clipboard', 'show clipboard content', 'what is in clipboard', 'paste from clipboard']
        self.close_all_keywords = ['close all apps','close all programs','close everything','kill all apps','terminate all apps','shutdown apps']
        self.create_folder_keywords = ['create folder','make folder','new folder','create directory','make a folder']
        self.create_file_keywords = ['create file','make file','new file','create text file','make a file']
        self.run_cmd_keywords = ['run command', 'execute command', 'run cmd', 'terminal command']
        self.file_search_keywords = ['search file', 'find file', 'search for file', 'find my file','look for file', 'where is my file', 'find document', 'search document','locate file', 'find folder', 'search my pc', 'find on my pc','search files', 'find files',]
        self.web_search_keywords = ['search', 'find', 'look up', 'who is', 'who was', 'who are','what is', 'what was', 'what are', 'where is', 'where was','when is', 'when was', 'when did', 'how is', 'how does', 'how do','why is', 'why does', 'why did', 'tell me about', 'information about','info about', 'details about', 'explain', 'describe', 'latest news','news about', 'definition of', 'meaning of',]
        self.wifi_on_keywords = ['turn on wifi','enable wifi','wifi on']
        self.wifi_off_keywords = ['turn off wifi','disable wifi','wifi off']
        self.bluetooth_on_keywords = ['turn on bluetooth','enable bluetooth','bluetooth on']
        self.bluetooth_off_keywords = ['turn off bluetooth','disable bluetooth','bluetooth off']
        self.brightness_up_keywords = ['brightness up','increase brightness','make screen brighter']
        self.brightness_down_keywords = ['brightness down','decrease brightness','reduce brightness']
        self.recycle_open_keywords = ['open recycle bin','show recycle bin'
]
        # --- Load System Access ---
        try:
            spec_sa = importlib.util.spec_from_file_location(
                "system_access",
                os.path.join(os.path.dirname(__file__), "system_access.py")
            )
            mod_sa = importlib.util.module_from_spec(spec_sa)
            spec_sa.loader.exec_module(mod_sa)
            self.sys_access = mod_sa.SystemAccess()
            self.use_sys_access = True
            print("System Access: Full PC access connected!")
        except Exception as e:
            self.use_sys_access = False
            print(f"System Access not loaded: {e}")

        # --- Load Smart Brain ---
        try:
            spec = importlib.util.spec_from_file_location(
                "smart_brain",
                os.path.join(os.path.dirname(__file__), "smart_brain.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.brain = module.SmartBrain()
            self.use_brain = True
            print("Smart Brain connected!")
        except Exception as e:
            self.use_brain = False
            print(f"Smart Brain not loaded: {e}")

        # --- Load Language Support ---
        try:
            spec2 = importlib.util.spec_from_file_location(
                "language_support",
                os.path.join(os.path.dirname(__file__), "language_support.py")
            )
            module2 = importlib.util.module_from_spec(spec2)
            spec2.loader.exec_module(module2)
            self.lang = module2.LanguageSupport()
            self.use_lang = True
            print("Language Support connected!")
        except Exception as e:
            self.use_lang = False
            print(f"Language Support not loaded: {e}")

        # --- Load Offline Brain ---
        try:
            spec3 = importlib.util.spec_from_file_location(
                "offline_brain",
                os.path.join(os.path.dirname(__file__), "offline_brain.py")
            )
            module3 = importlib.util.module_from_spec(spec3)
            spec3.loader.exec_module(module3)
            self.offline_brain = module3.OfflineBrain()
            self.use_offline = True
            print("Offline Brain connected!")
        except Exception as e:
            self.use_offline = False
            print(f"Offline Brain not loaded: {e}")


    def process(self, text):
        text_original = text

        if self.use_lang:
            text = self.lang.translate_to_english(text)

        text_lower = text.lower().strip()

        # --- Exit ---
        if any(k in text_lower for k in self.exit_keywords):
            return {'action': 'exit', 'response': "Goodbye! Shutting down Aria now."}

        # --- Time / Date ---
        if any(k in text_lower for k in self.time_keywords):
            return self.handle_time()
        if any(k in text_lower for k in self.date_keywords):
            return self.handle_date()

        # --- System Commands ---
        if any(k in text_lower for k in self.settings_keywords):
            return self.handle_settings()
        if any(k in text_lower for k in self.powershell_keywords):
            return {'action': 'open_powershell','response': 'Opening PowerShell.'}

        if any(k in text_lower for k in self.recycle_bin_keywords):
            return {'action': 'empty_recycle_bin','response': 'Emptying Recycle Bin.'}
        if any(k in text_lower for k in self.shutdown_keywords):
            return {'action': 'shutdown', 'response': "Shutting down in 10 seconds."}
        if any(k in text_lower for k in self.restart_keywords):
            return {'action': 'restart', 'response': "Restarting in 10 seconds."}
        if any(k in text_lower for k in self.sleep_keywords):
            return {'action': 'sleep', 'response': "Putting system to sleep."}
        if any(k in text_lower for k in self.lock_keywords):
            return {'action': 'lock', 'response': "Locking screen now."}
        if any(k in text_lower for k in self.screenshot_keywords):
            return {'action': 'screenshot', 'response': "Taking a screenshot!"}
        if any(k in text_lower for k in self.battery_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.get_battery_detail()}
            return {'action': 'battery', 'response': "Checking battery status."}
        # --- WiFi / Bluetooth / Brightness ---

        if any(k in text_lower for k in self.wifi_on_keywords):
            return {
                'action': 'wifi_on',
                'response': 'Turning WiFi on.'
    }

        if any(k in text_lower for k in self.wifi_off_keywords):
            return {
                'action': 'wifi_off',
                'response': 'Turning WiFi off.'
    }

        if any(k in text_lower for k in self.bluetooth_on_keywords):
            return {
                'action': 'bluetooth_on',
                'response': 'Turning Bluetooth on.'
    }

        if any(k in text_lower for k in self.bluetooth_off_keywords):
            return {
                'action': 'bluetooth_off',
                'response': 'Turning Bluetooth off.'
    }

        if any(k in text_lower for k in self.brightness_up_keywords):
            return {
                'action': 'brightness_up',
                'response': 'Increasing brightness.'
    }

        if any(k in text_lower for k in self.brightness_down_keywords):
            return {
                'action': 'brightness_down',
                'response': 'Decreasing brightness.'
    }

        # --- Weather / Volume / YouTube ---
        if any(k in text_lower for k in self.weather_keywords):
            return self.handle_weather(text_lower)
        if any(k in text_lower for k in self.volume_keywords):
            return self.handle_volume(text_lower)
        if any(k in text_lower for k in self.youtube_keywords):
            return self.handle_youtube(text_lower)

        # --- Camera / Clipboard ---
        if any(k in text_lower for k in self.camera_keywords):
            return self.handle_camera()
        if any(k in text_lower for k in self.clipboard_keywords):
            return self.handle_clipboard()

        # --- Close all running apps ---
        if any(k in text_lower for k in getattr(self, "close_all_keywords", [])):
            return self.handle_close_all()

        # --- Create folder ---
        if any(k in text_lower for k in getattr(self, "create_folder_keywords", [])):
            name = self._extract_create_name(
                text_lower, self.create_folder_keywords
            )
            return self.handle_create_folder(name)

        # --- Create file ---
        if any(k in text_lower for k in getattr(self, "create_file_keywords", [])):
            name = self._extract_create_name(
                text_lower, self.create_file_keywords
            )
            return self.handle_create_file(name)

        # --- Open file by name ---
        if any(k in text_lower for k in self.open_file_keywords):
            name = self._extract_file_name(text_lower)
            if name and self.use_sys_access:
                result = self.sys_access.open_file_by_name(name)
                return {
                    'action': 'file_opened'
                    if result.get('opened')
                    else 'response',
                    'response': result['response']
                }
            return {
                'action': 'response',
                'response': (
                    "Which file should I open? "
                    "Tell me the name."
                )
            }

        # --- Reminders ---
        if any(k in text_lower for k in self.reminder_keywords):
            return {'action': 'reminder', 'text': text_original, 'response': "Setting your reminder!"}

        # --- Music ---
        if any(k in text_lower for k in self.music_stop_keywords):
            return {'action': 'music_stop', 'response': "Stopping the song."}
        if any(k in text_lower for k in self.music_pause_keywords):
            return {'action': 'music_pause', 'response': "Pausing the song."}
        if any(k in text_lower for k in self.music_resume_keywords):
            return {'action': 'music_resume', 'response': "Resuming the song."}
        if any(k in text_lower for k in self.music_play_random_keywords):
            song = self._extract_song_name(text_lower)
            if not song:
                return {'action': 'music_random', 'response': "Playing a random song!"}
        if any(k in text_lower for k in self.music_play_keywords) or text_lower.startswith('play '):
            song_name = self._extract_song_name(text_lower)
            if song_name:
                return {'action': 'music_play', 'song_name': song_name, 'response': f"Searching for {song_name}..."}
            return {'action': 'music_random', 'response': "Playing a random song from your PC!"}

        # --- New Full PC Access Commands ---
        if any(k in text_lower for k in self.process_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.list_processes()}
            return {'action': 'response', 'response': "System access not available."}

        if any(k in text_lower for k in self.kill_process_keywords):
            name = self._extract_after(text_lower, self.kill_process_keywords)
            if name and self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.kill_process(name)}
            return {'action': 'response', 'response': "Which process should I kill?"}

        if any(k in text_lower for k in self.system_info_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.get_full_system_info()}
            return {'action': 'response', 'response': "System access not available."}

        if any(k in text_lower for k in self.disk_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.get_disk_usage()}
            return {'action': 'response', 'response': "Disk info not available."}

        if any(k in text_lower for k in self.network_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.get_network_info()}
            return {'action': 'response', 'response': "Network info not available."}

        if any(k in text_lower for k in self.internet_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.check_internet()}
            return {'action': 'response', 'response': "Cannot check internet."}

        if any(k in text_lower for k in self.installed_apps_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.get_installed_apps()}
            return {'action': 'response', 'response': "Cannot list apps."}

        if any(k in text_lower for k in self.startup_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.get_startup_programs()}
            return {'action': 'response', 'response': "Cannot list startup programs."}

        if any(k in text_lower for k in self.recent_files_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.get_recent_files()}
            return {'action': 'response', 'response': "Cannot get recent files."}

        if any(k in text_lower for k in self.env_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.list_env_variables()}
            return {'action': 'response', 'response': "Cannot access environment variables."}

        if any(k in text_lower for k in self.clipboard_read_keywords):
            if self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.get_clipboard()}
            return {'action': 'response', 'response': "Cannot read clipboard."}

        if any(k in text_lower for k in self.read_file_keywords):
            path = self._extract_after(text_lower, self.read_file_keywords)
            if path and self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.read_file(path)}
            return {'action': 'response', 'response': "Which file should I read? Provide the full path."}

        if any(k in text_lower for k in self.file_info_keywords):
            path = self._extract_after(text_lower, self.file_info_keywords)
            if path and self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.get_file_info(path)}
            return {'action': 'response', 'response': "Which file? Provide the full path."}

        if any(k in text_lower for k in self.run_cmd_keywords):
            cmd = self._extract_after(text_lower, self.run_cmd_keywords)
            if cmd and self.use_sys_access:
                return {'action': 'response', 'response': self.sys_access.run_command(cmd)}
            return {'action': 'response', 'response': "Which command should I run?"}



        # --- Folders ---
        for folder_name, folder_path in self.folders.items():
            if folder_name in text_lower:
                return self.handle_open_folder(folder_name, folder_path)

        # --- Open / Close Apps ---
        if any(k in text_lower for k in self.open_keywords):
            # Check if multiple apps mentioned
            if any(
                sep in text_lower
                for sep in [' and ', ', ', ' also ']
            ):
                return self.handle_open_multiple(
                    text_lower
                )
            return self.handle_open_app(text_lower)
        if any(k in text_lower for k in self.close_keywords):
            return self.handle_close(text_lower)

        # --- File Search ---
        if any(k in text_lower for k in self.file_search_keywords):
            return self.handle_file_search(text_lower)

        # --- Offline Brain (personal/emotional) ---
        if self.use_offline:
            offline_response = (
                self.offline_brain
                .get_response(text_lower)
            )
            if offline_response:
                return {
                    'action': 'response',
                    'response': offline_response
                }

        # --- Smart Brain (intent matching) ---
        if self.use_brain:
            brain_response = (
                self.brain.get_response(text_lower)
            )
            if brain_response:
                return {
                    'action': 'response',
                    'response': brain_response
                }

        # --- Web Search last resort ---
        if any(
            k in text_lower
            for k in self.web_search_keywords
        ):
            query = self._extract_search_query(
                text_lower
            )
            return {
                'action': 'web_search',
                'query': query,
                'response': (
                    f"Searching for '{query}'..."
                )
            }

        if len(text_lower.split()) >= 2:
            return {
                'action': 'web_search',
                'query': text_original,
                'response': (
                    f"Searching for "
                    f"'{text_original}'..."
                )
            }

        return {
            'action': 'unknown',
            'response': (
                "I did not understand. "
                "Click Help to see commands."
            )
        }

    def _extract_after(self, text, keywords):
        """Extract text after a keyword."""
        for k in sorted(keywords, key=len, reverse=True):
            if k in text:
                after = text.split(k, 1)[-1].strip()
                if after:
                    return after
        return None

    def handle_open_multiple(self, text):
        '''Open multiple apps from one command.
        e.g. open chrome, youtube and vlc'''
        import re
        # Remove open keywords
        cleaned = text
        for k in self.open_keywords:
            cleaned = cleaned.replace(k, ' ')

        # Split by separators
        parts = re.split(
            r',| and | also | then | with |&',
            cleaned
        )
        parts = [p.strip() for p in parts if p.strip()]

        opened = []
        failed = []

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check website
            website_keywords = [
                '.com', '.net', '.org', '.pk',
                '.edu', '.io', 'www.', 'youtube',
                'google', 'facebook', 'instagram',
                'twitter', 'github', 'linkedin',
            ]

            # YouTube special case
            if 'youtube' in part:
                import webbrowser
                webbrowser.open("https://www.youtube.com")
                opened.append("YouTube")
                continue

            # Google special case
            if 'google' in part and '.com' not in part:
                import webbrowser
                webbrowser.open("https://www.google.com")
                opened.append("Google")
                continue

            # Website
            if any(w in part for w in website_keywords):
                url = part if part.startswith('http')                     else 'https://' + part
                import webbrowser
                webbrowser.open(url)
                opened.append(part)
                continue

            # Known apps
            found = False
            for key, paths in self.apps.items():
                if key in part or part in key:
                    import os, subprocess
                    for path in paths:
                        if os.path.exists(path):
                            try:
                                subprocess.Popen([path])
                                opened.append(key)
                                found = True
                                break
                            except Exception:
                                pass
                    if found:
                        break

            if not found and part not in [
                'app', '', 'application'
            ]:
                failed.append(part)

        if opened:
            names = ', '.join(opened)
            response = f"✅ Opening {names}!"
            if failed:
                response += (
                    f"\n⚠ Could not find: "
                    f"{', '.join(failed)}"
                )
            return {
                'action': 'app_opened',
                'response': response
            }
        return {
            'action': 'response',
            'response': (
                "I could not find those apps. "
                "Check the names and try again."
            )
        }

    def handle_close_all(self):
        '''Close all user-visible running apps.'''
        import psutil
        # Apps to never kill — system critical
        protected = {
            'explorer.exe', 'svchost.exe',
            'system', 'registry', 'smss.exe',
            'csrss.exe', 'wininit.exe',
            'services.exe', 'lsass.exe',
            'winlogon.exe', 'dwm.exe',
            'taskhostw.exe', 'runtimebroker.exe',
            'searchindexer.exe', 'spoolsv.exe',
            'aria.exe', 'python.exe',
            'pythonw.exe', 'cmd.exe',
            'powershell.exe', 'windowsterminal.exe',
            'conhost.exe', 'audiodg.exe',
        }
        closed = []
        failed = []
        try:
            for proc in psutil.process_iter(
                ['pid', 'name']
            ):
                try:
                    name = proc.info['name'].lower()
                    if name in protected:
                        continue
                    if proc.info['pid'] == 0:
                        continue
                    proc.kill()
                    closed.append(
                        proc.info['name']
                    )
                except Exception:
                    pass

            if closed:
                unique = list(set(closed))[:8]
                names = ', '.join(unique)
                extra = (
                    f' and {len(closed)-8} more'
                    if len(closed) > 8 else ''
                )
                return {
                    'action': 'response',
                    'response': (
                        f"✅ Closed {len(closed)} apps: "
                        f"{names}{extra}"
                    )
                }
            return {
                'action': 'response',
                'response': "No apps were running to close."
            }
        except Exception as e:
            return {
                'action': 'error',
                'response': f"Could not close apps: {e}"
            }

    def handle_create_folder(self, name):
        '''Create a new folder on Desktop.'''
        import os
        if not name or len(name.strip()) < 1:
            return {
                'action': 'response',
                'response': (
                    "What should I name the folder? "
                    "Say: create folder MyProject"
                )
            }
        # Clean name — remove invalid chars
        import re
        clean = re.sub(r'[<>:"/\\|?*]', '', name).strip()
        if not clean:
            return {
                'action': 'response',
                'response': "That folder name is invalid."
            }
        # Create on Desktop by default
        desktop = os.path.join(
            os.path.expanduser('~'), 'Desktop'
        )
        folder_path = os.path.join(desktop, clean)
        try:
            if os.path.exists(folder_path):
                return {
                    'action': 'response',
                    'response': (
                        f"Folder '{clean}' already "
                        f"exists on your Desktop!"
                    )
                }
            os.makedirs(folder_path)
            # Open the new folder
            import subprocess
            subprocess.Popen(['explorer', folder_path])
            return {
                'action': 'response',
                'response': (
                    f"✅ Created folder '{clean}' "
                    f"on your Desktop!"
                )
            }
        except Exception as e:
            return {
                'action': 'error',
                'response': (
                    f"Could not create folder: {e}"
                )
            }

    def handle_create_file(self, name):
        '''Create a new text file on Desktop.'''
        import os, re
        if not name or len(name.strip()) < 1:
            return {
                'action': 'response',
                'response': (
                    "What should I name the file? "
                    "Say: create file notes"
                )
            }
        clean = re.sub(
            r'[<>:"/\\|?*]', '', name
        ).strip()
        if not clean:
            return {
                'action': 'response',
                'response': "That file name is invalid."
            }
        # Add .txt if no extension
        if '.' not in clean:
            clean += '.txt'
        desktop = os.path.join(
            os.path.expanduser('~'), 'Desktop'
        )
        file_path = os.path.join(desktop, clean)
        try:
            if os.path.exists(file_path):
                return {
                    'action': 'response',
                    'response': (
                        f"File '{clean}' already "
                        f"exists on your Desktop!"
                    )
                }
            with open(
                file_path, 'w', encoding='utf-8'
            ) as f:
                f.write('')
            # Open in notepad
            import subprocess
            subprocess.Popen(['notepad', file_path])
            return {
                'action': 'response',
                'response': (
                    f"✅ Created '{clean}' on your "
                    f"Desktop and opened in Notepad!"
                )
            }
        except Exception as e:
            return {
                'action': 'error',
                'response': (
                    f"Could not create file: {e}"
                )
            }

    def _extract_create_name(self, text, keywords):
        '''Extract name from create command.'''
        name = text
        for k in sorted(
            keywords, key=len, reverse=True
        ):
            name = name.replace(k, '').strip()
        # Remove filler words
        for w in [
            'called', 'named', 'name',
            'please', 'for me', 'my',
        ]:
            name = name.replace(w, '').strip()
        return name.strip() if name.strip() else None

    def _extract_file_name(self, text):
        '''Extract file name from open command.'''
        remove_phrases = [
            'open the document', 'open document',
            'open the file', 'open file named',
            'open the pdf', 'open the image',
            'open the photo', 'open the video',
            'open the word file', 'open word file',
            'open the excel file', 'open excel file',
            'open the presentation', 'open the ppt',
            'show me the file', 'show the document',
            'launch the file', 'find and open',
            'open the folder named',
            'open the', 'open',
            'show me', 'show', 'launch',
            'please', 'can you', 'could you',
            'for me', 'my',
        ]
        name = text
        for phrase in sorted(
            remove_phrases, key=len, reverse=True
        ):
            name = name.replace(phrase, '').strip()
        name = name.strip(' .,?!')
        return name if len(name) > 1 else None

    def _extract_song_name(self, text):
        remove = ['play song', 'play the song', 'play music', 'play me', 'play', 'listen to', 'put on', 'start playing', 'please', 'can you', 'could you', 'from my pc', 'from my laptop', 'for me', 'the song', 'a song', 'any song', 'something', 'anything', 'random', 'shuffle', 'surprise me', 'play a']
        song = text
        for r in sorted(remove, key=len, reverse=True):
            song = song.replace(r, '').strip()
        return song.strip() if song.strip() else None

    def _extract_search_query(self, text):
        remove = ['search for', 'search', 'find', 'look up', 'look for', 'tell me about', 'information about', 'info about', 'who is', 'who was', 'what is', 'what was', 'where is', 'when is', 'how is', 'how does', 'why is', 'explain', 'describe', 'news about', 'definition of', 'meaning of', 'please', 'can you', 'could you']
        query = text
        for r in sorted(remove, key=len, reverse=True):
            query = query.replace(r, '').strip()
        return query if query else text

    def handle_settings(self):
        try:
            os.system('start ms-settings:')
            return {'action': 'app_opened', 'response': "Opening Windows Settings!"}
        except Exception as e:
            return {'action': 'error', 'response': f"Could not open settings: {e}"}

    def handle_open_folder(self, name, path):
        try:
            subprocess.Popen(['explorer', path])
            return {'action': 'folder_opened', 'response': f"Opening {name} for you!"}
        except Exception as e:
            return {'action': 'error', 'response': f"Could not open {name}: {e}"}

    def handle_open_app(self, text):
        app_name = text
        for k in self.open_keywords:
            app_name = app_name.replace(k, '').strip()

        if not app_name or app_name in ['app', 'application', 'program', 'it', '']:
            return {'action': 'response', 'response': "Which app would you like me to open?"}

        if 'camera' in app_name:
            return self.handle_camera()
        if 'clipboard' in app_name:
            return self.handle_clipboard()

        website_keywords = ['.com', '.net', '.org', '.pk', '.edu', '.io', '.co', '.gov', 'www.', 'http://', 'https://']
        if any(w in app_name for w in website_keywords):
            url = app_name if app_name.startswith('http') else 'https://' + app_name
            chrome_paths = [r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe']
            for chrome in chrome_paths:
                if os.path.exists(chrome):
                    subprocess.Popen([chrome, url])
                    return {'action': 'app_opened', 'response': f"Opening {app_name} in Chrome!"}
            webbrowser.open(url)
            return {'action': 'app_opened', 'response': f"Opening {app_name}!"}

        for key, paths in self.apps.items():
            if key in app_name or app_name in key:
                for path in paths:
                    if os.path.exists(path):
                        try:
                            subprocess.Popen([path])
                            return {'action': 'app_opened', 'response': f"Opening {key}!"}
                        except Exception:
                            continue

        try:
            result = subprocess.run(f'where {app_name}', capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                subprocess.Popen([app_name])
                return {'action': 'app_opened', 'response': f"Opening {app_name}!"}
        except Exception:
            pass

        # Try system access to find app
        if self.use_sys_access:
            result = self.sys_access.run_command(f'where {app_name}')
            if 'Output' in result:
                path = result.split('\n')[1].strip()
                subprocess.Popen([path])
                return {'action': 'app_opened', 'response': f"Opening {app_name}!"}

        return {'action': 'response', 'response': f"Sorry, I could not find {app_name}."}

    def handle_close(self, text):
        app = text
        for k in self.close_keywords:
            app = app.replace(k, '').strip()
        app = app.strip()

        if not app:
            return {
                'action': 'response',
                'response': "Which app should I close?"
            }

        # Name to exe mapping
        name_map = {
            'file explorer': 'explorer',
            'explorer': 'explorer',
            'chrome': 'chrome',
            'google chrome': 'chrome',
            'firefox': 'firefox',
            'edge': 'msedge',
            'microsoft edge': 'msedge',
            'notepad': 'notepad',
            'calculator': 'calculator',
            'paint': 'mspaint',
            'vlc': 'vlc',
            'spotify': 'spotify',
            'task manager': 'taskmgr',
            'word': 'winword',
            'excel': 'excel',
            'powerpoint': 'powerpnt',
            'vs code': 'code',
            'visual studio code': 'code',
        }

        exe_name = name_map.get(app.lower(), app)

        try:
            result = subprocess.run(
                ['taskkill', '/f', '/im',
                 f'{exe_name}.exe'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return {
                    'action': 'response',
                    'response': f"✅ Closed {app}."
                }
            # Try original name
            subprocess.run(
                ['taskkill', '/f', '/im',
                 f'{app}.exe'],
                capture_output=True
            )
            return {
                'action': 'response',
                'response': f"✅ Closed {app}."
            }
        except Exception:
            pass

        return {
            'action': 'response',
            'response': (
                f"Could not find {app} running."
            )
        }

    def handle_camera(self):
        try:
            os.system('start microsoft.windows.camera:')
            return {'action': 'app_opened', 'response': "Opening Camera app!"}
        except Exception as e:
            return {'action': 'error', 'response': f"Could not open camera: {e}"}

    def handle_clipboard(self):
        try:
            import pyautogui
            pyautogui.hotkey('win', 'v')
            return {'action': 'app_opened', 'response': "Opening Clipboard History!"}
        except Exception:
            try:
                os.system('start ms-settings:clipboard')
                return {'action': 'app_opened', 'response': "Opening Clipboard Settings!"}
            except Exception as e:
                return {'action': 'error', 'response': f"Could not open clipboard: {e}"}

    def handle_file_search(self, text):
        query = text
        for k in sorted(self.file_search_keywords, key=len, reverse=True):
            query = query.replace(k, '').strip()
        query = query.replace('my', '').replace('the', '').strip()
        if not query:
            return {'action': 'response', 'response': "What file would you like me to find?"}
        if self.use_sys_access:
            return {'action': 'response', 'response': self.sys_access.find_file(query)}
        try:
            subprocess.Popen(f'explorer /root,search-ms:query={query}', shell=True)
            return {'action': 'file_search', 'response': f"🔍 Searching your PC for '{query}'!"}
        except Exception as e:
            return {'action': 'error', 'response': f"Could not search: {e}"}

    def handle_time(self):
        t = datetime.datetime.now().strftime("%I:%M %p")
        return {'action': 'response', 'response': f"The current time is {t}."}

    def handle_date(self):
        d = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return {'action': 'response', 'response': f"Today is {d}."}

    def handle_volume(self, text):
        if any(k in text for k in ['up', 'increase', 'louder', 'raise']):
            return {'action': 'volume_up', 'response': "Increasing volume."}
        elif any(k in text for k in ['down', 'decrease', 'lower', 'quieter']):
            return {'action': 'volume_down', 'response': "Decreasing volume."}
        elif 'mute' in text:
            return {'action': 'volume_mute', 'response': "Muting volume."}
        return {'action': 'response', 'response': "Increase, decrease, or mute?"}

    def handle_youtube(self, text):
        query = text
        for k in self.youtube_keywords:
            query = query.replace(k, '').strip()
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return {'action': 'search', 'response': f"Opening YouTube for '{query}'."}
        webbrowser.open("https://www.youtube.com")
        return {'action': 'search', 'response': "Opening YouTube."}

    def handle_weather(self, text):
        city = text
        for k in self.weather_keywords:
            city = city.replace(k, '').strip()
        city = city.replace('in', '').replace('for', '').strip()
        if city:
            webbrowser.open(f"https://www.google.com/search?q=weather+in+{city}")
            return {'action': 'search', 'response': f"Checking weather for {city}."}
        webbrowser.open("https://www.google.com/search?q=weather+today")
        return {'action': 'search', 'response': "Checking today's weather."}

    def wifi_on(self):
        try:
            subprocess.run(
                'netsh interface set interface "Wi-Fi" enable',
                shell=True
            )
            return "WiFi enabled."
        except Exception as e:
            return f"Could not enable WiFi: {e}"

    def wifi_off(self):
        try:
            subprocess.run(
                'netsh interface set interface "Wi-Fi" disable',
                shell=True
            )
            return "WiFi disabled."
        except Exception as e:
            return f"Could not disable WiFi: {e}"

    def bluetooth_on(self):
        try:
            subprocess.run(
                'powershell -Command "Start-Service bthserv"',
                shell=True
            )
            return "Bluetooth enabled."
        except Exception as e:
            return f"Could not enable Bluetooth: {e}"

    def bluetooth_off(self):
        try:
            subprocess.run(
                'powershell -Command "Stop-Service bthserv -Force"',
                shell=True
            )
            return "Bluetooth disabled."
        except Exception as e:
            return f"Could not disable Bluetooth: {e}"