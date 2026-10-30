# 项目接手说明

最后人工整理：2026-10-30。此文件记录当前状态和长期决策；完整修改历史见 [CHANGELOG.md](../CHANGELOG.md)。接手时先核对实际 Git 状态，不把这里的日期当成文件永远有效的保证。

## 当前基线

| 项目 | 当前记录 |
| --- | --- |
| 本机源码 | `E:\workplace\项目\adb_dashboard`；其他机器以实际检出目录为准 |
| GitHub | https://github.com/L7yee/Adb-fast-develop，公开仓库，MIT |
| 主分支 | main |
| 应用版本 | 2.2.0，见 electron/package.json 和 package-lock.json 根版本 |
| 最新应用发布 | [v2.2.0](https://github.com/L7yee/Adb-fast-develop/releases/tag/v2.2.0) |
| 该发布的源码 | 263374933de1d4d4ca89d67a5380cb938127920c |
| 最近一次应用验证 | 9 项测试、Electron 界面检查、Unisoc 实机屏幕信息读取、打包及远程资产校验通过（2026-10-28） |
| 当前工作 | 跨对话记录流程已建立；应用功能没有待实施的新需求，后续以新请求为准 |

上表的源码 hash 指最后一个应用 Release，文档提交会在它之后。当前仓库 HEAD 和每次 commit 的版本请运行 `node electron/scripts/history.js`，不要为保持上表而反复补写文档提交自身的 hash。

## 已确定的产品行为

- 当前应用只使用 Electron，Python/PyQt 仅保留在 `legacy-python/`，不为 Electron 引入 Python 依赖。
- 深色双栏导航参考页面：https://chain-evade-33063161.figma.site/ 。命令、日志、工具弹窗均已接入，不要恢复早期浅色界面。
- 指令每次点击整张卡片执行一次，保留编辑菜单；用户明确取消实时监控和卡片上的独立运行按钮。
- 设备接入后自动尝试一次 `adb root` 并复查状态。现有实现容忍 root 重启导致的短暂掉线，连续 3 次未检测到设备后允许下次接入重新尝试；设备检测间隔为 5 秒。
- 日志工作区分内核 `dmesg` 与 `logcat -d`，各自保存可编辑的绝对路径，再次写同一路径会覆盖旧文件。
- APK 默认 `adb -s SERIAL install -r -g FILE`；仅遇到 `INSTALL_FAILED_DEPRECATED_SDK_VERSION` 时加 `--bypass-low-target-sdk-block` 重试一次。`-g` 是 adb install 参数，不是 npm 打包参数。
- MIPI CLK 计算器来自用户的 `104269__MIPI CLK计算表.xlsx`。所需 DPI 时钟显示 Hz，DPI 时钟源输入和 MIPI CLK 输出仍是 MHz；样例所需 DPI 时钟为 191,289,600 Hz。
- 屏幕概览连接后读取一次，可手动重新读取；优先解析 `/proc/cmdline` 的 `lcd_name`、`lcd_id` 等，再尝试 bootconfig、属性及常见 sysfs 节点。字段保留来源；物理/覆盖分辨率分开，断开或切换设备后清空旧值。
- DDI 需要实际来源；不能把 LCD ID、触控芯片型号或设备树的第一个候选 Panel 当成已识别的 DDI。

## 发行与用户数据

- 构建入口：`electron/` 中 `npm run dist`，生成安装版 EXE 和便携 ZIP；便携 ZIP 解压一次后运行文件夹内的 `ADB Dashboard.exe`。
- `electron/dist/win-unpacked/ADB Dashboard.exe` 是已经解压的完整应用的一部分，启动快，不能只拿这一个 EXE 脱离旁边文件运行。
- 早期 `ADB Dashboard 2.1.0.exe` 是每次启动都解压的自解压便携包，已停用这种发行方式。
- dist、node_modules 被 Git 忽略，代码页看不到安装包是正常的；安装包在 GitHub Releases。Release 允许版本迭代，用户期望本地 dist 只保留当前发行文件。
- 历史本机旧包/测速目录的清理曾被自动审批拦下。打包不会自动清除旧版本；接手时实际检查，不宣称已经清理，也不把过去的审批结果当成永久权限规则。
- productName 为 ADB Dashboard，appId 为 `dev.l7yee.adbdashboard`；保持应用身份稳定，以便覆盖升级。
- 自定义命令、窗口设置、日志路径存放在 Electron userData，分别对应 commands.yaml、window.json、log-paths.json。不要把用户配置替换为内置默认文件。
- GitHub 认证使用本机已有 Git 凭据；不要向用户索取私钥，也不要把 token、密钥或真实设备序列号写入交接文档。

## 代码入口与验证

| 文件 | 作用 |
| --- | --- |
| electron/main.js | 窗口、设备接入、自动 root、IPC |
| electron/adb.js | 设备检测、ADB 进程、APK 兼容重试 |
| electron/display-info.js | 屏幕信息采集、来源优先级、解析 |
| electron/config.js | YAML 命令迁移、校验与用户数据持久化 |
| electron/preload.js | 隔离的渲染进程 API |
| electron/renderer/app.js、index.html、dark.css | 界面行为、内容和当前深色样式 |
| electron/renderer/mipi-clock.js | MIPI 计算公式 |
| electron/tests/ | 单元测试和 visual-smoke.js 界面检查 |

根目录读取记录：`node electron/scripts/history.js`。应用开发在 `electron/` 中进行：`npm ci`、`npm start`、`npm test`。涉及界面时运行 `npx electron tests/visual-smoke.js`；需要实体设备才能完成的检查应注明是否已实测。界面检查会生成 preview.png 和 preview-logs.png，提交前只保留本次有意义的预览变化。

## 接手顺序与已知限制

1. 读 AGENTS.md、本文件、CHANGELOG.md，检查工作区，运行历史命令；核对当前需求是否已完成。
2. 涉及某个模块再阅读其代码；依照当前会话授权做最小改动，并记录真实验证结果。
3. 完成后更新记录、提交并推送；应用发布核对标签、包内版本及 GitHub Release 资产，再告知用户。

屏幕节点存在厂商差异，当前仅在一台 Unisoc 设备验证了 1600×2400、Panel `lcd_jt122wqh009_mipi_wqxga2400` 和 LCD ID `ID122015`。该机 DDI 未识别，跨平台解析有测试样例，但不等于所有平台均已实机验证。进一步兼容时依据用户设备的实际接口补充，避免猜测。
