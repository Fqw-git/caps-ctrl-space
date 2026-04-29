import queue
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

import pystray
from PIL import Image

from key_mapper import AppStateSnapshot


@dataclass(frozen=True)
class TrayRefreshRequest:
    snapshot: AppStateSnapshot
    show_notice: bool = False


class TrayManager:
    def __init__(self, app) -> None:
        self.app = app
        self.icon: pystray.Icon | None = None
        self.command_queue: queue.Queue[TrayRefreshRequest | None] = queue.Queue()
        self.stop_requested = threading.Event()
        self.icon_dir = self.get_resource_dir() / "icons"
        self.active_icon_path = self.icon_dir / "on.png"
        self.inactive_icon_path = self.icon_dir / "off.png"
        self._icon_cache: dict[bool, Image.Image] = {}

    def get_resource_dir(self) -> Path:
        if getattr(sys, "frozen", False):
            return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        return Path(__file__).resolve().parent

    def load_image(self, path: Path) -> Image.Image:
        with Image.open(path) as image:
            return image.convert("RGBA").copy()

    def build_image(self, active: bool) -> Image.Image:
        if active not in self._icon_cache:
            path = self.active_icon_path if active else self.inactive_icon_path
            self._icon_cache[active] = self.load_image(path)

        return self._icon_cache[active].copy()

    def current_status_text(self, active: bool) -> str:
        return "Caps Mapper: ON" if active else "Caps Mapper: OFF"

    def request_refresh(self, snapshot: AppStateSnapshot, show_notice: bool = False) -> None:
        if self.stop_requested.is_set():
            return

        self.command_queue.put(TrayRefreshRequest(snapshot, show_notice))

    def apply_refresh(self, request: TrayRefreshRequest) -> None:
        if self.icon is None:
            return

        self.icon.icon = self.build_image(request.snapshot.enabled)
        self.icon.title = self.current_status_text(request.snapshot.enabled)
        self.icon.update_menu()

        if request.show_notice and request.snapshot.show_notifications:
            message = (
                "Caps Lock -> Ctrl+Space enabled"
                if request.snapshot.enabled
                else "Caps Lock restored"
            )
            try:
                self.icon.notify(message, "Caps Mapper")
            except Exception:
                pass

    def process_commands(self, icon: pystray.Icon) -> None:
        icon.visible = True

        while not self.stop_requested.is_set():
            try:
                request = self.command_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if request is None:
                break

            self.apply_refresh(request)

    def on_toggle_mapping(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        del icon, item
        self.app.toggle_mapping()

    def on_toggle_notifications(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        del icon, item
        self.app.toggle_notifications()

    def on_quit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        del icon, item
        self.app.stop_event.set()
        self.stop()

    def notifications_checked(self, item: pystray.MenuItem) -> bool:
        del item
        return self.app.get_snapshot().show_notifications

    def create_icon(self) -> pystray.Icon:
        snapshot = self.app.get_snapshot()
        menu = pystray.Menu(
            pystray.MenuItem("Toggle Mapping", self.on_toggle_mapping),
            pystray.MenuItem("Show Notifications", self.on_toggle_notifications, checked=self.notifications_checked),
            pystray.MenuItem("Quit", self.on_quit),
        )
        return pystray.Icon(
            "caps_mapper",
            self.build_image(snapshot.enabled),
            self.current_status_text(snapshot.enabled),
            menu,
        )

    def run(self) -> None:
        self.icon = self.create_icon()
        self.icon.run(setup=self.process_commands)

    def stop(self) -> None:
        if self.stop_requested.is_set():
            return

        self.stop_requested.set()
        self.command_queue.put(None)

        if self.icon is not None:
            try:
                self.icon.stop()
            except Exception:
                pass
