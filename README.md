# ADB Dashboard

基于 Electron 的 Android 调试桌面工具，界面采用简洁的 macOS 风格。运行不需要 Python。

关联仓库：[L7yee/Adb-fast-develop](https://github.com/L7yee/Adb-fast-develop)。

## 开始使用

准备 Node.js 20.19+、npm 和 Android SDK Platform Tools。确保 `adb` 已加入系统 `PATH`，并在手机上开启 USB 调试。

```powershell
npm install
npm start
```

也可以在安装依赖后双击 `启动ADB Dashboard.bat`。打包 Windows 安装版和便携版：

```powershell
npm run dist
```

## 功能

- 检测设备连接与 Root 状态；当前按原版规则一次使用一台设备。
- 运行读取、操作和实时输出命令；支持停止、自动刷新（1/5/10/30 秒）、结果对比。
- 添加、编辑、删除和拖动排序命令；安装 APK；保存或复制输出；转换 Init Cmd。
- `Ctrl+1` 到 `Ctrl+0` 运行前十条命令，`Ctrl+R` 刷新设备，`Ctrl+S` 保存输出，`Esc` 停止。

首次运行会把 `config/commands.yaml` 复制到 Electron 用户数据目录，之后的编辑只保存在用户数据目录。打包版因此可以正常保存命令，并保留原项目的默认配置。窗口位置也保存在用户数据目录。

旧 Python/PyQt 实现已移到 `legacy-python/` 作为迁移备份；新的启动脚本与打包流程只运行 Electron，不调用 Python。现有目录没有 `.git` 元数据，因此这里未创建提交或推送到关联仓库。
