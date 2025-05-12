#!/bin/bash
#
# Gravity: 240370紫外线指数传感器远程仓库发布准备脚本 v1.0.1
# 此脚本用于准备将项目推送到远程仓库前的所有必要操作
# 包括：更新README.md、管理mpext文件
#

# 设置颜色变量
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 显示带颜色的标题
echo -e "${CYAN}"
echo "╔═════════════════════════════════════════════════════════╗"
echo "║                                                         ║"
echo -e "║  ${GREEN}Gravity: 240370紫外线指数传感器 - 远程仓库发布准备${CYAN}  ║"
echo "║                                                         ║"
echo -e "║  ${BLUE}版本: v1.0.1                           作者: rockts${CYAN}  ║"
echo "║                                                         ║"
echo "╚═════════════════════════════════════════════════════════╝"
echo -e "${NC}"

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

# 获取当前工作目录
CURRENT_DIR=$(pwd)
PROJECT_NAME=$(basename "$CURRENT_DIR")
echo -e "${PURPLE}当前项目: ${CYAN}$PROJECT_NAME${NC}"
echo -e "${PURPLE}工作目录: ${CYAN}$CURRENT_DIR${NC}\n"

# 检查必要的脚本是否存在
echo -e "${BLUE}检查必要的组件...${NC}"
missing_components=0

# 检查 prepare_remote_readme.sh
if [ ! -f "scripts/prepare_remote_readme.sh" ]; then
  echo -e "${RED}✗ scripts/prepare_remote_readme.sh 脚本不存在${NC}"
  missing_components=1
else
  echo -e "${GREEN}✓ 发现 README 管理脚本${NC}"
fi

# 检查 manage_remote_mpext.sh
if [ ! -f "scripts/manage_remote_mpext.sh" ]; then
  echo -e "${RED}✗ scripts/manage_remote_mpext.sh 脚本不存在${NC}"
  missing_components=1
else
  echo -e "${GREEN}✓ 发现 MPEXT 管理脚本${NC}"
fi

# 检查 README_REMOTE.md
if [ ! -f "README_REMOTE.md" ]; then
  echo -e "${RED}✗ README_REMOTE.md 文件不存在${NC}"
  missing_components=1
else
  echo -e "${GREEN}✓ 发现远程仓库 README 模板${NC}"
fi

if [ $missing_components -eq 1 ]; then
  echo -e "\n${RED}缺少必要组件，无法继续。${NC}"
  exit 1
fi

# 确保脚本有执行权限
echo -e "${BLUE}设置脚本执行权限...${NC}"
chmod +x scripts/prepare_remote_readme.sh scripts/manage_remote_mpext.sh
echo -e "${GREEN}✓ 执行权限已设置${NC}"

# 计时开始
START_TIME=$(date +%s)

# 步骤0: 检查并列出MPEXT文件
echo -e "\n${CYAN}┌──────────────────────────────────────────┐"
echo -e "│  ${YELLOW}步骤 0: 列出并检查当前MPEXT文件状态  ${CYAN}│"
echo -e "└──────────────────────────────────────────┘${NC}"

# 获取所有的mpext文件
MPEXT_FILES=$(ls -t *.mpext 2>/dev/null)
MPEXT_COUNT=$(echo "$MPEXT_FILES" | wc -l)

if [ -z "$MPEXT_FILES" ]; then
  echo -e "${RED}警告: 未找到MPEXT文件${NC}"
else
  echo -e "${BLUE}当前MPEXT文件 (按时间排序):${NC}"
  echo -e "${YELLOW}---------------------------------------------${NC}"
  ls -lh *.mpext | awk '{print $9, "(" $5 ")"}'
  echo -e "${YELLOW}---------------------------------------------${NC}"
  echo -e "${GREEN}✓ 找到 $MPEXT_COUNT 个MPEXT文件${NC}"
  
  # 检查版本号
  LATEST_MPEXT=$(ls -t *.mpext | head -n 1)
  echo -e "${BLUE}最新版本: ${CYAN}$LATEST_MPEXT${NC}"
  
  # 从config.json获取当前版本号
  CONFIG_VERSION=$(grep -o '"version": "[^"]*"' config.json | cut -d'"' -f4)
  echo -e "${BLUE}配置版本: ${CYAN}$CONFIG_VERSION${NC}"
  
  # 检查版本是否一致
  if [[ "$LATEST_MPEXT" == *"$CONFIG_VERSION"* ]]; then
    echo -e "${GREEN}✓ 版本号一致${NC}"
  else
    echo -e "${RED}警告: 版本号不一致${NC}"
    echo -e "${YELLOW}是否需要更新版本号? (y/n) ${NC}"
    read -r version_answer
    if [[ "$version_answer" =~ ^[Yy]$ ]]; then
      echo -e "${YELLOW}请先更新config.json中的版本号并重新构建MPEXT文件${NC}"
      exit 1
    fi
  fi
