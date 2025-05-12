# Gravity: 240370 紫外线指数传感器安装指南

本文档提供了在行空板(UniHiker)上安装和使用 Gravity: 240370 紫外线指数传感器的详细说明。

## 安装方法

### 方法一：通过 Mind+导入扩展包

1. 打开[Mind+软件](http://www.mindplus.cc/)
2. 选择"扩展"→"用户库"
3. 点击"导入"按钮
4. 选择下载的`lekeopen-uvindex240370sensor-V1.0.1.mpext`扩展包
5. 重启 Mind+软件，在扩展库中即可找到"Gravity: 240370 紫外线指数传感器"

### 方法二：通过脚本直接安装到行空板

如果您想直接在行空板上使用 Python 代码访问传感器，可以使用部署脚本：

```bash
# 部署到默认行空板(unihiker.local)
./deploy_to_unihiker.sh

# 部署到指定IP的行空板
./deploy_to_unihiker.sh unihiker 192.168.1.xxx
```

## 硬件连接

请按照以下步骤连接 Gravity: 240370 紫外线指数传感器到行空板：

1. 将传感器板上的拨码开关调至"I2C"一侧
2. 按照以下方式连接：

   | 传感器引脚 | 行空板引脚 |
   | ---------- | ---------- |
   | D/R (SDA)  | I2C SDA    |
   | C/T (SCL)  | I2C SCL    |
   | GND        | GND        |
   | VCC        | 3.3V/5V    |

3. 确保连接牢固，避免接触不良

## 测试安装

安装完成后，可以运行测试脚本验证传感器功能：

```bash
# 如果您使用方法一安装
cd examples
python3 test_uv_sensor_v3.py

# 如果您使用方法二安装
ssh unihiker@unihiker.local
python3 -c "from unihiker_uv_patch_v3 import PatchUVSensor; sensor = PatchUVSensor(); print('初始化:', sensor.begin()); print('UV指数:', sensor.read_UV_index_data())"
```

## 排错指南

如果遇到问题，请检查：

1. **I2C 通信错误**：确认拨码开关位于 I2C 一侧，并检查接线是否正确
2. **传感器无法初始化**：检查电源连接，确保电压在 3.3V-5V 范围内
3. **读取数据异常**：将传感器放置在紫外线源下(如阳光下)进行测试
4. **Python 导入错误**：确认库文件已正确安装到行空板的系统路径

## 更多资源

- [详细用户指南](docs/USER_GUIDE.md)
- [技术规格文档](docs/TECHNICAL_SPEC.md)
- [官方产品库](https://wiki.dfrobot.com.cn/SKU_SEN0636_Gravity:%20240370%E7%B4%AB%E5%A4%96%E7%BA%BF%E6%8C%87%E6%95%B0%E4%BC%A0%E6%84%9F%E5%99%A8)
- [项目 GitHub 仓库](https://github.com/username/lekeopen-uvindex240370sensor)
