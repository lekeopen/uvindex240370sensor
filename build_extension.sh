#!/bin/bash
#
# Gravity: 240370紫外线指数传感器扩展打包脚本 v1.0.1
# 用于构建 Gravity UV Index 240370 Sensor 扩展包
#

echo "===== Gravity: 240370紫外线指数传感器扩展打包脚本 v1.0.1 ====="

# 确保脚本目录是基准
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 获取版本号
VERSION=$(grep -o '"version": "[^"]*"' config.json | cut -d'"' -f4)
EXTENSION_NAME="lekeopen-uvindex240370sensor-V${VERSION}.mpext"

# 确保构建目录存在
mkdir -p build

# 创建库文件zip包
echo "创建库文件zip包..."
cd python/libraries
zip -r ../../build/libraries.zip ./*.py
cd ../..

if [ ! -f "build/libraries.zip" ]; then
  echo "错误: 无法创建库文件zip包"
  exit 1
fi

# 复制libraries.zip到项目目录
echo "更新项目中的libraries.zip..."
cp build/libraries.zip python/libraries/libraries.zip
cp build/libraries.zip arduinoC/libraries/libraries.zip

# 创建扩展包
echo "创建扩展包..."
cd ..
zip -r "lekeopen-uvindex240370sensor/${EXTENSION_NAME}" lekeopen-uvindex240370sensor/config.json \
  lekeopen-uvindex240370sensor/python \
  lekeopen-uvindex240370sensor/arduinoC \
  -x "*/\.*" "*/__pycache__/*" "*/\~*" "*/node_modules/*"
cd "lekeopen-uvindex240370sensor"

if [ -f "${EXTENSION_NAME}" ]; then
  echo "✓ 扩展包创建成功: ${EXTENSION_NAME}"
  echo "您可以将此文件导入到Mind+中进行使用"
else
  echo "✗ 扩展包创建失败"
  exit 1
fi

echo "===== 打包完成 ====="
