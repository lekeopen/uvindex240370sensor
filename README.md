# Gravity: 240370紫外线指数传感器 (UV Index Sensor)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![版本](https://img.shields.io/badge/版本-1.0.1-blue.svg)](https://github.com/username/lekeopen-uvindex240370sensor)

## 产品介绍

这是一款针对行空板优化的DFRobot Gravity系列240370紫外线指数传感器扩展，能检测240-370nm波长范围内的紫外线强度，涵盖UVA\UVB\UVC三种波长范围。通过底层处理，能直接输出0-11的UV指数等级和1-5的危害风险警告。本扩展包解决了行空板上的I2C通信问题，优化了设备识别和数据处理逻辑。

## 主要特点

- 🌈 波长范围240-370nm，覆盖UVA/UVB/UVC
- 🔢 直接输出紫外线指数与风险等级，无需转换
- 🛠️ 修复了行空板 PinPong 库 I2C 通信问题
- 📊 改进的 UV 指数计算和错误处理
- 🌐 支持 Arduino 和行空板双平台

## 使用方法

### Mind+ 中使用

1. 导入扩展包 `lekeopen-uvindex240370sensor-V1.0.1.mpext`
2. 在积木区找到"Gravity: 240370紫外线指数传感器"积木块
3. 使用积木块读取 UV 指数、原始数据或风险等级

### Python 代码中使用

```python
from unihiker_uv_patch_v3 import PatchUVSensor

# 创建传感器对象
sensor = PatchUVSensor()
sensor.begin()

# 读取数据
raw_value = sensor.read_UV_original_data()
uv_index = sensor.read_UV_index_data()
risk_level = sensor.read_risk_level_data()

print(f"原始值: {raw_value}")
print(f"UV指数: {uv_index}")
print(f"风险等级: {risk_level}")
```

### Arduino 中使用

```cpp
#include <DFRobot_UVIndex240370Sensor.h>

DFRobot_UVIndex240370Sensor UVSensor;

void setup() {
  Serial.begin(115200);
  
  // 初始化传感器
  UVSensor.begin();
}

void loop() {
  // 读取原始值
  uint16_t raw = UVSensor.getRaw();
  
  // 读取 UV 指数
  uint8_t index = UVSensor.getUvIndex();
  
  // 读取风险级别
  uint8_t riskLevel = UVSensor.getRiskLevel();
  
  Serial.print("原始值: ");
  Serial.println(raw);
  
  Serial.print("UV指数: ");
  Serial.println(index);
  
  Serial.print("风险等级: ");
  Serial.println(riskLevel);
  
  delay(1000);
}
```

## 紫外线风险等级指南

| 紫外线指数 | 风险等级 | 防护建议 |
|----------|---------|----------|
| 0-2 | 低风险 | 可以安全在户外活动，无需特殊防护 |
| 3-5 | 中等风险 | 在户外活动时建议使用防晒霜，佩戴太阳镜 |
| 6-7 | 高风险 | 避免在中午时分长时间暴露，使用SPF15+防晒霜 |
| 8-10 | 很高风险 | 尽量减少户外活动，必要时采取全面防护措施 |
| 11+ | 极高风险 | 尽量避免在阳光下活动，必须采取全面防护 |

## 目录结构

```
lekeopen-uvindex240370sensor/
├── arduinoC/        - Arduino 库和示例
├── python/          - Python 库和 Mind+ 扩展
├── docs/            - 项目文档
├── examples/        - 示例程序
├── build/           - 构建文件
├── build_extension.sh - 扩展包构建脚本
└── deploy_to_unihiker.sh - 行空板部署脚本
```

## 开源协议

本项目采用 MIT 开源协议。详情请参阅 [LICENSE](LICENSE) 文件。
