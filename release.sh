#!/bin/bash
# ============================================================
# 光压云盘开发者API控制台 - 版本发布脚本
# 用法: ./release.sh <版本号> [提交信息]
# 示例: ./release.sh 1.0.1 "修复xxx问题"
# ============================================================

set -e

VERSION=$1
COMMIT_MSG=$2

if [ -z "$VERSION" ]; then
  echo "用法: ./release.sh <版本号> [提交信息]"
  echo "示例: ./release.sh 1.0.1 \"修复xxx问题\""
  exit 1
fi

# 版本号格式校验（支持 x.y.z）
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "[错误] 版本号格式应为 x.y.z（例如 1.0.1）"
  exit 1
fi

TAG="v$VERSION"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  发布版本 $TAG"
echo "=========================================="

# 1. 检查工作区是否干净
if [ -n "$(git status --porcelain)" ]; then
  echo ""
  echo "[警告] 工作区有未提交的变更："
  git status --short
  echo ""
  if [ -z "$COMMIT_MSG" ]; then
    read -p "是否提交这些变更？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
      echo "已取消发布"
      exit 1
    fi
    read -p "请输入提交信息: " COMMIT_MSG
  fi
  git add -A
  git commit -m "$COMMIT_MSG"
  echo "[OK] 已提交变更"
fi

# 2. 检查 tag 是否已存在
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "[错误] 标签 $TAG 已存在，请使用其他版本号"
  exit 1
fi

# 3. 推送到远程 main 分支
echo ""
echo "[1/4] 推送代码到远程 main 分支..."
git push origin main

# 4. 创建并推送 tag
echo ""
echo "[2/4] 创建并推送标签 $TAG ..."
git tag -a "$TAG" -m "Release $TAG"
git push origin "$TAG"
echo "[OK] 标签 $TAG 已推送"

# 5. 本地打包（排除敏感文件和非必要文件）
echo ""
echo "[3/4] 生成本地源码包..."
ARCHIVE_NAME="guangyapan-api-console-$VERSION"
tar -czf "${ARCHIVE_NAME}.tar.gz" \
  --exclude=".git" \
  --exclude="config.json" \
  --exclude="__pycache__" \
  --exclude="*.pyc" \
  --exclude=".DS_Store" \
  --exclude="*.log" \
  --exclude="venv" \
  --exclude=".venv" \
  -C .. "$(basename "$SCRIPT_DIR")"
echo "[OK] 源码包: ${ARCHIVE_NAME}.tar.gz"

# 6. 生成文件清单和校验和
echo ""
echo "[4/4] 生成文件清单和校验和..."
tar -tzf "${ARCHIVE_NAME}.tar.gz" > "filelist-$VERSION.txt"
shasum -a 256 "${ARCHIVE_NAME}.tar.gz" > "checksum-$VERSION.txt"
echo "[OK] 文件清单: filelist-$VERSION.txt"
echo "[OK] 校验和: checksum-$VERSION.txt"

echo ""
echo "=========================================="
echo "  版本 $TAG 发布完成！"
echo "=========================================="
echo ""
echo "GitHub Release 页面:"
echo "  https://github.com/whboy10000/guangya_file_cross-account-transfer/releases/tag/$TAG"
echo ""
echo "本地产物:"
echo "  - ${ARCHIVE_NAME}.tar.gz"
echo "  - filelist-$VERSION.txt"
echo "  - checksum-$VERSION.txt"
echo ""
echo "提示: 可在 GitHub Release 页面手动上传上述源码包和说明"
