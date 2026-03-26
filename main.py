import atexit
import ctypes
import sys
import threading
import time

import keyboard


user32 = ctypes.windll.user32
VK_CAPITAL = 0x14

enabled = True
passthrough_caps = False
state_lock = threading.Lock()


def show_status(message: str) -> None:
    print(message, flush=True)


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


def cleanup() -> None:
    keyboard.unhook_all()


def main() -> None:
    atexit.register(cleanup)

    show_status("Caps Lock mapper started")
    show_status("[ON ] Caps Lock -> Ctrl+Space")
    show_status("Toggle: Ctrl+Caps Lock")
    show_status("Exit: Ctrl+C")

    keyboard.on_press_key("caps lock", on_caps_press, suppress=True)

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        show_status("Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    # Let the console finish initialization before installing hooks.
    time.sleep(0.1)
    main()
