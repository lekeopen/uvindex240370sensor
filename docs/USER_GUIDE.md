# 紫外线传感器用户指南

## 产品介绍

DFRobot 240370 紫外线指数传感器是一款能直接输出紫外线 UV 指数和危害等级的传感器。经过优化的驱动库解决了在行空板(UniHiker)上的兼容性问题，提供了稳定可靠的数据读取。

## 快速入门

### 硬件连接

将紫外线传感器按照下表连接到行空板：

| 传感器引脚 | 行空板引脚 |
| ---------- | ---------- |
| VCC        | 3.3V       |
| GND        | GND        |
| SDA        | SDA (I2C)  |
| SCL        | SCL (I2C)  |

### 软件安装

#### 方法 1：使用 Mind+

1. 在 Mind+中导入扩展包
2. 创建新项目
3. 使用积木块编程

#### 方法 2：直接使用 Python

1. 将`unihiker_uv_patch_v2.py`上传到行空板
2. 在 Python 代码中导入:

```python
from unihiker_uv_patch_v2 import PatchUVSensor

# 创建传感器对象
sensor = PatchUVSensor()

# 初始化
if sensor.begin():
    # 读取数据
    raw_value = sensor.read_UV_original_data()
    uv_index = sensor.read_UV_index_data()
    risk_level = sensor.read_risk_level_data()
```

## 功能说明

本传感器能够提供三种数据：

1. **原始数据**: 传感器直接读取的未处理数值 (0-20000 范围)
2. **UV 指数**: 国际标准紫外线指数 (0-11 范围)
3. **风险等级**: 紫外线危害程度 (0-4，分别表示低、中、高、很高、极高风险)

## 示例程序

参见`examples`文件夹中的示例程序：

- `basic_uv_example.py`: 基础使用示例
- `gui_uv_monitor.py`: 带 GUI 界面的监测示例
- `mindplus_integration.py`: Mind+集成示例

## 故障排除

### 无法读取数据

- 检查电源连接是否正确
- 确认 I2C 连接线有没有松动
- 使用`sudo i2cdetect -y 4`命令检查 I2C 设备

### 数据异常

- 传感器需要在有光照的环境下测试
- 值为 0 可能是光照太弱或连接问题
- 不稳定值可能需要使用数据平滑处理

## 技术规格

- 工作电压: 3.3V-5V
- 接口类型: I2C
- 默认 I2C 地址: 0x23 (可能是 0x38)
- 测量范围: 0-15 UV 指数
- 精度: ±0.5 UV 指数

## 更多资源

- [行空板官网](https://www.unihiker.com/)
- [Mind+ 软件下载](https://mindplus.cc/)
- [传感器数据手册](https://www.dfrobot.com.cn/)

---

如有任何问题，请联系我们的技术支持团队。
