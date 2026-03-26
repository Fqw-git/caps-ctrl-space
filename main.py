import atexit
import ctypes
import sys
import threading
import time

import keyboard
import pystray
from PIL import Image, ImageDraw


user32 = ctypes.windll.user32
VK_CAPITAL = 0x14

enabled = True
show_notifications = False
passthrough_caps = False
state_lock = threading.Lock()
stop_event = threading.Event()
tray_icon = None


def show_status(message: str) -> None:
    print(message, flush=True)


def build_tray_image(active: bool) -> Image.Image:
    size = 64
    image = Image.new("RGB", (size, size), (24, 24, 24))
    draw = ImageDraw.Draw(image)

    accent = (34, 197, 94) if active else (107, 114, 128)
    text = "A" if active else "C"

    draw.rounded_rectangle((6, 6, 58, 58), radius=14, fill=(40, 40, 40), outline=accent, width=4)
    draw.text((22, 14), text, fill=accent)
    draw.rectangle((14, 42, 50, 48), fill=accent)
    return image


def current_status_text() -> str:
    return "Caps Mapper: ON" if enabled else "Caps Mapper: OFF"


def refresh_tray(show_notice: bool = False) -> None:
    if tray_icon is None:
        return

    with state_lock:
        current = enabled
        notifications_enabled = show_notifications

    tray_icon.icon = build_tray_image(current)
    tray_icon.title = current_status_text()
    tray_icon.update_menu()

    if show_notice and notifications_enabled:
        message = "Caps Lock -> Ctrl+Space enabled" if current else "Caps Lock restored"
        try:
            tray_icon.notify(message, "Caps Mapper")
        except Exception:
            pass


def ensure_capslock_off() -> None:
    global passthrough_caps

    if not (user32.GetKeyState(VK_CAPITAL) & 0x0001):
        return

    passthrough_caps = True
    try:
        keyboard.send("caps lock")
    finally:
        passthrough_caps = False


def toggle_mapping() -> None:
    global enabled

    with state_lock:
        enabled = not enabled
        current = enabled

    if current:
        ensure_capslock_off()

    if current:
        show_status("[ON ] Caps Lock -> Ctrl+Space")
    else:
        show_status("[OFF] Caps Lock restored")

    refresh_tray(show_notice=True)


def on_caps_press(event: keyboard.KeyboardEvent) -> None:
    global passthrough_caps

    if event.event_type != "down":
        return

    if passthrough_caps:
        return

    if keyboard.is_pressed("ctrl"):
        toggle_mapping()
        return

    with state_lock:
        current = enabled

    if current:
        keyboard.send("ctrl+space")
        return

    passthrough_caps = True
    try:
        keyboard.send("caps lock")
    finally:
        passthrough_caps = False


def on_toggle_from_tray(icon: pystray.Icon, item: pystray.MenuItem) -> None:
    del icon, item
    toggle_mapping()


def on_toggle_notifications(icon: pystray.Icon, item: pystray.MenuItem) -> None:
    global show_notifications
    del icon, item

    with state_lock:
        show_notifications = not show_notifications
        current = show_notifications

    show_status(f"[INFO] Notifications {'enabled' if current else 'disabled'}")
    refresh_tray(show_notice=False)


def on_quit_from_tray(icon: pystray.Icon, item: pystray.MenuItem) -> None:
    del item
    stop_event.set()
    icon.stop()


def notifications_checked(item: pystray.MenuItem) -> bool:
    del item
    with state_lock:
        return show_notifications


def create_tray_icon() -> pystray.Icon:
    menu = pystray.Menu(
        pystray.MenuItem("Toggle Mapping", on_toggle_from_tray),
        pystray.MenuItem("Show Notifications", on_toggle_notifications, checked=notifications_checked),
        pystray.MenuItem("Quit", on_quit_from_tray),
    )
    return pystray.Icon("caps_mapper", build_tray_image(enabled), current_status_text(), menu)


def run_tray_icon() -> None:
    global tray_icon

    tray_icon = create_tray_icon()
    tray_icon.run()


def cleanup() -> None:
    stop_event.set()
    keyboard.unhook_all()
    if tray_icon is not None:
        try:
            tray_icon.stop()
        except Exception:
            pass


def main() -> None:
    atexit.register(cleanup)

    ensure_capslock_off()

    show_status("Caps Lock mapper started")
    show_status("[ON ] Caps Lock -> Ctrl+Space")
    show_status("Toggle: Ctrl+Caps Lock")
    show_status("Tray: status and quit menu")
    show_status("Exit: Ctrl+C or tray Quit")

    keyboard.on_press_key("caps lock", on_caps_press, suppress=True)

    tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
    tray_thread.start()

    try:
        while not stop_event.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        show_status("Exiting...")
    finally:
        cleanup()
        sys.exit(0)


if __name__ == "__main__":
    time.sleep(0.1)
    main()
