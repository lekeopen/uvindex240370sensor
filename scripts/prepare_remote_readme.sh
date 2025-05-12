#!/bin/bash
#
# Gravity: 240370紫外线指数传感器远程仓库README管理脚本 v1.0.0
# 此脚本用于在推送到远程仓库前准备专用的README.md文件
#

echo "===== Gravity: 240370紫外线指数传感器远程仓库README管理脚本 v1.0.0 ====="

# 确保脚本目录是基准
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
# 返回项目根目录
cd ..

# 检查是否在git仓库中
if [ ! -d ".git" ]; then
  echo "错误: 当前目录不是git仓库"
  exit 1
fi

# 检查README_REMOTE.md文件是否存在
if [ ! -f "README_REMOTE.md" ]; then
  echo "错误: README_REMOTE.md 文件不存在"
  exit 1
fi

# 确认README_REMOTE.md不是空文件
if [ ! -s "README_REMOTE.md" ]; then
  echo "错误: README_REMOTE.md 是空文件"
  exit 1
fi

echo "准备用远程仓库专用的README替换当前README..."

# 备份当前的README.md
if [ -f "README.md" ]; then
  echo "备份当前的README.md到README_LOCAL.md..."
  cp README.md README_LOCAL.md
  echo "备份完成: $(ls -l README_LOCAL.md)"
fi

# 将README_REMOTE.md复制为README.md
echo "应用远程仓库专用的README..."
cp README_REMOTE.md README.md
echo "README.md 已更新: $(ls -l README.md)"

# 将README.md添加到git
git add README.md
echo "README.md 已加入git暂存区"

# 检查是否有更改需要提交
if git diff --cached --quiet -- README.md; then
  echo "README.md 没有变化，无需提交"
else
  echo "✓ README.md已更新为远程仓库版本"
  echo "请运行以下命令提交更改并推送到远程仓库:"
  echo "  git commit -m \"docs: 更新README.md为远程仓库版本\""
  echo "  git push origin <分支名>"
fi

echo ""
echo "注意: 推送完成后，如果需要恢复本地README.md，请执行:"
echo "  cp README_LOCAL.md README.md"

echo "===== README管理完成 ====="
