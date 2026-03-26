import atexit
import sys
import threading
import time

from key_mapper import KeyMapperApp
from tray_icon import TrayManager


def main() -> None:
    app = KeyMapperApp()
    tray_manager = TrayManager(app)
    app.set_tray_manager(tray_manager)
    atexit.register(app.cleanup)

    app.ensure_capslock_off()

    app.show_status("Caps Lock mapper started")
    app.show_status("[ON ] Caps Lock -> Ctrl+Space")
    app.show_status("Toggle: Ctrl+Caps Lock")
    app.show_status("Tray: status and quit menu")
    app.show_status("Exit: Ctrl+C or tray Quit")

    app.install_keyboard_hooks()

    tray_thread = threading.Thread(target=tray_manager.run, daemon=True)
    tray_thread.start()

    try:
        while not app.stop_event.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        app.show_status("Exiting...")
    finally:
        app.cleanup()
        tray_manager.stop()
        sys.exit(0)


if __name__ == "__main__":
    time.sleep(0.1)
    main()
