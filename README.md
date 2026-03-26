# caps-ctrl-space

一个运行在 Windows 下的小工具，用于将 `Caps Lock` 映射为 `Ctrl + Space`，并通过 `Ctrl + Caps Lock` 快速启用或禁用映射。

这个工具主要面向中文输入场景，适合希望获得类似 iOS 单键中英文切换体验的用户；同时也支持临时关闭映射，以便在游戏或其他特殊场景下恢复原始 `Caps Lock` 行为。

## 中文说明

### 功能特性

- 映射启用时，按下 `Caps Lock` 会发送 `Ctrl + Space`
- 映射关闭时，`Caps Lock` 恢复默认行为
- 按下 `Ctrl + Caps Lock` 可以切换映射开关
- 系统托盘图标会显示当前状态
- 托盘菜单支持：
  - 切换映射状态
  - 控制是否显示通知弹窗
  - 退出程序
- 程序启动时，如果 `Caps Lock` 已经处于开启状态，会自动关闭
- 重新启用映射时，如果 `Caps Lock` 仍处于开启状态，也会自动关闭，避免大写锁定残留

### 运行环境

- Windows
- Python 3.10+

### 安装依赖

```powershell
pip install -r requirements.txt
```

### 启动方式

```powershell
python app.py
```

### 操作说明

- `Caps Lock`：在映射开启时发送 `Ctrl + Space`
- `Ctrl + Caps Lock`：切换映射开关
- 托盘图标：显示当前状态，右键可切换映射、控制通知或退出
- `Ctrl + C`：在终端中退出程序

### 项目结构

- `app.py`：程序入口
- `key_mapper.py`：键盘映射与状态管理逻辑
- `tray_icon.py`：托盘图标、菜单与通知逻辑

### 打包 EXE

如果你希望生成可直接分发的 `exe` 文件，可以使用 `PyInstaller`：

```powershell
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name caps-ctrl-space --exclude-module numpy --exclude-module matplotlib --exclude-module pandas --exclude-module scipy app.py
```

打包完成后，生成的文件位于：

```powershell
dist\caps-ctrl-space.exe
```

### 注意事项

- 本工具依赖全局键盘钩子，部分环境下可能需要以管理员权限运行终端。
- `Ctrl + Space` 是否能够切换中英文，取决于你当前输入法的快捷键设置；如果你的输入法使用了其他快捷键，需要先在输入法中进行调整。

---

## English

A small Windows background tool that remaps `Caps Lock` to `Ctrl + Space` and lets you toggle the remapping with `Ctrl + Caps Lock`.

This project is mainly designed for Chinese input workflows. It aims to provide a one-key Chinese/English input toggle experience similar to iOS, while still allowing you to temporarily restore the original `Caps Lock` behavior for games or other scenarios.

### Features

- When mapping is enabled, pressing `Caps Lock` sends `Ctrl + Space`
- When mapping is disabled, `Caps Lock` works normally
- Press `Ctrl + Caps Lock` to toggle the mapping on or off
- Tray icon shows the current state
- Tray menu lets you:
  - toggle mapping
  - enable or disable notification popups
  - quit the app
- On startup, the app automatically turns off `Caps Lock` if it is already active
- When mapping is turned back on, the app also clears any active `Caps Lock` state

### Requirements

- Windows
- Python 3.10+

### Installation

```powershell
pip install -r requirements.txt
```

### Run

```powershell
python app.py
```

### Controls

- `Caps Lock`: send `Ctrl + Space` when mapping is enabled
- `Ctrl + Caps Lock`: toggle mapping
- Tray icon: show current state, toggle mapping, control notifications, or quit
- `Ctrl + C`: quit from terminal

### Project Structure

- `app.py`: application entry point
- `key_mapper.py`: keyboard mapping and state management
- `tray_icon.py`: tray icon, menu, and notification handling

### Build EXE

If you want to generate a standalone `exe`, you can use `PyInstaller`:

```powershell
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name caps-ctrl-space --exclude-module numpy --exclude-module matplotlib --exclude-module pandas --exclude-module scipy app.py
```

After the build completes, the executable will be available at:

```powershell
dist\caps-ctrl-space.exe
```

### Notes

- The tool depends on a global keyboard hook. In some environments, running the terminal as administrator may be required.
- Whether `Ctrl + Space` switches your input method depends on your IME settings. If your current IME uses a different shortcut, adjust the IME configuration first.
