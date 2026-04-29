import atexit
import argparse
import threading
import time
from pathlib import Path

from key_mapper import KeyMapperApp
from tray_icon import TrayManager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Caps Lock mapper")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug logging to caps_mapper_debug.log",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    debug_log_path = Path(__file__).with_name("caps_mapper_debug.log") if args.debug else None

    if debug_log_path is not None:
        debug_log_path.write_text("", encoding="utf-8")

    app = KeyMapperApp(debug_enabled=args.debug, debug_log_path=debug_log_path)
    tray_manager = TrayManager(app)
    app.set_tray_manager(tray_manager)
    atexit.register(app.cleanup)

    app.ensure_capslock_off()

    app.show_status("Caps Lock mapper started")
    app.show_status("[ON ] Caps Lock -> Ctrl+Space")
    app.show_status("Toggle: Ctrl+Caps Lock")
    app.show_status("Tray: status and quit menu")
    app.show_status("Exit: Ctrl+C or tray Quit")
    if args.debug:
        app.show_status(f"Debug: logging to {debug_log_path}")
        app.debug_log("debug logging enabled")

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
