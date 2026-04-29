import ctypes
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING

import keyboard


user32 = ctypes.windll.user32
VK_CAPITAL = 0x14

if TYPE_CHECKING:
    from tray_icon import TrayManager


@dataclass(frozen=True)
class AppStateSnapshot:
    enabled: bool
    show_notifications: bool


class KeyMapperApp:
    def __init__(self) -> None:
        self._enabled = True
        self._show_notifications = False
        self.passthrough_caps = threading.Event()  # 重入保护, 标记是否是程序自己发送的 Caps Lock 事件
        self.state_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.tray_manager: TrayManager | None = None

    def set_tray_manager(self, tray_manager: "TrayManager") -> None:
        self.tray_manager = tray_manager

    def show_status(self, message: str) -> None:
        print(message, flush=True)

    def get_snapshot(self) -> AppStateSnapshot:
        with self.state_lock:
            return AppStateSnapshot(
                enabled=self._enabled,
                show_notifications=self._show_notifications,
            )

    def _send_capslock_passthrough(self) -> None:
        self.passthrough_caps.set()
        try:
            keyboard.send("caps lock")
        finally:
            self.passthrough_caps.clear()

    def ensure_capslock_off(self) -> None:
        if not (user32.GetKeyState(VK_CAPITAL) & 0x0001):
            return

        self._send_capslock_passthrough()

    def toggle_mapping(self) -> None:
        with self.state_lock:
            self._enabled = not self._enabled
            snapshot = AppStateSnapshot(
                enabled=self._enabled,
                show_notifications=self._show_notifications,
            )

        if snapshot.enabled:
            self.ensure_capslock_off()

        if snapshot.enabled:
            self.show_status("[ON ] Caps Lock -> Ctrl+Space")
        else:
            self.show_status("[OFF] Caps Lock restored")

        if self.tray_manager is not None:
            self.tray_manager.request_refresh(snapshot, show_notice=True)

    def toggle_notifications(self) -> None:
        with self.state_lock:
            self._show_notifications = not self._show_notifications
            snapshot = AppStateSnapshot(
                enabled=self._enabled,
                show_notifications=self._show_notifications,
            )

        self.show_status(
            f"[INFO] Notifications {'enabled' if snapshot.show_notifications else 'disabled'}"
        )
        if self.tray_manager is not None:
            self.tray_manager.request_refresh(snapshot, show_notice=False)

    def on_caps_press(self, event: keyboard.KeyboardEvent) -> None:
        if event.event_type != "down":
            return

        if self.passthrough_caps.is_set():
            return

        if keyboard.is_pressed("ctrl"):
            self.toggle_mapping()
            return

        if self.get_snapshot().enabled:
            keyboard.send("ctrl+space")
            return

        self._send_capslock_passthrough()

    def install_keyboard_hooks(self) -> None:
        keyboard.on_press_key("caps lock", self.on_caps_press, suppress=True)

    def cleanup(self) -> None:
        self.stop_event.set()
        keyboard.unhook_all()
