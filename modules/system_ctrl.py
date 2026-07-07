import ctypes
import os
import subprocess
import datetime
from pathlib import Path

class SystemController:
    def __init__(self):
        self.volume_available = False
        self._init_volume()

    def _init_volume(self):
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
            self.volume_available = True
            print("Volume control initialized!")
        except Exception:
            self.volume_available = False
            print("Using keyboard volume control")

    def volume_up(self):
        try:
            if self.volume_available:
                current = self.volume_ctrl.GetMasterVolumeLevelScalar()
                new_vol = min(1.0, current + 0.1)
                self.volume_ctrl.SetMasterVolumeLevelScalar(new_vol, None)
                return f"Volume increased to {int(new_vol * 100)}%."
            else:
                import pyautogui
                pyautogui.press('volumeup')
                pyautogui.press('volumeup')
                return "Volume increased."
        except Exception as e:
            return f"Could not increase volume: {e}"

    def volume_down(self):
        try:
            if self.volume_available:
                current = self.volume_ctrl.GetMasterVolumeLevelScalar()
                new_vol = max(0.0, current - 0.1)
                self.volume_ctrl.SetMasterVolumeLevelScalar(new_vol, None)
                return f"Volume decreased to {int(new_vol * 100)}%."
            else:
                import pyautogui
                pyautogui.press('volumedown')
                pyautogui.press('volumedown')
                return "Volume decreased."
        except Exception as e:
            return f"Could not decrease volume: {e}"

    def volume_mute(self):
        try:
            if self.volume_available:
                is_muted = self.volume_ctrl.GetMute()
                self.volume_ctrl.SetMute(not is_muted, None)
                return "Volume muted." if not is_muted else "Volume unmuted."
            else:
                import pyautogui
                pyautogui.press('volumemute')
                return "Volume muted."
        except Exception as e:
            return f"Could not mute: {e}"

    def shutdown(self):
        try:
            subprocess.run(
                ['shutdown', '/s', '/t', '10'],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "System will shutdown in 10 seconds."
        except Exception as e:
            return f"Could not shutdown: {e}"

    def restart(self):
        try:
            subprocess.run(['shutdown', '/r', '/t', '10'])
            return "System will restart in 10 seconds."
        except Exception as e:
            return f"Could not restart: {e}"

    def sleep(self):
        try:
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'])
            return "Putting system to sleep."
        except Exception as e:
            return f"Could not sleep: {e}"

    def lock_screen(self):
        try:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'])
            return "Locking screen."
        except Exception as e:
            return f"Could not lock: {e}"

    def take_screenshot(self):
        try:
            import pyautogui

            desktop = Path.home() / "OneDrive" / "Desktop"

            if not desktop.exists():
                desktop = Path.home() / "Desktop"

            filename = datetime.datetime.now().strftime(
                "screenshot_%Y%m%d_%H%M%S.png"
            )

            save_path = desktop / filename

            screenshot = pyautogui.screenshot()
            screenshot.save(str(save_path))

            print(f"Screenshot saved at: {save_path}")

            return f"Screenshot saved as {filename}"

        except Exception as e:
            print(f"Screenshot Error: {e}")
            return f"Could not take screenshot: {e}"

    def get_battery(self):
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                pct = battery.percent
                status = "plugged in" if battery.power_plugged else "on battery"
                return f"Battery is at {pct}% and {status}."
            return "No battery detected."
        except Exception as e:
            return f"Could not get battery: {e}"

    def close_app(self, app_name):
        try:
            if not app_name.endswith(".exe"):
                app_name += ".exe"
            # attempt to close the application
            subprocess.run(['taskkill', '/f', '/im', app_name], capture_output=True, text=True)
            return f"Closing {app_name}."
        except Exception as e:
            return f"Could not close {app_name}: {e}"

    def wifi_on(self):
        try:
            # enable the Wi-Fi interface
            subprocess.run(
                'netsh interface set interface "Wi-Fi" admin=enabled',
                shell=True
            )
            return "WiFi enabled."
        except Exception as e:
            return f"Could not enable WiFi: {e}"

    def wifi_off(self):
        try:
            subprocess.run(
                'netsh interface set interface "Wi-Fi" admin=disabled',
                shell=True
            )
            return "WiFi disabled."
        except Exception as e:
            return f"Could not disable WiFi: {e}"    
    def bluetooth_on(self):
        try:
            subprocess.run(
                'powershell Start-Service bthserv',
                shell=True
            )
            return "Bluetooth enabled."
        except Exception as e:
            return f"Could not enable Bluetooth: {e}"

    def bluetooth_off(self):
        try:
            subprocess.run(
                'powershell Stop-Service bthserv -Force',
                shell=True
            )
            return "Bluetooth disabled."
        except Exception as e:
            return f"Could not disable Bluetooth: {e}"   
    def brightness_up(self):
        try:
            import screen_brightness_control as sbc

            current = sbc.get_brightness()[0]
            new = min(100, current + 10)

            sbc.set_brightness(new)

            return f"Brightness increased to {new}%"

        except Exception as e:
            return f"Could not increase brightness: {e}"

    def brightness_down(self):
        try:
            import screen_brightness_control as sbc

            current = sbc.get_brightness()
            if isinstance(current, list):
                current = current[0]
            new = max(0, current - 10)

            sbc.set_brightness(new)

            return f"Brightness decreased to {new}%"

        except Exception as e:
            return f"Could not decrease brightness: {e}"

    def open_settings(self):
        try:
            subprocess.Popen("start ms-settings:", shell=True)
            return "Opening Windows Settings."
        except Exception as e:
            return f"Could not open Settings: {e}"

    def empty_recycle_bin(self):
        try:
            import winshell

            winshell.recycle_bin().empty(
                confirm=False,
                show_progress=False,
                sound=True
            )

            return "Recycle Bin emptied successfully."

        except Exception as e:
            return f"Could not empty Recycle Bin: {e}"

    def open_powershell(self):
        try:
            subprocess.Popen(
                ["powershell.exe"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return "Opening PowerShell."
        except Exception as e:
            return f"Could not open PowerShell: {e}"
    def open_recycle_bin(self):
        try:
            subprocess.Popen(
                'explorer.exe shell:RecycleBinFolder',
                shell=True
            )
            return "Opening Recycle Bin."
        except Exception as e:
            return f"Could not open Recycle Bin: {e}"    