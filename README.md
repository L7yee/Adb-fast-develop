# ADB Dashboard

一款基于 Electron 的开源 Android ADB 调试桌面工具。当前维护的应用位于 [`electron/`](electron/)，采用简洁的 macOS 风格界面；旧版 Python/PyQt 源码完整归档于 [`legacy-python/`](legacy-python/)。

## 目录

```text
adb_dashboard/
├─ electron/              # 当前应用、配置、测试、资源和 Windows 启动脚本
│  ├─ renderer/            # 界面
│  ├─ config/              # 内置命令
│  ├─ resources/           # 图标
│  ├─ scripts/             # 开发辅助脚本
│  └─ tests/               # 自动测试与界面检查
├─ legacy-python/         # 旧版 Python/PyQt 源码，仅供查阅或独立运行
├─ LICENSE                # MIT 许可证
└─ README.md
```

## 运行 Electron 版

需要 Node.js 22.12+、npm 和 Android SDK Platform Tools，并将 `adb` 加入系统 `PATH`。在手机上开启 USB 调试后运行：

```powershell
cd electron
npm ci
npm start
```

Windows 下也可以在安装依赖后双击 `electron/启动ADB Dashboard.bat`。生成 Windows 安装版和便携版：

```powershell
cd electron
npm run dist
```

产物位于 `electron/dist/`，此目录不会提交到 Git。应用默认命令来自 `electron/config/commands.yaml`；首次运行后，用户修改的命令与窗口设置保存在 Electron 用户数据目录。

## 功能

- 检测设备连接和 Root 状态，一次操作一台设备。
- 运行读取、操作和实时输出命令，支持停止、自动刷新、结果对比。
- 添加、编辑、删除及排序命令，安装 APK，保存或复制输出，转换 Init Cmd。
- `Ctrl+1` 至 `Ctrl+0` 运行前十条命令，`Ctrl+R` 刷新设备，`Ctrl+S` 保存输出，`Esc` 停止。

## 开源协议

项目源码，包括 `electron/` 与 `legacy-python/`，以 [MIT 许可证](LICENSE) 开源。第三方依赖遵循各自的许可证。关联仓库：[L7yee/Adb-fast-develop](https://github.com/L7yee/Adb-fast-develop)。
