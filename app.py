import atexit
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

    tray_thread = threading.Thread(target=tray_manager.run, name="tray-icon")
    tray_thread.start()

    try:
        while not app.stop_event.wait(0.2):
            pass
    except KeyboardInterrupt:
        app.show_status("Exiting...")
    finally:
        app.cleanup()
        tray_manager.stop()
        tray_thread.join(timeout=2.0)


if __name__ == "__main__":
    time.sleep(0.1)
    main()
