# Caps Lock 输入法切换工具

这个工具在 Windows 下常驻运行：

- 映射启用时：按 `Caps Lock` 会发送一次 `Ctrl + Space`
- 映射关闭时：`Caps Lock` 恢复默认行为
- 按 `Ctrl + Caps Lock` 可以切换映射开关
- 系统托盘会显示当前映射状态，并提供切换与退出入口

## 运行方式

1. 安装 Python 3.10+
2. 安装依赖：

```powershell
pip install -r requirements.txt
```

3. 启动：

```powershell
python main.py
```

## 控制说明

- `Ctrl + Caps Lock`：启用/禁用映射
- 托盘图标：显示当前状态，右键可切换映射、控制是否弹出通知、或退出
- `Ctrl + C`：退出程序

## 注意事项

- 该工具依赖全局键盘钩子，部分系统环境下可能需要使用管理员权限启动终端。
- `Ctrl + Space` 是否切换中英文，取决于你当前输入法的快捷键设置；如果你的输入法不是这个组合键，需要在输入法设置中同步调整。
- 重新开启映射时，程序会自动检查并关闭已开启的 `Caps Lock` 状态，避免大写锁定残留。
