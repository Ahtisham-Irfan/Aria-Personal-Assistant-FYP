import re
import datetime
from PySide6.QtCore import QTimer, QObject, Signal


class ReminderManager(QObject):
    reminder_triggered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.reminders = []
        self.timer = QTimer()
        self.timer.timeout.connect(self._check)
        self.timer.start(30000)  # Check every 30 sec

    def parse_and_add(self, text):
        text = text.lower().strip()
        minutes = None
        message = ""

        # Pattern: "remind me in X minutes to ..."
        m = re.search(
            r'in\s+(\d+)\s+minute', text
        )
        if m:
            minutes = int(m.group(1))

        # Pattern: "in X hours"
        if not minutes:
            m = re.search(
                r'in\s+(\d+)\s+hour', text
            )
            if m:
                minutes = int(m.group(1)) * 60

        # Pattern: "in X seconds"
        if not minutes:
            m = re.search(
                r'in\s+(\d+)\s+second', text
            )
            if m:
                minutes = max(
                    1, int(m.group(1)) // 60
                )

        if not minutes:
            return None

        # Extract message
        for kw in ['to ', 'about ', 'that ']:
            idx = text.find(kw)
            if idx != -1:
                message = text[
                    idx + len(kw):
                ].strip()
                break

        if not message:
            message = "Your reminder is here!"

        # Capitalize
        message = message.capitalize()

        # Set trigger time
        trigger_time = (
            datetime.datetime.now() +
            datetime.timedelta(minutes=minutes)
        )

        self.reminders.append({
            'message': message,
            'trigger_time': trigger_time,
            'minutes': minutes,
            'done': False
        })

        if minutes >= 60:
            hours = minutes // 60
            mins = minutes % 60
            if mins:
                time_str = (
                    f"{hours} hour "
                    f"and {mins} minutes"
                )
            else:
                time_str = f"{hours} hour"
        else:
            time_str = f"{minutes} minutes"

        return (
            f"Got it! I will remind you "
            f"in {time_str} to {message} ⏰"
        )

    def _check(self):
        now = datetime.datetime.now()
        for r in self.reminders:
            if not r['done'] and \
                    now >= r['trigger_time']:
                r['done'] = True
                self.reminder_triggered.emit(
                    f"⏰ Reminder: {r['message']}"
                )

    def get_active(self):
        now = datetime.datetime.now()
        active = []
        for r in self.reminders:
            if not r['done']:
                remaining = (
                    r['trigger_time'] - now
                )
                mins = int(
                    remaining.total_seconds() / 60
                )
                active.append({
                    'message': r['message'],
                    'remaining_mins': max(1, mins)
                })
        return active

    def clear_all(self):
        self.reminders.clear()