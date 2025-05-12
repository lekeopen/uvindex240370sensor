# 紫外线传感器技术文档

## 技术架构

紫外线传感器库的技术架构如下：

```
+------------------+
| Mind+ 积木接口   |   <- 用户使用的图形化编程积木
+--------+---------+
         |
+--------v---------+
| main.ts         |   <- 积木定义和Python代码生成
+--------+---------+
         |
+--------v---------+
| 传感器驱动库     |   <- 核心功能实现
+------------------+
```

传感器驱动库有两个版本：

- `unihiker_uv_patch_v2.py`: 使用 smbus 库的通用版本
- `DFRobot_UVIndex240370Sensor_unihiker.py`: 原始版本

## 关键技术点

### 1. 设备 ID 字节序问题

行空板上读取到的设备 ID 为 0x7C42，而标准设备 ID 为 0x427C（字节序颠倒）。我们的解决方案：

```python
# 读取设备ID
data = bus.read_i2c_block_data(addr, REG_PID, 2)
device_id = (data[0] << 8) | data[1]

# 支持两种字节序的设备ID
if device_id == DEVICE_PID or device_id == DEVICE_PID_REVERSED:
    # 找到设备
    return True
```

### 2. I2C 总线探测

行空板使用的 I2C 总线编号与标准不同，我们实现了自动探测：

```python
# 常用的总线列表
bus_list = [1, 0, 2, 3, 4, 5, 6, 7]  # 优先尝试常用总线，特别是总线4

# 尝试所有总线直到找到设备
for bus_num in bus_list:
    try:
        bus = smbus.SMBus(bus_num)
        # 尝试读取设备...
    except Exception:
        continue
```

### 3. 数据修正机制

当 UV 指数读取异常时，使用原始值计算 UV 指数：

```python
def read_UV_index_data(self):
    """读取UV指数数据"""
    try:
        # 尝试直接读取UV指数...
        if uv_index == 0 or uv_index > 20:  # UV指数异常
            # 使用原始值计算UV指数
            raw_value = self.read_UV_original_data()
            uv_index = max(0, min(11, int(raw_value / 1800)))
        return uv_index
    except Exception:
        return 0
```

### 4. 模拟模式支持

当硬件不可用时，提供模拟数据以便于开发和测试：

```python
def read_UV_original_data(self):
    """读取紫外线原始数据"""
    # 模拟模式返回模拟数据
    if self._simulation_mode:
        # 生成随机波动数据
        self._last_raw_value = max(100, min(20000,
                                  self._last_raw_value + random.randint(-500, 500)))
        return self._last_raw_value

    # 实际硬件读取...
```

## 关键参数

| 参数名              | 值     | 描述                |
| ------------------- | ------ | ------------------- |
| DEVICE_ADDR         | 0x23   | 默认 I2C 设备地址   |
| DEVICE_ADDR_ALT     | 0x38   | 备用 I2C 设备地址   |
| REG_PID             | 0x00   | 设备 ID 寄存器地址  |
| DEVICE_PID          | 0x427c | 标准设备 ID         |
| DEVICE_PID_REVERSED | 0x7c42 | 字节序颠倒的设备 ID |
| REG_DATA            | 0x06   | 原始数据寄存器地址  |
| REG_INDEX           | 0x07   | UV 指数寄存器地址   |
| REG_RISK            | 0x08   | 风险等级寄存器地址  |

## 数据转换

UV 指数转换算法：

```python
# 简化版UV指数计算方法
uv_index = max(0, min(11, int(raw_value / 1800)))
```

风险等级定义：

- 0: 低风险 (UV 指数 0-2)
- 1: 中等风险 (UV 指数 3-5)
- 2: 高风险 (UV 指数 6-7)
- 3: 很高风险 (UV 指数 8-10)
- 4: 极高风险 (UV 指数 11+)

## 扩展开发

### 添加新功能

要添加新功能：

1. 在`unihiker_uv_patch_v2.py`中添加新方法
2. 更新`main.ts`文件添加新积木定义
3. 更新本地化文件添加新积木的翻译

### 修改数据处理方法

可以通过修改以下方法定制数据处理：

- `read_UV_original_data()`: 修改原始数据处理
- `read_UV_index_data()`: 修改 UV 指数计算
- `read_risk_level_data()`: 修改风险等级计算
