#!/bin/bash
# ============================================================
# 番茄钟 macOS 构建脚本
# 用法：在 macOS 终端中运行 bash build_mac.sh
# 需要：Python 3.10+、pip
# ============================================================

set -e

APP_NAME="PomodoroTimer"
VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🍅 番茄钟 macOS 打包脚本 v${VERSION}"
echo "================================================"

# 1. 检查 Python
echo "[1/5] 检查 Python 环境..."
PYTHON=$(which python3 || which python)
if [ -z "$PYTHON" ]; then
    echo "❌ 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi
echo "✅ Python: $($PYTHON --version)"

# 2. 安装依赖
echo "[2/5] 安装依赖（Pillow、PyInstaller）..."
$PYTHON -m pip install --quiet Pillow pyinstaller

# 3. 生成图标（.icns 格式）
echo "[3/5] 生成应用图标..."
$PYTHON - <<'EOF'
from PIL import Image, ImageDraw
import os, subprocess, shutil, tempfile

def create_icns(output_path):
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    tmp_dir = tempfile.mkdtemp()
    iconset_dir = os.path.join(tmp_dir, "AppIcon.iconset")
    os.makedirs(iconset_dir)

    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        p = size // 10
        draw.ellipse([p, p, size-p, size-p], fill=(220, 60, 60, 255))
        lw = size // 4; lh = size // 5; cx = size // 2; top = p - size // 12
        draw.polygon([(cx, top), (cx-lw//2, top+lh), (cx+lw//2, top+lh)], fill=(60, 180, 60, 255))
        if size >= 32:
            inner = size // 2 - size // 6
            draw.ellipse([cx-inner, cx-inner, cx+inner, cx+inner], fill=(255,255,255,200))
            lnw = max(1, size//32)
            draw.line([(cx,cx),(cx,cx-inner+size//10)], fill=(220,60,60,255), width=lnw)
            draw.line([(cx,cx),(cx+inner-size//10,cx)], fill=(220,60,60,255), width=lnw)
        # 保存标准和 @2x 尺寸
        img.save(os.path.join(iconset_dir, f"icon_{size}x{size}.png"))
        if size <= 512:
            img2 = img.resize((size*2, size*2), Image.LANCZOS)
            img2.save(os.path.join(iconset_dir, f"icon_{size}x{size}@2x.png"))

    icns_path = output_path
    subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], check=True)
    shutil.rmtree(tmp_dir)
    print(f"图标已生成: {icns_path}")

create_icns(os.path.join(os.environ.get("SCRIPT_DIR", "."), "pomodoro.icns"))
EOF

# 4. PyInstaller 打包
echo "[4/5] 使用 PyInstaller 打包 .app..."
cd "$SCRIPT_DIR"
$PYTHON -m PyInstaller \
    --onefile \
    --windowed \
    --icon="pomodoro.icns" \
    --name="$APP_NAME" \
    --distpath="$SCRIPT_DIR/dist" \
    --workpath="$SCRIPT_DIR/build" \
    --specpath="$SCRIPT_DIR" \
    --osx-bundle-identifier="com.pomodoro.timer" \
    "pomodoro.py"

# 5. 打包为 DMG
echo "[5/5] 创建 DMG 安装包..."
DMG_NAME="${APP_NAME}-v${VERSION}-macOS.dmg"
APP_PATH="$SCRIPT_DIR/dist/${APP_NAME}.app"

if [ ! -d "$APP_PATH" ]; then
    # onefile 模式生成的是单文件，转换为 .app bundle
    echo "  (单文件模式，跳过 DMG，直接压缩为 zip)"
    cd "$SCRIPT_DIR/dist"
    zip -r "${APP_NAME}-v${VERSION}-macOS.zip" "${APP_NAME}"
    echo "✅ 已生成: $SCRIPT_DIR/dist/${APP_NAME}-v${VERSION}-macOS.zip"
else
    # 使用 hdiutil 创建 DMG
    hdiutil create \
        -volname "$APP_NAME" \
        -srcfolder "$APP_PATH" \
        -ov -format UDZO \
        "$SCRIPT_DIR/dist/$DMG_NAME"
    echo "✅ 已生成: $SCRIPT_DIR/dist/$DMG_NAME"
fi

echo ""
echo "🎉 打包完成！产物位于: $SCRIPT_DIR/dist/"
echo "================================================"
