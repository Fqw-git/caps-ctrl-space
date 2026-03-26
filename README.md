# Caps Lock 输入法切换工具

这个工具在 Windows 下常驻运行：

- 映射启用时：按 `Caps Lock` 会发送一次 `Ctrl + Space`
- 映射关闭时：`Caps Lock` 恢复默认行为
- 按 `Space + Caps Lock` 可以切换映射开关

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

- `Space + Caps Lock`：启用/禁用映射
- `Ctrl + C`：退出程序

## 注意事项

- 该工具依赖全局键盘钩子，部分系统环境下可能需要使用管理员权限启动终端。
- `Ctrl + Space` 是否切换中英文，取决于你当前输入法的快捷键设置；如果你的输入法不是这个组合键，需要在输入法设置中同步调整。
- `Caps Lock` 本身由 Python 键盘钩子处理；当前总开关调整为 `Space + Caps Lock` 用于排查是否是 `Win` 键带来的系统级冲突。
