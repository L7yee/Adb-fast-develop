# 变更与版本记录

应用版本来自对应 commit 中的 `package.json`，不等同于每次提交都发布一个版本。带 `vX.Y.Z` 标签的提交才是本项目已登记的发布版本。下表已通过 Git 历史与 GitHub Releases 核对。

完整、实时的逐次提交记录：在根目录运行 `node electron/scripts/history.js`，或在 `electron/` 运行 `npm run history`。它直接从 Git 读取每个 commit 的版本和标签，也包含这份文件自身的后续提交，避免手工补 hash 形成循环。

## 未发布 · 文档与维护工具

- 2026-10-30：建立本文件、`docs/PROJECT_STATE.md` 和新对话接手流程；增加只读的 commit/版本清单命令，包含早期根目录 `package.json` 的版本读取。
- 应用仍为 2.2.0；本次只修改文档和历史查询工具，不重新打包或发布应用。
- 验证：历史命令与已有 12 个应用提交的版本、3 个发布标签逐一对照；检查命令从根目录与 `electron/` 均可运行，且不会修改工作区。

## 已发布版本

| 版本 | 发布日期 | 源码 commit | 主要改动 | 当次验证 |
| --- | --- | --- | --- | --- |
| [v2.2.0](https://github.com/L7yee/Adb-fast-develop/releases/tag/v2.2.0) | 2026-10-28 | [2633749](https://github.com/L7yee/Adb-fast-develop/commit/2633749) | 屏幕概览显示分辨率、Panel、LCD ID、DDI；接入读取一次、手动刷新和来源提示；兼容 cmdline、bootconfig、属性及常见屏幕节点 | 9 项测试、界面检查及 Unisoc 实机读取；两种发行文件上传后核对大小与 SHA256 |
| [v2.1.2](https://github.com/L7yee/Adb-fast-develop/releases/tag/v2.1.2) | 2026-10-27 | [89260be](https://github.com/L7yee/Adb-fast-develop/commit/89260be) | 所需 DPI 时钟数值和单位改为 Hz | 6 项测试、界面检查；默认样例 191,289,600 Hz；发行文件校验 |
| [v2.1.1](https://github.com/L7yee/Adb-fast-develop/releases/tag/v2.1.1) | 2026-10-26 | [82868d0](https://github.com/L7yee/Adb-fast-develop/commit/82868d0) | 将每次启动解压的便携 EXE 改为只需解压一次的 ZIP；首次在 GitHub Release 提供安装包和便携 ZIP | 6 项测试、ZIP 内容和包内版本检查；发行文件校验 |

## 早期提交 · 未建立发布标签

这些版本号在源码中存在，但没有对应 Git 发布标签，不能据此声称它们曾发布到 GitHub Release。

| 日期 | 应用版本 | Commit | 改动 |
| --- | --- | --- | --- |
| 2026-10-26 | 2.1.0 | [30ca3f9](https://github.com/L7yee/Adb-fast-develop/commit/30ca3f9) | 调整自解压便携包压缩方式以缩短解压耗时；该发行形式已被 v2.1.1 的 ZIP 替代 |
| 2026-10-26 | 2.1.0 | [bdda1c2](https://github.com/L7yee/Adb-fast-develop/commit/bdda1c2) | 点击整张指令卡片执行；设备接入后自动尝试一次 adb root，并复查连接状态 |
| 2026-10-24 | 2.1.0 | [86138b6](https://github.com/L7yee/Adb-fast-develop/commit/86138b6) | 参考 Figma 页面建立深色双栏侧边导航；折叠、搜索、工具入口和界面回归检查 |
| 2026-10-22 | 2.1.0 | [b63e888](https://github.com/L7yee/Adb-fast-develop/commit/b63e888) | 移植 MIPI CLK 计算表，添加计算器 |
| 2026-10-22 | 2.0.0 | [a6c055e](https://github.com/L7yee/Adb-fast-develop/commit/a6c055e) | 旧目标 SDK APK 安装失败时，使用 --bypass-low-target-sdk-block 重试一次 |
| 2026-10-22 | 2.0.0 | [76c35b8](https://github.com/L7yee/Adb-fast-develop/commit/76c35b8) | APK 安装加入 -g 授予运行时权限 |
| 2026-10-22 | 2.0.0 | [6637b92](https://github.com/L7yee/Adb-fast-develop/commit/6637b92) | 取消指令实时监控，改为单次执行；日志分为 dmesg、logcat -d，并各自持久化保存路径 |
| 2026-10-21 | 2.0.0 | [4740f8f](https://github.com/L7yee/Adb-fast-develop/commit/4740f8f) | Electron 迁入 electron/，Python 归档至 legacy-python/，采用 MIT 开源 |
| 2026-10-21 | 2.0.0 | [5a4ba22](https://github.com/L7yee/Adb-fast-develop/commit/5a4ba22) | 初次迁移为 Electron；当时 package.json 位于仓库根目录 |

## 后续记录规则

1. 每次修改先写明目的、实际行为和已完成的验证；未验证、未发布或失败的步骤明确标出。
2. 普通提交归入“未发布”，Git 自动保存 commit 与当时的版本；历史命令可随时查阅，无需手填当前提交自身的 hash。
3. 发布应用时，先核对版本和锁文件，再登记 `vX.Y.Z`、源码 commit、Release 链接、下载文件与验证结果。GitHub 可保留多个历史 Release，本地 dist 按用户偏好保留当前发行文件。
4. 文档更新通常沿用当前应用版本，不为记录本身额外生成安装包。