fi

# 步骤1: 更新README.md
echo -e "\n${CYAN}┌──────────────────────────────────────────┐"
echo -e "│  ${YELLOW}步骤 1: 准备远程仓库专用的README.md  ${CYAN}│"
echo -e "└──────────────────────────────────────────┘${NC}"

echo -e "${BLUE}执行中，请稍等...${NC}"
scripts/prepare_remote_readme.sh
if [ $? -ne 0 ]; then
  echo -e "${RED}README.md准备失败，终止发布准备${NC}"
  exit 1
fi
echo -e "${GREEN}✓ README.md准备完成${NC}"

# 步骤2: 管理mpext文件
echo -e "\n${CYAN}┌──────────────────────────────────────────┐"
echo -e "│  ${YELLOW}步骤 2: 管理MPEXT文件，只保留最新版本  ${CYAN}│"
echo -e "└──────────────────────────────────────────┘${NC}"

echo -e "${BLUE}执行中，请稍等...${NC}"
scripts/manage_remote_mpext.sh
if [ $? -ne 0 ]; then
  echo -e "${RED}MPEXT文件管理失败，终止发布准备${NC}"
  exit 1
fi
echo -e "${GREEN}✓ MPEXT文件管理完成${NC}"

# 最终状态检查
echo -e "\n${CYAN}┌──────────────────────────────────────────┐"
echo -e "│  ${YELLOW}步骤 3: 最终状态检查及提交确认        ${CYAN}│"
echo -e "└──────────────────────────────────────────┘${NC}"

# 检查git状态
echo -e "${BLUE}当前Git状态:${NC}"
echo -e "${YELLOW}---------------------------------------------${NC}"
git status
echo -e "${YELLOW}---------------------------------------------${NC}"

# 获取当前分支
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo -e "${BLUE}当前分支: ${CYAN}$current_branch${NC}"

# 计算执行时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo -e "${BLUE}处理用时: ${CYAN}${DURATION}秒${NC}"

# 发布确认
echo -e "\n${GREEN}✓ 远程仓库发布准备已完成!${NC}"
echo -e "${BLUE}是否立即推送到远程仓库? (y/n) ${NC}"
read -r push_answer
if [[ "$push_answer" =~ ^[Yy]$ ]]; then
  echo -e "${YELLOW}正在推送到远程仓库...${NC}"
  git push origin "$current_branch"
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 已成功推送到远程仓库${NC}"
    
    # 询问是否创建发布标签
    echo -e "${BLUE}是否要为当前版本创建Git标签? (y/n) ${NC}"
    read -r tag_answer
    if [[ "$tag_answer" =~ ^[Yy]$ ]]; then
      # 获取版本号
      VERSION=$(grep -o '"version": "[^"]*"' config.json | cut -d'"' -f4)
      TAG_NAME="v$VERSION"
      
      # 检查标签是否已存在
      if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
        echo -e "${YELLOW}标签 $TAG_NAME 已存在${NC}"
        echo -e "${BLUE}是否覆盖? (y/n) ${NC}"
        read -r override_answer
        if [[ "$override_answer" =~ ^[Yy]$ ]]; then
          git tag -d "$TAG_NAME"
          git push origin :refs/tags/"$TAG_NAME"
        else
          echo -e "${YELLOW}标签创建已取消${NC}"
          echo -e "${CYAN}┌───────────────────────────────────────┐"
          echo -e "│  ${GREEN}✓ 发布流程完成                      ${CYAN}│"
          echo -e "└───────────────────────────────────────┘${NC}"
          exit 0
        fi
      fi
      
      # 创建并推送标签
      git tag -a "$TAG_NAME" -m "Release $TAG_NAME"
      git push origin "$TAG_NAME"
      echo -e "${GREEN}✓ 标签 $TAG_NAME 已创建并推送${NC}"
    fi
  else
    echo -e "${RED}推送失败，请手动执行:${NC}"
    echo -e "${BLUE}  git push origin $current_branch${NC}"
  fi
else
  echo -e "${YELLOW}请稍后手动推送:${NC}"
  echo -e "${BLUE}  git push origin $current_branch${NC}"
fi

echo -e "\n${CYAN}┌───────────────────────────────────────┐"
echo -e "│  ${GREEN}✓ 发布流程完成                      ${CYAN}│"
echo -e "└───────────────────────────────────────┘${NC}"
