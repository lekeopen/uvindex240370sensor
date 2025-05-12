#!/bin/bash
#
# Gravity: 240370紫外线指数传感器扩展打包脚本 v1.0.1
# 用于构建 Gravity UV Index 240370 Sensor 扩展包
#

echo "===== Gravity: 240370紫外线指数传感器扩展打包脚本 v1.0.1 ====="

# 确保脚本目录是基准
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
# 返回项目根目录
cd ..

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

# 创建Arduino C库文件zip包
echo "创建Arduino C库文件zip包..."
cd arduinoC/libraries
zip -r ../../build/arduino_libraries.zip ./DFRobot_UVIndex240370Sensor
cd ../..

if [ ! -f "build/libraries.zip" ]; then
  echo "错误: 无法创建Python库文件zip包"
  exit 1
fi

if [ ! -f "build/arduino_libraries.zip" ]; then
  echo "错误: 无法创建Arduino C库文件zip包"
  exit 1
fi

# 复制libraries.zip到项目目录
echo "更新项目中的libraries.zip..."
cp build/libraries.zip python/libraries/libraries.zip

# 合并Arduino库和Python库到Arduino的libraries.zip
echo "合并Arduino库和Python库..."
cp build/arduino_libraries.zip arduinoC/libraries/libraries.zip
cd arduinoC/libraries
mkdir -p temp
cd temp
unzip ../libraries.zip
cd ..
unzip -o ../../build/libraries.zip -d temp
cd temp
zip -r ../libraries.zip .
cd ..
rm -rf temp
cd ../..

# 创建扩展包
echo "创建扩展包..."
zip -r "${EXTENSION_NAME}" config.json \
  python \
  arduinoC \
  -x "*/\.*" "*/__pycache__/*" "*/\~*" "*/node_modules/*"

if [ -f "${EXTENSION_NAME}" ]; then
  echo "✓ 扩展包创建成功: ${EXTENSION_NAME}"
  
  # 只保留最新的3个mpext文件
  echo "清理旧的mpext文件，仅保留最新的3个..."
  ls -t *.mpext | tail -n +4 | xargs rm -f 2>/dev/null
  
  # 统计保留的mpext文件数量
  MPEXT_COUNT=$(ls *.mpext | wc -l)
  echo "当前保留了 ${MPEXT_COUNT} 个mpext文件"
  
  echo "您可以将此文件导入到Mind+中进行使用"
else
  echo "✗ 扩展包创建失败"
  exit 1
fi

echo "===== 打包完成 ====="
