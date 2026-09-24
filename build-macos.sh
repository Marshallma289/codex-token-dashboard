#!/bin/sh
set -eu

if [ "$(uname -s)" != "Darwin" ]; then
    echo "macOS 安装包必须在 macOS 上构建。" >&2
    exit 1
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
output_dir=${1:-"$script_dir/release"}
mkdir -p "$output_dir"
output_dir=$(CDPATH= cd -- "$output_dir" && pwd)
python_bin=${PYTHON:-python3}
version=$(tr -d '\r\n' < "$script_dir/VERSION")
stamp=$(date -u +%Y%m%d-%H%M%S)
arch=$(uname -m)
build_root="$output_dir/build-$version-$stamp-$arch"
package="$build_root/CodexTokenDashboard-Mac-$arch"
archive="$output_dir/CodexTokenDashboard-Mac-$arch-$version-$stamp.zip"

command -v "$python_bin" >/dev/null 2>&1 || { echo "找不到 Python。" >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "构建需要 Node.js 来检查前端脚本。" >&2; exit 1; }
mkdir -p "$build_root" "$package"
cd "$script_dir"
"$python_bin" -m unittest discover -s tests
node --check web/app.js
"$python_bin" -m PyInstaller --noconfirm \
    --workpath "$build_root/work" \
    --distpath "$build_root/dist" \
    CodexTokenDesktop.spec

app="$build_root/dist/CodexTokenDesktop.app"
if [ ! -d "$app" ]; then
    echo "未生成 CodexTokenDesktop.app。" >&2
    exit 1
fi
ditto "$app" "$package/CodexTokenDesktop.app"
for name in LICENSE THIRD_PARTY_NOTICES.md providers.json.example VERSION MACOS.md start-dashboard.command; do
    cp "$script_dir/$name" "$package/$name"
done
ditto -c -k --sequesterRsrc --keepParent "$package" "$archive"
(
    cd "$output_dir"
    shasum -a 256 "$(basename "$archive")" > "$(basename "$archive").sha256"
)
printf '%s\n' "$archive"
