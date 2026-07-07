import os
import subprocess
import datetime
import socket
import platform
import getpass


class SystemAccess:
    def __init__(self):
        self.user = getpass.getuser()
        self.home = os.path.expanduser("~")

        # ALL drives + user folders
        self.search_paths = self._get_all_paths()
        print("System Access: Full PC access ready!")

    def _get_all_paths(self):
        """Build complete list of search paths."""
        paths = []

        # User folders first (most likely location)
        user_folders = [
            'Desktop', 'Documents', 'Downloads',
            'Pictures', 'Videos', 'Music',
            'OneDrive', 'OneDrive - Personal',
        ]
        for folder in user_folders:
            p = os.path.join(self.home, folder)
            if os.path.exists(p):
                paths.append(p)

        # All available drives C D E F G H
        for drive in 'CDEFGHIJ':
            drive_path = f"{drive}:\\"
            if os.path.exists(drive_path):
                paths.append(drive_path)

        return paths

    # ----------------------------
    # OPEN FILE BY NAME — MAIN FIX
    # ----------------------------
    def open_file_by_name(self, name):
        """
        Search entire PC for file by name
        and open it with default application.
        """
        if not name or len(name.strip()) < 2:
            return {
                'opened': False,
                'response': (
                    "Please tell me the file name."
                )
            }

        print(f"Searching for: '{name}'")
        found = self._deep_search(name)
        print(f"Found {len(found)} files")

        if not found:
            # Try partial search with just
            # first word of name
            words = name.split()
            if len(words) > 1:
                for word in words:
                    if len(word) > 2:
                        found = self._deep_search(
                            word
                        )
                        if found:
                            break

        if not found:
            return {
                'opened': False,
                'response': (
                    f"I could not find any file "
                    f"named '{name}' on your PC.\n\n"
                    f"💡 Tips:\n"
                    f"• Say the exact file name\n"
                    f"• Example: open Ahmad Ali CV\n"
                    f"• Example: open project report"
                )
            }

        # Pick best match
        best = self._best_match(name, found)
        return self._open_path(best)

    def _deep_search(self, name):
        """
        Search across all drives and
        user folders for matching files.
        """
        name_lower = name.lower().strip()
        results = []

        # Skip these folders — system/junk
        skip_dirs = {
            'windows', 'system32', 'syswow64',
            '$recycle.bin', 'winsxs', 'assembly',
            'softwaredistribution', 'servicing',
            'node_modules', '__pycache__',
            'site-packages', 'dist-info',
            '.git', 'temp', 'tmp', 'cache',
            'nvidia', 'intel', 'amd',
        }

        for search_root in self.search_paths:
            if not os.path.exists(search_root):
                continue
            try:
                for root, dirs, files in \
                        os.walk(search_root):
                    # Filter out skip dirs
                    dirs[:] = [
                        d for d in dirs
                        if d.lower()
                        not in skip_dirs
                        and not d.startswith('$')
                    ]

                    for file in files:
                        file_lower = file.lower()
                        # Remove extension for match
                        file_no_ext = os.path.splitext(
                            file_lower
                        )[0]

                        # Check if name matches
                        if (
                            name_lower in file_lower
                            or name_lower in file_no_ext
                            or self._fuzzy_match(
                                name_lower, file_no_ext
                            )
                        ):
                            full_path = os.path.join(
                                root, file
                            )
                            results.append(full_path)

                        if len(results) >= 20:
                            return results

            except (PermissionError, OSError):
                continue

        return results

    def _fuzzy_match(self, query, filename):
        """
        Check if all words of query
        appear in filename.
        """
        words = query.split()
        if len(words) < 2:
            return False
        # All words must be in filename
        return all(w in filename for w in words)

    def _best_match(self, name, paths):
        """
        Score and pick the best file match.
        Prefers: exact name > recent > smaller path
        """
        name_lower = name.lower()
        name_words = name_lower.split()
        best = paths[0]
        best_score = -1

        for path in paths:
            fname = os.path.basename(path).lower()
            fname_no_ext = os.path.splitext(fname)[0]
            score = 0

            # Exact filename match (no ext)
            if fname_no_ext == name_lower:
                score += 100

            # All words present
            word_matches = sum(
                1 for w in name_words
                if w in fname_no_ext
            )
            score += word_matches * 10

            # Starts with query
            if fname_no_ext.startswith(name_lower):
                score += 20

            # Recency bonus
            try:
                mtime = os.path.getmtime(path)
                score += mtime / 1e13
            except Exception:
                pass

            # Prefer user folders
            user_folders = [
                'desktop', 'documents',
                'downloads', 'pictures',
                'onedrive'
            ]
            path_lower = path.lower()
            if any(f in path_lower
                   for f in user_folders):
                score += 5

            if score > best_score:
                best_score = score
                best = path

        return best

    def _open_path(self, path):
        """Open file with Windows default app."""
        try:
            name = os.path.basename(path)
            folder = os.path.dirname(path)
            # os.startfile is the Windows way
            os.startfile(path)
            return {
                'opened': True,
                'path': path,
                'response': (
                    f"✅ Opening {name}!\n"
                    f"📂 {folder}"
                )
            }
        except Exception as e:
            try:
                # Fallback: open in explorer
                subprocess.Popen(
                    ['explorer', '/select,', path]
                )
                return {
                    'opened': True,
                    'path': path,
                    'response': (
                        f"✅ Found and showing: "
                        f"{os.path.basename(path)}"
                    )
                }
            except Exception:
                return {
                    'opened': False,
                    'response': (
                        f"Found the file but could "
                        f"not open it: {e}"
                    )
                }

    # ----------------------------
    # FIND FILE (list only)
    # ----------------------------
    def find_file(self, name, search_path=None):
        results = self._deep_search(name)
        if not results:
            return f"No files found matching '{name}'"
        out = (
            f"🔍 Found {len(results)} file(s) "
            f"matching '{name}':\n\n"
        )
        for r in results[:10]:
            try:
                size = os.path.getsize(r)
                size_str = (
                    f"{size/1024:.1f} KB"
                    if size < 1024*1024
                    else f"{size/(1024*1024):.1f} MB"
                )
            except Exception:
                size_str = "Unknown"
            out += (
                f"📄 {os.path.basename(r)}\n"
                f"   📂 {os.path.dirname(r)}\n"
                f"   💾 {size_str}\n\n"
            )
        return out

    # ----------------------------
    # LIST FOLDER
    # ----------------------------
    def list_folder(self, path):
        try:
            if not os.path.exists(path):
                return f"Folder not found: {path}"
            items = os.listdir(path)
            folders = [
                i for i in items
                if os.path.isdir(
                    os.path.join(path, i)
                )
            ]
            files = [
                i for i in items
                if os.path.isfile(
                    os.path.join(path, i)
                )
            ]
            result = (
                f"📁 {path}\n\n"
                f"Folders ({len(folders)}):\n"
            )
            for f in folders[:10]:
                result += f"  📂 {f}\n"
            result += f"\nFiles ({len(files)}):\n"
            for f in files[:15]:
                result += f"  📄 {f}\n"
            if len(files) > 15:
                result += (
                    f"  ... and "
                    f"{len(files)-15} more"
                )
            return result
        except PermissionError:
            return f"Access denied to {path}"
        except Exception as e:
            return f"Error: {e}"

    # ----------------------------
    # READ FILE
    # ----------------------------
    def read_file(self, path):
        try:
            if not os.path.exists(path):
                return f"File not found: {path}"
            size = os.path.getsize(path)
            if size > 100 * 1024:
                return (
                    f"File too large "
                    f"({size/1024:.0f} KB). "
                    f"Opening instead."
                )
            with open(
                path, 'r',
                encoding='utf-8',
                errors='ignore'
            ) as f:
                content = f.read()
            lines = content.split('\n')
            preview = '\n'.join(lines[:50])
            result = (
                f"📄 {os.path.basename(path)}\n"
                f"Lines: {len(lines)} | "
                f"Size: {size/1024:.1f} KB\n\n"
                f"{preview}"
            )
            if len(lines) > 50:
                result += (
                    f"\n\n... "
                    f"({len(lines)-50} more lines)"
                )
            return result
        except Exception as e:
            return f"Cannot read file: {e}"

    # ----------------------------
    # FILE INFO
    # ----------------------------
    def get_file_info(self, path):
        try:
            if not os.path.exists(path):
                return f"Not found: {path}"
            stat = os.stat(path)
            size = stat.st_size
            created = datetime.datetime\
                .fromtimestamp(stat.st_ctime)\
                .strftime("%B %d, %Y %I:%M %p")
            modified = datetime.datetime\
                .fromtimestamp(stat.st_mtime)\
                .strftime("%B %d, %Y %I:%M %p")
            size_str = (
                f"{size} bytes" if size < 1024
                else f"{size/1024:.1f} KB"
                if size < 1024*1024
                else f"{size/(1024*1024):.1f} MB"
            )
            return (
                f"📄 {os.path.basename(path)}\n\n"
                f"📂 {os.path.dirname(path)}\n"
                f"💾 Size: {size_str}\n"
                f"📅 Created: {created}\n"
                f"✏ Modified: {modified}\n"
                f"🔒 Read-only: "
                f"{'Yes' if not os.access(path, os.W_OK) else 'No'}"
            )
        except Exception as e:
            return f"Error: {e}"

    # ----------------------------
    # PROCESSES
    # ----------------------------
    def list_processes(self):
        import psutil
        try:
            procs = []
            for p in psutil.process_iter([
                'pid', 'name', 'memory_info'
            ]):
                try:
                    mem = p.info['memory_info']
                    mem_mb = (
                        mem.rss / (1024*1024)
                        if mem else 0
                    )
                    procs.append({
                        'pid': p.info['pid'],
                        'name': p.info['name'],
                        'mem_mb': mem_mb
                    })
                except Exception:
                    pass
            procs.sort(
                key=lambda x: x['mem_mb'],
                reverse=True
            )
            result = (
                f"⚙ Running Processes "
                f"({len(procs)} total)\n\n"
                f"Top by Memory:\n"
                f"{'─'*40}\n"
            )
            for p in procs[:15]:
                result += (
                    f"{p['name'][:25]:<26}"
                    f"PID:{p['pid']:<8}"
                    f"{p['mem_mb']:.0f} MB\n"
                )
            return result
        except Exception as e:
            return f"Error: {e}"

    def kill_process(self, name_or_pid):
        import psutil
        try:
            killed = []
            for p in psutil.process_iter(
                ['pid', 'name']
            ):
                try:
                    if (
                        str(p.info['pid'])
                        == str(name_or_pid)
                        or name_or_pid.lower()
                        in p.info['name'].lower()
                    ):
                        p.kill()
                        killed.append(
                            p.info['name']
                        )
                except Exception:
                    pass
            if killed:
                return (
                    f"✅ Killed: "
                    f"{', '.join(set(killed))}"
                )
            return (
                f"No process found: {name_or_pid}"
            )
        except Exception as e:
            return f"Error: {e}"

    # ----------------------------
    # SYSTEM INFO
    # ----------------------------
    def get_full_system_info(self):
        import psutil
        try:
            cpu_freq = psutil.cpu_freq()
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')
            os_info = platform.uname()
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(
                    hostname
                )
            except Exception:
                local_ip = "Not connected"
            battery = psutil.sensors_battery()
            bat_str = "No battery"
            if battery:
                bat_str = (
                    f"{battery.percent:.0f}% — "
                    f"{'Charging' if battery.power_plugged else 'On Battery'}"
                )
            boot = datetime.datetime.fromtimestamp(
                psutil.boot_time()
            )
            uptime = datetime.datetime.now() - boot
            hours = int(
                uptime.total_seconds() // 3600
            )
            mins = int(
                (uptime.total_seconds() % 3600)
                // 60
            )
            return (
                f"💻 SYSTEM INFO\n\n"
                f"OS: {os_info.system} "
                f"{os_info.release}\n"
                f"Computer: {os_info.node}\n"
                f"User: {self.user}\n\n"
                f"CPU Cores: "
                f"{psutil.cpu_count(logical=False)}"
                f" / {psutil.cpu_count()} logical\n"
                f"CPU Speed: "
                f"{cpu_freq.current:.0f} MHz\n"
                f"CPU Usage: "
                f"{psutil.cpu_percent()}%\n\n"
                f"RAM: "
                f"{ram.total/(1024**3):.1f} GB | "
                f"{ram.percent}% used\n"
                f"Free RAM: "
                f"{ram.available/(1024**3):.1f} GB\n\n"
                f"Disk C: "
                f"{disk.total/(1024**3):.0f} GB | "
                f"{disk.percent}% used\n"
                f"Free: "
                f"{disk.free/(1024**3):.1f} GB\n\n"
                f"Battery: {bat_str}\n"
                f"Uptime: {hours}h {mins}m\n"
                f"IP: {local_ip}"
            )
        except Exception as e:
            return f"Error: {e}"

    def get_disk_usage(self):
        import psutil
        result = "💾 DISK USAGE\n\n"
        try:
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(
                        part.mountpoint
                    )
                    total = usage.total / (1024**3)
                    used = usage.used / (1024**3)
                    free = usage.free / (1024**3)
                    pct = usage.percent
                    bar_f = int(pct / 5)
                    bar = (
                        "█" * bar_f
                        + "░" * (20 - bar_f)
                    )
                    result += (
                        f"Drive {part.mountpoint}\n"
                        f"{bar} {pct}%\n"
                        f"Total:{total:.0f}GB  "
                        f"Used:{used:.1f}GB  "
                        f"Free:{free:.1f}GB\n\n"
                    )
                except Exception:
                    pass
            return result
        except Exception as e:
            return f"Error: {e}"

    def get_network_info(self):
        import psutil
        try:
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(
                    hostname
                )
            except Exception:
                local_ip = "Not connected"
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_io_counters()
            result = (
                f"🌐 NETWORK\n\n"
                f"Hostname: {hostname}\n"
                f"Local IP: {local_ip}\n\n"
                f"Sent: "
                f"{stats.bytes_sent/(1024**2):.1f}"
                f" MB\n"
                f"Received: "
                f"{stats.bytes_recv/(1024**2):.1f}"
                f" MB\n\nInterfaces:\n"
            )
            for name, addrs in interfaces.items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        result += (
                            f"  {name}: "
                            f"{addr.address}\n"
                        )
            return result
        except Exception as e:
            return f"Error: {e}"

    def check_internet(self):
        try:
            socket.create_connection(
                ("8.8.8.8", 53), timeout=3
            )
            return "✅ Internet connected!"
        except OSError:
            return "❌ No internet connection."

    def get_installed_apps(self):
        import winreg
        apps = []
        keys = [
            r"SOFTWARE\Microsoft\Windows"
            r"\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft"
            r"\Windows\CurrentVersion\Uninstall",
        ]
        try:
            for key_path in keys:
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        key_path
                    )
                    i = 0
                    while True:
                        try:
                            sub = winreg.EnumKey(
                                key, i
                            )
                            sub_key = winreg.OpenKey(
                                key, sub
                            )
                            try:
                                name, _ = (
                                    winreg.QueryValueEx(
                                        sub_key,
                                        "DisplayName"
                                    )
                                )
                                if name:
                                    apps.append(name)
                            except Exception:
                                pass
                            i += 1
                        except OSError:
                            break
                except Exception:
                    pass
            apps = sorted(set(apps))
            result = (
                f"📦 Installed Apps "
                f"({len(apps)})\n\n"
            )
            for app in apps[:30]:
                result += f"• {app}\n"
            if len(apps) > 30:
                result += (
                    f"\n... and {len(apps)-30} more"
                )
            return result
        except Exception as e:
            return f"Error: {e}"

    def get_startup_programs(self):
        import winreg
        startups = []
        keys = [
            (winreg.HKEY_CURRENT_USER,
             r"SOFTWARE\Microsoft\Windows"
             r"\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"SOFTWARE\Microsoft\Windows"
             r"\CurrentVersion\Run"),
        ]
        try:
            for hive, path in keys:
                try:
                    key = winreg.OpenKey(hive, path)
                    i = 0
                    while True:
                        try:
                            name, val, _ = (
                                winreg.EnumValue(
                                    key, i
                                )
                            )
                            startups.append(
                                (name, val)
                            )
                            i += 1
                        except OSError:
                            break
                except Exception:
                    pass
            result = (
                f"🚀 STARTUP PROGRAMS "
                f"({len(startups)})\n\n"
            )
            for name, path in startups:
                result += (
                    f"• {name}\n"
                    f"  {path[:55]}\n\n"
                )
            return result or "No startup programs."
        except Exception as e:
            return f"Error: {e}"

    def get_recent_files(self):
        try:
            recent = os.path.join(
                os.environ.get('APPDATA', ''),
                r'Microsoft\Windows\Recent'
            )
            if not os.path.exists(recent):
                return "Recent files not found."
            files = []
            for f in os.listdir(recent):
                path = os.path.join(recent, f)
                mtime = os.path.getmtime(path)
                files.append((f, mtime))
            files.sort(
                key=lambda x: x[1], reverse=True
            )
            result = "🕐 RECENT FILES\n\n"
            for name, mtime in files[:15]:
                dt = datetime.datetime\
                    .fromtimestamp(mtime)\
                    .strftime("%b %d  %I:%M %p")
                clean = name.replace('.lnk', '')
                result += f"• {clean}\n  {dt}\n\n"
            return result
        except Exception as e:
            return f"Error: {e}"

    def list_env_variables(self):
        result = "🔧 ENVIRONMENT VARIABLES\n\n"
        important = [
            'USERNAME', 'COMPUTERNAME', 'OS',
            'TEMP', 'APPDATA', 'LOCALAPPDATA',
            'USERPROFILE', 'SYSTEMROOT',
            'PROGRAMFILES',
        ]
        for key in important:
            val = os.environ.get(key, 'Not set')
            if len(val) > 60:
                val = val[:60] + "..."
            result += f"{key}:\n  {val}\n\n"
        return result

    def get_clipboard(self):
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            content = root.clipboard_get()
            root.destroy()
            if content:
                preview = (
                    content[:300] + "..."
                    if len(content) > 300
                    else content
                )
                return f"📋 Clipboard:\n\n{preview}"
            return "📋 Clipboard is empty."
        except Exception:
            return "Could not access clipboard."

    def get_battery_detail(self):
        import psutil
        try:
            battery = psutil.sensors_battery()
            if not battery:
                return "No battery detected."
            pct = battery.percent
            plugged = battery.power_plugged
            secs = battery.secsleft
            if secs == psutil.POWER_TIME_UNLIMITED:
                time_str = "Plugged in"
            elif secs == psutil.POWER_TIME_UNKNOWN:
                time_str = "Calculating..."
            else:
                hrs = secs // 3600
                mins = (secs % 3600) // 60
                time_str = f"{hrs}h {mins}m remaining"
            bar_f = int(pct / 5)
            bar = "█" * bar_f + "░" * (20 - bar_f)
            color = (
                "🟢" if pct > 50
                else "🟡" if pct > 20
                else "🔴"
            )
            status = (
                "Charging ⚡"
                if plugged else "On Battery 🔋"
            )
            return (
                f"🔋 BATTERY\n\n"
                f"{color} {bar} {pct:.0f}%\n\n"
                f"Status: {status}\n"
                f"Time: {time_str}"
            )
        except Exception as e:
            return f"Error: {e}"

    def run_command(self, cmd):
        try:
            result = subprocess.run(
                cmd, shell=True,
                capture_output=True,
                text=True, timeout=10
            )
            output = result.stdout.strip()
            error = result.stderr.strip()
            if output:
                return f"✅ Output:\n{output[:500]}"
            if error:
                return f"⚠ Error:\n{error[:300]}"
            return "✅ Command executed."
        except subprocess.TimeoutExpired:
            return "⏱ Command timed out."
        except Exception as e:
            return f"Error: {e}"