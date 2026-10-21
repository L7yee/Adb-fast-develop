# 旧版 Python/PyQt 实现

此目录保存迁移前的 Python 版本。当前项目的主要应用及发布流程位于 [`../electron/`](../electron/)。

旧版源码位于 `adb_dashboard/`，原有入口为 `run.py`。如需单独运行旧版，需 Python 3.13、PyQt6、PyYAML 和系统 `PATH` 中的 `adb`：

```powershell
cd legacy-python
pip install -r requirements.txt
python run.py
```

历史开发记录保留在 `.harness/`。此目录的源码同样遵循仓库根目录的 MIT 许可证。
