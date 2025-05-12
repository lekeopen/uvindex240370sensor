#!/bin/bash
#
# Gravity: 240370紫外线指数传感器远程仓库README管理脚本 v1.0.1
# 此脚本用于在推送到远程仓库前准备专用的README.md文件
#

echo "===== Gravity: 240370紫外线指数传感器远程仓库README管理脚本 v1.0.1 ====="

# 设置颜色变量
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 确保脚本目录是基准
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
# 返回项目根目录
cd ..

# 检查是否在git仓库中
if [ ! -d ".git" ]; then
  echo -e "${RED}错误: 当前目录不是git仓库${NC}"
  exit 1
fi

# 检查README_REMOTE.md文件是否存在
if [ ! -f "README_REMOTE.md" ]; then
  echo -e "${RED}错误: README_REMOTE.md 文件不存在${NC}"
  exit 1
fi

# 检查README_REMOTE.md文件是否为空
if [ ! -s "README_REMOTE.md" ]; then
  echo -e "${RED}错误: README_REMOTE.md 文件为空${NC}"
  exit 1
fi

# 验证README_REMOTE.md文件内容
if ! grep -q "Gravity: 240370紫外线指数传感器" README_REMOTE.md; then
  echo -e "${RED}错误: README_REMOTE.md 文件内容不正确，缺少必要的标题${NC}"
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
  echo -e "${YELLOW}README.md 没有变化，无需提交${NC}"
else
  echo -e "${GREEN}✓ README.md已更新为远程仓库版本${NC}"
  echo -e "${BLUE}是否自动提交更改? (y/n) ${NC}"
  read -r answer
  if [[ "$answer" =~ ^[Yy]$ ]]; then
    # 获取当前分支名
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    
    # 提交更改
    git commit -m "docs: 更新README.md为远程仓库版本"
    echo -e "${GREEN}✓ 已提交更改${NC}"
    
    # 提示推送
    echo -e "${BLUE}是否推送到远程仓库? (y/n) ${NC}"
    read -r push_answer
    if [[ "$push_answer" =~ ^[Yy]$ ]]; then
      git push origin "$current_branch"
      if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 已成功推送到远程仓库${NC}"
      else
        echo -e "${RED}推送失败，请手动执行:${NC}"
        echo -e "${BLUE}  git push origin $current_branch${NC}"
      fi
    else
      echo -e "${YELLOW}请稍后手动推送:${NC}"
      echo -e "${BLUE}  git push origin $current_branch${NC}"
    fi
  else
    echo -e "${YELLOW}请手动提交更改:${NC}"
    echo -e "${BLUE}  git commit -m \"docs: 更新README.md为远程仓库版本\"${NC}"
    echo -e "${BLUE}  git push origin <分支名>${NC}"
  fi
fi

echo ""
echo -e "${YELLOW}注意: 如果需要恢复本地README.md，请执行:${NC}"
echo -e "${BLUE}  cp README_LOCAL.md README.md${NC}"

echo -e "${GREEN}===== README管理完成 =====${NC}"
