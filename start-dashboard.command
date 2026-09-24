#!/bin/sh
set -eu

cd "$(dirname "$0")"
if [ "$(uname -s)" != "Darwin" ]; then
    echo "此启动器仅适用于 macOS。" >&2
    exit 1
fi

if [ -d "CodexTokenDesktop.app" ]; then
    open "CodexTokenDesktop.app"
    exit 0
fi

python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || {
    echo "需要 Python 3.10 或更新版本。" >&2
    exit 1
}
python3 -c 'import webview' 2>/dev/null || {
    echo "请先运行：python3 -m pip install -r requirements-desktop.txt" >&2
    exit 1
}
exec python3 desktop.py
