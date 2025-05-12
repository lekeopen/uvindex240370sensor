#!/bin/bash
#
# Gravity: 240370紫外线指数传感器库部署脚本 v1.0.1
# 用于将Gravity 240370紫外线指数传感器库部署到行空板上
#

echo "===== Gravity: 240370紫外线指数传感器库部署脚本 v1.0.1 ====="
echo "正在部署库文件到行空板..."

# 确保脚本目录是基准
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 定义库文件
LIB_FILES=("python/libraries/unihiker_uv_patch_v3.py")
REMOTE_USER=${1:-"unihiker"}
REMOTE_HOST=${2:-"unihiker.local"}
REMOTE_DIR="/usr/lib/python3/dist-packages"

# 检查库文件是否存在
for file in "${LIB_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo "错误: 找不到库文件 $file"
    exit 1
  fi
done

# 尝试SCP复制
echo "正在将库文件复制到行空板 ($REMOTE_HOST)..."
for file in "${LIB_FILES[@]}"; do
  filename=$(basename "$file")
  echo "复制 $filename..."
  
  # 使用scp复制文件
  if scp "$file" "$REMOTE_USER@$REMOTE_HOST:~/$filename"; then
    echo "文件已复制到行空板家目录"
    
    # 使用SSH执行sudo命令将文件移动到目标目录
    if ssh "$REMOTE_USER@$REMOTE_HOST" "sudo cp ~/$filename $REMOTE_DIR/ && sudo chmod 644 $REMOTE_DIR/$filename && rm ~/$filename"; then
      echo "✓ 文件已成功安装到 $REMOTE_DIR/$filename"
    else
      echo "✗ 无法将文件移动到 $REMOTE_DIR"
      exit 1
    fi
  else
    echo "✗ 无法复制文件到行空板"
    exit 1
  fi
done

echo "===== 库文件部署完成! ====="
echo "现在您可以在行空板上通过以下方式导入库:"
echo "from unihiker_uv_patch_v3 import PatchUVSensor"
