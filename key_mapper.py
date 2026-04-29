import ctypes
import threading
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import keyboard


user32 = ctypes.windll.user32
VK_CAPITAL = 0x14
MAX_WINDOW_TEXT = 512

if TYPE_CHECKING:
    from tray_icon import TrayManager


@dataclass(frozen=True)
class AppStateSnapshot:
    enabled: bool
    show_notifications: bool


class KeyMapperApp:
    def __init__(self, debug_enabled: bool = False, debug_log_path: Path | None = None) -> None:
        self._enabled = True
        self._show_notifications = False
        self.passthrough_caps = threading.Event()  # 重入保护, 标记是否是程序自己发送的 Caps Lock 事件
        self.state_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.tray_manager: TrayManager | None = None
        self.debug_enabled = debug_enabled
        self.debug_log_path = debug_log_path

    def set_tray_manager(self, tray_manager: "TrayManager") -> None:
        self.tray_manager = tray_manager

    def show_status(self, message: str) -> None:
        print(message, flush=True)

    def debug_log(self, message: str) -> None:
        if not self.debug_enabled or self.debug_log_path is None:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        line = f"{timestamp} {message}\n"
        try:
            with self.debug_log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(line)
        except OSError:
            pass

    def get_capslock_state(self) -> bool:
        return bool(user32.GetKeyState(VK_CAPITAL) & 0x0001)

    def get_foreground_window_info(self) -> str:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return "foreground=none"

        title_buffer = ctypes.create_unicode_buffer(MAX_WINDOW_TEXT)
        class_buffer = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, title_buffer, len(title_buffer))
        user32.GetClassNameW(hwnd, class_buffer, len(class_buffer))

        process_id = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

        return (
            f"foreground=hwnd=0x{hwnd:08X} "
            f"pid={process_id.value} "
            f"class={class_buffer.value!r} "
            f"title={title_buffer.value!r}"
        )

    def get_snapshot(self) -> AppStateSnapshot:
        with self.state_lock:
            return AppStateSnapshot(
                enabled=self._enabled,
                show_notifications=self._show_notifications,
            )

    def _send_capslock_passthrough(self) -> None:
        self.debug_log(
            f"send caps_lock passthrough begin caps_on={self.get_capslock_state()} {self.get_foreground_window_info()}"
        )
        self.passthrough_caps.set()
        try:
            keyboard.send("caps lock")
        finally:
            self.passthrough_caps.clear()
            self.debug_log(
                f"send caps_lock passthrough end caps_on={self.get_capslock_state()} {self.get_foreground_window_info()}"
            )

    def ensure_capslock_off(self) -> None:
        if not self.get_capslock_state():
            return

        self.debug_log("ensure_capslock_off detected caps_on=True")
        self._send_capslock_passthrough()

    def toggle_mapping(self) -> None:
        with self.state_lock:
            self._enabled = not self._enabled
            snapshot = AppStateSnapshot(
                enabled=self._enabled,
                show_notifications=self._show_notifications,
            )

        self.debug_log(
            f"toggle_mapping enabled={snapshot.enabled} notifications={snapshot.show_notifications} "
            f"caps_on={self.get_capslock_state()} {self.get_foreground_window_info()}"
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

        self.debug_log(
            f"toggle_notifications enabled={snapshot.enabled} notifications={snapshot.show_notifications}"
        )
        self.show_status(
            f"[INFO] Notifications {'enabled' if snapshot.show_notifications else 'disabled'}"
        )
        if self.tray_manager is not None:
            self.tray_manager.request_refresh(snapshot, show_notice=False)

    def on_caps_press(self, event: keyboard.KeyboardEvent) -> None:
        if event.event_type != "down":
            return

        snapshot = self.get_snapshot()
        self.debug_log(
            f"caps_press scan_code={event.scan_code} enabled={snapshot.enabled} "
            f"ctrl_pressed={keyboard.is_pressed('ctrl')} passthrough={self.passthrough_caps.is_set()} "
            f"caps_on={self.get_capslock_state()} {self.get_foreground_window_info()}"
        )

        if self.passthrough_caps.is_set():
            self.debug_log("caps_press ignored because passthrough is active")
            return

        if keyboard.is_pressed("ctrl"):
            self.debug_log("caps_press detected ctrl modifier, toggling mapping")
            self.toggle_mapping()
            return

        if snapshot.enabled:
            self.debug_log("caps_press sending ctrl+space")
            keyboard.send("ctrl+space")
            self.debug_log(
                f"caps_press sent ctrl+space caps_on={self.get_capslock_state()} {self.get_foreground_window_info()}"
            )
            return

        self.debug_log("caps_press mapping disabled, forwarding native caps_lock")
        self._send_capslock_passthrough()

    def install_keyboard_hooks(self) -> None:
        keyboard.on_press_key("caps lock", self.on_caps_press, suppress=True)
        self.debug_log("keyboard hooks installed for caps lock")

    def cleanup(self) -> None:
        self.stop_event.set()
        keyboard.unhook_all()
        self.debug_log("cleanup completed and keyboard hooks removed")
