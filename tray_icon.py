import pystray
from PIL import Image, ImageDraw


class TrayManager:
    def __init__(self, app) -> None:
        self.app = app
        self.icon = None

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

    def current_status_text(self) -> str:
        return "Caps Mapper: ON" if self.app.enabled else "Caps Mapper: OFF"

    def refresh(self, show_notice: bool = False) -> None:
        if self.icon is None:
            return

        with self.app.state_lock:
            current = self.app.enabled
            notifications_enabled = self.app.show_notifications

        self.icon.icon = self.build_image(current)
        self.icon.title = self.current_status_text()
        self.icon.update_menu()

        if show_notice and notifications_enabled:
            message = "Caps Lock -> Ctrl+Space enabled" if current else "Caps Lock restored"
            try:
                self.icon.notify(message, "Caps Mapper")
            except Exception:
                pass

    def on_toggle_mapping(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        del icon, item
        self.app.toggle_mapping()

    def on_toggle_notifications(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        del icon, item
        self.app.toggle_notifications()

    def on_quit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        del item
        self.app.stop_event.set()
        icon.stop()

    def notifications_checked(self, item: pystray.MenuItem) -> bool:
        del item
        with self.app.state_lock:
            return self.app.show_notifications

    def create_icon(self) -> pystray.Icon:
        menu = pystray.Menu(
            pystray.MenuItem("Toggle Mapping", self.on_toggle_mapping),
            pystray.MenuItem("Show Notifications", self.on_toggle_notifications, checked=self.notifications_checked),
            pystray.MenuItem("Quit", self.on_quit),
        )
        return pystray.Icon("caps_mapper", self.build_image(self.app.enabled), self.current_status_text(), menu)

    def run(self) -> None:
        self.icon = self.create_icon()
        self.icon.run()

    def stop(self) -> None:
        if self.icon is not None:
            try:
                self.icon.stop()
            except Exception:
                pass
