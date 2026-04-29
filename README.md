# caps-ctrl-space

A small Windows background utility that remaps `Caps Lock` to `Ctrl + Space`, and lets you toggle the remapping with `Ctrl + Caps Lock`.

This project is mainly designed for Chinese input workflows. It aims to provide a one-key Chinese/English input toggle experience similar to iOS, while still allowing you to temporarily restore the original `Caps Lock` behavior for games or other scenarios.

## 中文说明

### 功能特性

- 映射开启时，按下 `Caps Lock` 会发送 `Ctrl + Space`
- 映射关闭时，`Caps Lock` 恢复默认行为
- 按下 `Ctrl + Caps Lock` 可以切换映射开关
- 系统托盘图标显示当前状态
- 托盘菜单支持：
  - 切换映射状态
  - 控制是否显示通知弹窗
  - 退出程序
- 程序启动时，如果 `Caps Lock` 已经处于开启状态，会自动将其关闭
- 重新启用映射时，如果 `Caps Lock` 仍处于开启状态，也会自动关闭
- 支持 `--debug` 调试模式，便于定位某些软件中按键映射失效的问题

### 运行环境

- Windows
- Python 3.10+

### 安装依赖

```powershell
pip install -r requirements.txt
```

### 启动方式

正常启动：

```powershell
python app.py
```

启用调试日志：

```powershell
python app.py --debug
```

启用 `--debug` 后，程序会在项目根目录生成：

```text
caps_mapper_debug.log
```

日志中会记录：

- 是否捕获到了 `Caps Lock` 按键事件
- 当前映射状态
- 是否检测到了 `Ctrl`
- 当前前台窗口的标题、类名和进程 ID
- 是否执行了 `Ctrl + Space` 发送逻辑

### 操作说明

- `Caps Lock`：映射开启时发送 `Ctrl + Space`
- `Ctrl + Caps Lock`：切换映射开关
- 托盘图标：显示当前状态，可切换映射、控制通知或退出
- `Ctrl + C`：在终端中退出程序

### 管理员权限说明

本工具依赖全局键盘 hook。

如果目标软件以管理员权限运行，而本工具不是管理员权限运行，`Caps Lock` 映射可能在该软件中失效。这不是项目逻辑问题，而是 Windows 权限边界导致的行为。

如果你在某些软件中发现映射失效，请优先检查：

- 目标软件是否以管理员权限运行
- 当前终端或打包后的 exe 是否也以管理员权限运行

### 项目结构

- `app.py`：程序入口
- `key_mapper.py`：键盘映射、状态管理与调试日志逻辑
- `tray_icon.py`：托盘图标、菜单与通知逻辑
- `build.ps1`：Windows 打包脚本

### 打包 EXE

推荐直接使用项目内置脚本：

```powershell
.\build.ps1
```

如果当前环境还没有安装 `PyInstaller`：

```powershell
.\build.ps1 -InstallPyInstaller
```

如果你使用的是特定 Python 或 conda 环境中的解释器，也可以显式指定：

```powershell
.\build.ps1 -Python "C:\path\to\python.exe"
```

打包脚本会：

- 使用 `PyInstaller`
- 生成单文件、无控制台窗口的 exe
- 自动添加管理员权限请求（`--uac-admin`）
- 将最终产物复制到项目根目录
- 清理 `build/`、`dist/` 和 `.spec` 中间产物

最终生成的文件位于：

```text
caps-ctrl-space.exe
```

### 注意事项

- 某些环境下，运行终端或 exe 可能需要管理员权限
- `Ctrl + Space` 是否能够切换中英文，取决于你当前输入法的快捷键设置
- 某些使用更底层输入处理方式的软件，可能不会被常规全局键盘 hook 正常捕获

---

## English

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
- Supports `--debug` mode for diagnosing cases where key mapping fails in specific applications

### Requirements

- Windows
- Python 3.10+

### Installation

```powershell
pip install -r requirements.txt
```

### Run

Normal run:

```powershell
python app.py
```

Run with debug logging:

```powershell
python app.py --debug
```

When `--debug` is enabled, the app writes a log file in the project root:

```text
caps_mapper_debug.log
```

The debug log records:

- whether the `Caps Lock` key event was captured
- current mapping state
- whether `Ctrl` was detected
- foreground window title, class name, and process ID
- whether the `Ctrl + Space` send path was executed

### Controls

- `Caps Lock`: send `Ctrl + Space` when mapping is enabled
- `Ctrl + Caps Lock`: toggle mapping
- Tray icon: show current state, toggle mapping, control notifications, or quit
- `Ctrl + C`: quit from terminal

### Administrator Privileges

This tool depends on a global keyboard hook.

If the target application is running as administrator while this tool is not, the `Caps Lock` remapping may stop working inside that application. This is a Windows privilege boundary issue rather than an application logic bug.

If remapping fails only in some applications, first check:

- whether the target app is running as administrator
- whether this tool is also running as administrator

### Project Structure

- `app.py`: application entry point
- `key_mapper.py`: keyboard mapping, state management, and debug logging
- `tray_icon.py`: tray icon, menu, and notification handling
- `build.ps1`: Windows build script

### Build EXE

Recommended:

```powershell
.\build.ps1
```

If `PyInstaller` is not installed yet:

```powershell
.\build.ps1 -InstallPyInstaller
```

If you want to use a specific Python interpreter, including one from a conda environment:

```powershell
.\build.ps1 -Python "C:\path\to\python.exe"
```

The build script will:

- use `PyInstaller`
- build a single-file windowed executable
- request administrator privileges automatically via `--uac-admin`
- copy the final exe to the project root
- clean intermediate `build/`, `dist/`, and `.spec` artifacts

Final output:

```text
caps-ctrl-space.exe
```

### Notes

- In some environments, the terminal or packaged exe must be run as administrator
- Whether `Ctrl + Space` switches your input method depends on your IME settings
- Some applications using lower-level input handling may not expose key events to ordinary global keyboard hooks
