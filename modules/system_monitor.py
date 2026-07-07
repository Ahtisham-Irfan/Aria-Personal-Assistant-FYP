import os
import platform
from PySide6.QtCore import QTimer


class SystemMonitor:
    """
    Polls CPU / RAM / Disk usage on a timer and reports
    it back via the on_update callback as a dict:
    {'cpu': float, 'ram': float, 'disk': float}
    """

    def __init__(self):
        self._timer = QTimer()
        self._timer.setInterval(2000)
        self._on_update = None
        self._timer.timeout.connect(self._poll)
        try:
            import psutil
            self._psutil = psutil
        except Exception:
            self._psutil = None

    def start(self, on_update=None):
        self._on_update = on_update
        self._timer.start()
        self._poll()

    def stop(self):
        self._timer.stop()

    def _poll(self):
        if not self._on_update:
            return

        if self._psutil:
            try:
                cpu = self._psutil.cpu_percent(interval=None)
                ram = self._psutil.virtual_memory().percent
                drive = "C:\\" if platform.system() == "Windows" \
                    else os.path.abspath(os.sep)
                disk = self._psutil.disk_usage(drive).percent
            except Exception:
                cpu, ram, disk = 0, 0, 0
        else:
            cpu, ram, disk = 0, 0, 0

        self._on_update({
            'cpu': cpu, 'ram': ram, 'disk': disk
        })
