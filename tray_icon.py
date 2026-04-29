import queue
import threading
from dataclasses import dataclass

import pystray
from PIL import Image, ImageDraw

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

    def build_image(self, active: bool) -> Image.Image:
        size = 64
        image = Image.new("RGB", (size, size), (24, 24, 24))
        draw = ImageDraw.Draw(image)

        accent = (34, 197, 94) if active else (107, 114, 128)
        text = "A" if active else "C"

        draw.rounded_rectangle((6, 6, 58, 58), radius=14, fill=(40, 40, 40), outline=accent, width=4)
        draw.text((22, 14), text, fill=accent)
        draw.rectangle((14, 42, 50, 48), fill=accent)
        return image

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
