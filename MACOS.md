# macOS 使用说明

## 从源码启动

需要 macOS 12 或更新版本，以及 Python 3.10 或更新版本。

```sh
python3 -m pip install -r requirements-desktop.txt
python3 desktop.py
```

也可在安装依赖后双击 `start-dashboard.command`。桌面窗口使用系统 WebKit；软件只在本机 `127.0.0.1` 启动内部服务。

## 使用打包程序

在 macOS 上运行 `python3 -m pip install -r requirements-build.txt` 后，执行 `./build-macos.sh`。构建结果是按当前 Mac 架构生成的 ZIP，其中包含 `CodexTokenDesktop.app`。完整解压后可打开该应用。Intel Mac 与 Apple 芯片 Mac 应分别使用 `x86_64` 与 `arm64` 包。

当前构建未进行 Apple Developer ID 签名或公证。macOS 可能要求用户在系统界面中自行确认来自未识别开发者的应用。

## 数据与配置

- 默认读取 `~/.codex/sessions` 和 `~/.codex/archived_sessions` 中的本机日志。
- 数据库和界面偏好保存在 `~/Library/Application Support/CodexTokenDashboard/`。
- 自定义供应商名称时，将 `providers.json.example` 复制为 `~/Library/Application Support/CodexTokenDashboard/providers.json` 并修改内容，然后重新打开应用。
- 数据库和个人配置不包含在分发包中，软件不会上传统计数据。
