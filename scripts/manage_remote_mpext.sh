#!/bin/bash
#
# Gravity: 240370紫外线指数传感器远程仓库mpext管理脚本 v1.0.0
# 用于确保远程仓库只保留最新的一个mpext文件
#

echo "===== Gravity: 240370紫外线指数传感器远程仓库mpext管理脚本 v1.0.0 ====="

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

# 获取最新的mpext文件
LATEST_MPEXT=$(ls -t *.mpext | head -n 1)

if [ -z "$LATEST_MPEXT" ]; then
  echo "错误: 未找到mpext文件"
  exit 1
fi

echo "最新的mpext文件是: $LATEST_MPEXT"

# 获取远程仓库中的所有mpext文件
echo "检查远程仓库中的mpext文件..."
OLD_MPEXT_FILES=$(git ls-files --cached "*.mpext" | grep -v "$LATEST_MPEXT")

# 如果有旧的mpext文件，删除它们
if [ ! -z "$OLD_MPEXT_FILES" ]; then
  echo "发现旧的mpext文件，准备删除:"
  echo "$OLD_MPEXT_FILES"
  
  # 从git中删除旧的mpext文件
  echo "$OLD_MPEXT_FILES" | xargs git rm --cached
  
  echo "已从git缓存中删除旧的mpext文件"
  
  # 确保最新的mpext被添加到git
  git add "$LATEST_MPEXT"
  
  # 提交更改
  git commit -m "chore: 只保留最新的mpext文件 ($LATEST_MPEXT)"
  
  echo "已提交更改，现在只保留最新的mpext文件: $LATEST_MPEXT"
  echo "请使用 'git push' 将更改推送到远程仓库"
else
  echo "远程仓库中已经只有最新的mpext文件"
  
  # 确保最新的mpext被添加到git
  git add "$LATEST_MPEXT"
  
  # 检查是否有更改需要提交
  if git diff --cached --quiet; then
    echo "没有需要提交的更改"
  else
    git commit -m "chore: 更新mpext文件 ($LATEST_MPEXT)"
    echo "已提交更改，请使用 'git push' 将更改推送到远程仓库"
  fi
fi

echo "===== 管理完成 ====="
