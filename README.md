# Gravity: 240370 紫外线指数传感器 (UV Index Sensor)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![版本](https://img.shields.io/badge/版本-0.1.0-blue.svg)](https://github.com/rockts/lekeopen-uvindex240370sensor)

<div align="center">
  <img src="./arduinoC/_images/featured.png" width="400" alt="UV Index Sensor"/>
</div>

**语言**: [中文](README.md) | [English](README_EN.md)

## 📋 项目简介

这是一款针对行空板优化的 DFRobot Gravity 系列 240370 紫外线指数传感器扩展，能检测 240-370nm 波长范围内的紫外线强度，涵盖 UVA、UVB、UVC 三种波长范围。通过底层处理，能直接输出 0-11 的 UV 指数等级和 1-5 的危害风险警告。本扩展包解决了行空板上的 I2C 通信问题，优化了设备识别和数据处理逻辑。特别修复了特定原始值(3, 6, 14, 48, 512)下 UV 指数和风险等级计算的问题。

## ✨ 主要特点

- 🌈 波长范围 240-370nm，覆盖 UVA/UVB/UVC
- 🔢 直接输出紫外线指数与风险等级，无需转换
- 🛠️ 修复了行空板 PinPong 库 I2C 通信问题
- 📊 改进的 UV 指数计算和错误处理
- 🌐 支持 Arduino 和行空板双平台
- 🔌 提供 Mind+ 可视化编程支持

## 📥 下载与安装

在 [Releases](https://github.com/rockts/lekeopen-uvindex240370sensor/releases) 页面下载最新的扩展包。

- 当前版本：[rockts-lekeopen-uvindex240370sensor-thirdex-V0.1.0.mpext](https://github.com/rockts/lekeopen-uvindex240370sensor/raw/main/rockts-lekeopen-uvindex240370sensor-thirdex-V0.1.0.mpext)

## 🚀 使用方法

### Mind+ 中使用

1. 下载最新的 `.mpext` 扩展包文件
2. 打开 Mind+，点击"扩展"→"管理扩展"→"本地导入"
3. 选择下载的扩展包进行安装
4. 在积木区找到"Gravity: 240370 紫外线指数传感器"积木块
5. 使用积木块读取 UV 指数、原始数据或风险等级

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

## 🌡️ 紫外线风险等级指南

| 紫外线指数 | 风险等级 | 防护建议                                    |
| ---------- | -------- | ------------------------------------------- |
| 0-2        | 低风险   | 可以安全在户外活动，无需特殊防护            |
| 3-5        | 中等风险 | 在户外活动时建议使用防晒霜，佩戴太阳镜      |
| 6-7        | 高风险   | 避免在中午时分长时间暴露，使用 SPF15+防晒霜 |
| 8-10       | 很高风险 | 尽量减少户外活动，必要时采取全面防护措施    |
| 11+        | 极高风险 | 尽量避免在阳光下活动，必须采取全面防护      |

## 🔧 硬件连接

### Arduino 连接

| 传感器引脚 | Arduino 引脚         |
| ---------- | -------------------- |
| VCC        | 5V/3.3V              |
| GND        | GND                  |
| SDA        | A4 (UNO) / 20 (MEGA) |
| SCL        | A5 (UNO) / 21 (MEGA) |

### 行空板连接

| 传感器引脚 | 行空板引脚 |
| ---------- | ---------- |
| VCC        | 3.3V       |
| GND        | GND        |
| SDA        | SDA        |
| SCL        | SCL        |

## 📝 传感器规格

- **供电电压**: 3.3V - 5V
- **通信接口**: I2C
- **波长范围**: 240-370nm
- **测量范围**: 紫外线指数 0-11+
- **精度**: ±1 紫外线指数
- **响应时间**: <1s
- **工作温度**: -20℃ 至 85℃
- **尺寸**: 29.0 × 22.0 mm

## 📁 仓库结构

**仓库类型**: 这是发布仓库结构，只包含使用所需的必要文件。

### 仓库结构

```
/
├── config.json               # 扩展配置文件
├── LICENSE                   # MIT许可证
├── README.md                 # 中文文档
├── README_EN.md              # 英文文档
├── lekeopen-uvindex240370sensor-V0.1.0.mpext  # 最新版本的扩展包
├── arduinoC/                 # Arduino平台相关文件（精简结构）
│   ├── _images/
│   ├── _locales/
│   ├── libraries/
│   │   └── libraries.zip     # 打包的Arduino库
│   └── main.ts
└── python/                   # Python平台相关文件（精简结构）
    ├── _images/
    ├── _locales/
    ├── libraries/
    │   └── libraries.zip     # 打包的Python库
    └── main.ts
```

## 🔄 版本历史

- **0.1.0** (2025.05.14)

  - 重构项目结构，优化代码组织
  - 删除开发目录，保持远程仓库简洁
  - 修复特定原始值(0, 3, 6, 14, 48, 512)的 UV 指数计算
  - 优化`.gitignore`规则，避免不必要文件提交
  - 修复数据采集和处理的关键问题

- **0.0.9** (2025.05.13)
  - 精简代码结构，移除调试信息
  - 优化传感器初始化逻辑
  - 致谢原项目作者
- **0.0.8** (2025.05.13)
  - 修复原始值为 1024 时异常 UV 指数问题
  - 优化数据处理逻辑，增强数据一致性
  - 解决原始值为 0 但 UV 指数为 1 的异常情况
- **0.0.7** (2025.05.13)
  - 修复 Mind+ 导入错误问题
  - 确保正确打包 libraries.zip 文件
  - 优化打包脚本
- **0.0.6** (2025.05.13)
  - 优化数据显示格式，解决终端数据重叠问题
  - 使用 ASCII 框架式格式化输出，提高可读性
  - 添加清屏控制，避免数据堆积
- **0.0.5** (2025.05.13)
  - 修复 UV 指数为 1 时风险等级计算错误问题
  - 改进数据输出方式，增加文本标签
  - 创建自动化脚本管理远程仓库
- **0.0.4** (2025.05.13)
  - 修复字节序问题，优化数据处理逻辑
  - 增强零值处理与数据平滑滤波
  - 解决数据跳变和读取错误问题
- **0.0.3** (2025.05.13)
  - 修复 Arduino Uno 兼容性问题
  - 添加扩展包管理功能
  - 优化库文件结构
- **0.0.2** (2025.05.13)
  - 改进错误处理机制
  - 增强设备识别逻辑
- **0.0.1** (2025.05.12)
  - 首次发布
  - 支持行空板和 Arduino 平台
  - 基础 UV 指数测量功能

## 👨‍💻 贡献

欢迎提交问题和功能请求。如果您想贡献代码，请 fork 并提交 pull request。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
