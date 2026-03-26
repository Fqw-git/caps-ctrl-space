import ctypes
import threading

import keyboard


user32 = ctypes.windll.user32
VK_CAPITAL = 0x14


class KeyMapperApp:
    def __init__(self) -> None:
        self.enabled = True
        self.show_notifications = False
        self.passthrough_caps = False
        self.state_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.tray_manager = None

    def set_tray_manager(self, tray_manager) -> None:
        self.tray_manager = tray_manager

    def show_status(self, message: str) -> None:
        print(message, flush=True)

    def ensure_capslock_off(self) -> None:
        if not (user32.GetKeyState(VK_CAPITAL) & 0x0001):
            return

        self.passthrough_caps = True
        try:
            keyboard.send("caps lock")
        finally:
            self.passthrough_caps = False

    def toggle_mapping(self) -> None:
        with self.state_lock:
            self.enabled = not self.enabled
            current = self.enabled

        if current:
            self.ensure_capslock_off()

        if current:
            self.show_status("[ON ] Caps Lock -> Ctrl+Space")
        else:
            self.show_status("[OFF] Caps Lock restored")

        if self.tray_manager is not None:
            self.tray_manager.refresh(show_notice=True)

    def toggle_notifications(self) -> None:
        with self.state_lock:
            self.show_notifications = not self.show_notifications
            current = self.show_notifications

        self.show_status(f"[INFO] Notifications {'enabled' if current else 'disabled'}")
        if self.tray_manager is not None:
            self.tray_manager.refresh(show_notice=False)

    def on_caps_press(self, event: keyboard.KeyboardEvent) -> None:
        if event.event_type != "down":
            return

        if self.passthrough_caps:
            return

        if keyboard.is_pressed("ctrl"):
            self.toggle_mapping()
            return

        with self.state_lock:
            current = self.enabled

        if current:
            keyboard.send("ctrl+space")
            return

        self.passthrough_caps = True
        try:
            keyboard.send("caps lock")
        finally:
            self.passthrough_caps = False

    def install_keyboard_hooks(self) -> None:
        keyboard.on_press_key("caps lock", self.on_caps_press, suppress=True)

    def cleanup(self) -> None:
        self.stop_event.set()
        keyboard.unhook_all()
