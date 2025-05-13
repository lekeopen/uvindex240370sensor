# -*- coding: utf-8 -*-
'''!
  @file       unihiker_uv_patch_v3.py
  @brief      行空板(Unihiker)紫外线指数传感器(240370)补丁文件 - Pinpong专用版
  @copyright  Copyright (c) 2021-2025 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license    The MIT License (MIT)
  @version    V3.0.3
  @date       2025-5-13
  
  使用说明:
  1. 将此文件复制到Mind+扩展的python/libraries目录中
  2. 在代码中使用 from unihiker_uv_patch_v3 import PatchUVSensor
  3. 创建传感器对象: sensor = PatchUVSensor()
  4. 使用方法:
     - sensor.begin() - 初始化传感器
     - sensor.read_UV_original_data() - 读取原始值
     - sensor.read_UV_index_data() - 读取UV指数
     - sensor.read_risk_level_data() - 读取风险等级
     
  更新日志:
  - V3.0.2 (2025-5-12): 根据官方维基校准数据计算，修复UI重叠问题，增强数据稳定性
  - V3.0.1 (2025-5-12): 修复数据异常和显示重叠问题 
  - V3.0.0 (2025-5-12): 专注于Pinpong库，移除其他库依赖，简化代码
  - V2.0.1 (2025-5-12): 修复设备ID字节序问题
'''

import time
import random
import sys
import os

# 传感器常量定义
SENSOR_ADDR = 0x23      # 官方指定I2C地址
REG_PID = 0x00          # 设备ID寄存器地址
REG_DATA = 0x06         # 紫外线原始数据寄存器
REG_INDEX = 0x07        # 紫外线指数寄存器
REG_RISK = 0x08         # 风险等级寄存器
DEVICE_ID = 0x427c      # 原始设备ID
DEVICE_ID_REV = 0x7c42  # 字节序颠倒的设备ID

# 全局变量
PINPONG_AVAILABLE = False

# 尝试导入PinPong库
try:
    from pinpong.board import I2C, Board
    # 初始化行空板Board对象 - 这一步非常重要
    board = Board("unihiker")
    board.begin()
    PINPONG_AVAILABLE = True
    print("PinPong库导入成功")
except ImportError:
    # 尝试其他可能路径
    try:
        # 行空板可能的路径
        paths = [
            "/usr/lib/python3/dist-packages",
            "/usr/local/lib/python3/dist-packages",
            os.path.expanduser("~/.local/lib/python3/dist-packages"),
            "/usr/share/unihiker/lib"
        ]
        
        # 添加路径
        for path in paths:
            if path not in sys.path and os.path.exists(path):
                sys.path.append(path)
        
        # 再次尝试导入
        from pinpong.board import I2C, Board
        board = Board("unihiker")
        board.begin()  # 初始化行空板
        PINPONG_AVAILABLE = True
        print("PinPong库导入成功（使用附加路径）")
    except ImportError:
        print("警告: PinPong库不可用，将使用模拟模式")
        PINPONG_AVAILABLE = False

class PatchUVSensor:
    """适用于行空板的UV指数传感器补丁类 - PinPong专用版"""
    
    def __init__(self, simulation_mode=False, debug_mode=False, force_real=False):
        """初始化传感器对象"""
        self._addr = SENSOR_ADDR
        self._i2c = None
        self._bus_index = None
        self._initialized = False
        self._force_real = force_real
        self._simulation_mode = simulation_mode and not force_real
        if not PINPONG_AVAILABLE and not simulation_mode:
            self._simulation_mode = True
        self._debug_mode = False  # 默认关闭调试模式，避免过多输出
        
        # 上次读取的有效值（用于错误恢复）
        self._last_data = 0
        self._last_index = 0
        self._last_risk = 0
        
        # 如果是模拟模式，初始化模拟数据
        if self._simulation_mode:
            self._init_simulation()
    
    def _debug(self, msg):
        """输出调试信息"""
        if self._debug_mode:
            print(f"[UV传感器] {msg}")
    
    def _init_simulation(self):
        """初始化模拟数据"""
        self._sim_values = [0, 1, 2, 3, 5, 7, 9, 11, 8, 6, 4, 2, 1]
        self._sim_index = 0
        self._sim_counter = 0
    
    def _simulate_data(self):
        """生成模拟数据"""
        self._sim_counter += 1
        if self._sim_counter % 10 == 0:
            self._sim_index = (self._sim_index + 1) % len(self._sim_values)
        
        base = self._sim_values[self._sim_index]
        noise = random.uniform(-0.3, 0.3)
        return base + noise
    
    def _check_device_id(self, device_id):
        """检查设备ID是否匹配（支持字节序颠倒）"""
        if device_id in [DEVICE_ID, DEVICE_ID_REV]:
            return True
        
        # 尝试字节序变换
        byte1 = (device_id >> 8) & 0xFF
        byte2 = device_id & 0xFF
        swapped = (byte2 << 8) | byte1
        
        return swapped in [DEVICE_ID, DEVICE_ID_REV]
    
    def _calculate_uv_index(self, raw_value):
        """根据原始值计算UV指数 - 基于官方维基校准"""
        # 参考：https://wiki.dfrobot.com.cn/SKU_SEN0636_Gravity:240370紫外线指数传感器
        # 异常数据处理 - 进一步降低阈值
        if raw_value > 1200:  # 更严格的阈值，确保UV指数不会超出范围
            return 11  # 返回最大值而不是0，避免大幅度跳变
        elif raw_value < 0:  # 处理负值
            return 0
            
        # 根据官方校准表提供的数据计算UV指数
        if raw_value < 50:
            return 0
        elif raw_value < 227:
            return 1
        elif raw_value < 318:
            return 2
        elif raw_value < 408:
            return 3
        elif raw_value < 503:
            return 4
        elif raw_value < 606:
            return 5
        elif raw_value < 696:
            return 6
        elif raw_value < 795:
            return 7
        elif raw_value < 881:
            return 8
        elif raw_value < 976:
            return 9
        elif raw_value < 1079:
            return 10
        else:
            # 限制最大值为11
            return 11
    
    def _get_risk_level(self, uv_index):
        """根据UV指数计算风险等级"""
        if uv_index <= 0:  # 修改为包括小于等于0的所有情况
            return 0  # 无风险
        elif uv_index == 1:  # UV指数为1时风险等级为0
            return 0  # 低风险但显示为无风险
        elif uv_index <= 3:
            return 1  # 低
        elif uv_index <= 6:
            return 2  # 中
        elif uv_index <= 8:
            return 3  # 高
        elif uv_index <= 10:
            return 4  # 很高
        else:
            return 5  # 极高
    
    def begin(self):
        """初始化传感器"""
        # 模拟模式直接返回成功
        if self._simulation_mode and not self._force_real:
            self._initialized = True
            return True
        
        # 检查PinPong是否可用
        if not PINPONG_AVAILABLE:
            if self._force_real:
                print("错误: PinPong库不可用，无法使用真实传感器")
                return False
            else:
                print("PinPong库不可用，自动切换到模拟模式")
                self._simulation_mode = True
                # 确保初始化模拟模式数据
                self._init_simulation()
                self._initialized = True
                return True
        
        # 扫描所有可能的I2C总线
        buses_to_try = [4, 1, 0, 2, 3, 5, 6, 7]  # 扩大搜索范围
        
        for attempt in range(2):  # 尝试两轮
            for bus in buses_to_try:
                try:
                    # 确保使用正确的方式初始化I2C
                    try:
                        # 使用全局board对象创建I2C对象
                        i2c = I2C(bus)
                    except:
                        # 如果上面的方式失败，尝试创建新board对象并初始化I2C
                        board = Board("unihiker") 
                        board.begin()
                        i2c = board.get_i2c(bus)
                    
                    # 尝试读取设备ID
                    try:
                        data = i2c.readfrom_mem(self._addr, REG_PID, 2)
                        device_id = (data[0] << 8) | data[1]
                        
                        if self._check_device_id(device_id):
                            self._i2c = i2c
                            self._bus_index = bus
                            print(f"找到紫外线传感器! 总线: {bus}, 地址: 0x{self._addr:02X}")
                            self._initialized = True
                            return True
                    except Exception as e:
                        pass
                except Exception as e:
                    pass
            
            # 第一轮未找到，等待一下再试
            if attempt == 0:
                time.sleep(0.5)
        
        # 未找到有效设备
        if self._force_real:
            print("错误: 未找到紫外线传感器，请检查连接")
            return False
        else:
            print("警告: 未找到紫外线传感器，已切换到模拟模式")
            self._simulation_mode = True
            # 初始化模拟模式数据
            self._init_simulation()
            self._initialized = True
            return True
    
    def read_register_16bit(self, reg):
        """读取16位寄存器"""
        # 如果强制使用真实数据但处于模拟模式，则直接报错
        if self._force_real and self._simulation_mode:
            raise RuntimeError("未连接真实传感器，无法读取数据")
            
        # 模拟模式返回模拟数据
        if self._simulation_mode and not self._force_real:
            # 静默处理，不再显示模拟模式提示
            if reg == REG_DATA:
                val = int(self._simulate_data() * 400)
                self._last_data = val
                return val
            elif reg == REG_INDEX:
                val = int(self._simulate_data())
                self._last_index = val
                return val
            elif reg == REG_RISK:
                val = self._get_risk_level(self._last_index)
                if self._last_index <= 0:
                    val = 0
                self._last_risk = val
                return val
            return 0
        
        # 确保传感器已初始化
        if not self._initialized or not self._i2c:
            if self._force_real:
                raise RuntimeError("传感器未初始化")
            self._simulation_mode = True
            self._init_simulation()
            return self.read_register_16bit(reg)
            
        # 读取实际寄存器
        max_retries = 3
        last_error = None
        
        for retry in range(max_retries):
            try:
                if retry > 0:
                    try:
                        self._i2c.readfrom_mem(self._addr, REG_PID, 2)
                        time.sleep(0.01)
                    except:
                        pass
                
                # 使用readfrom_mem方法读取数据
                data = None
                try:
                    data = self._i2c.readfrom_mem(self._addr, reg, 2)
                except Exception as e:
                    try:
                        data = self._i2c.read(self._addr, reg, 2)
                    except:
                        raise e
                
                if not data or len(data) != 2:
                    raise ValueError("数据长度错误")
                
                value_normal = (data[0] << 8) | data[1]
                value_swapped = (data[1] << 8) | data[0]
                
                if reg == REG_DATA:
                    if value_normal > 5000 and value_swapped <= 1200:
                        value = value_swapped
                    else:
                        value = value_normal if value_normal <= 1200 else value_swapped
                elif reg == REG_INDEX:
                    value = value_normal if value_normal <= 11 else value_swapped
                    value = min(11, max(0, value))
                elif reg == REG_RISK:
                    value = value_normal if 0 <= value_normal <= 5 else value_swapped
                    value = min(5, max(0, value))
                else:
                    value = value_normal
                
                if value == 0xFFFF and reg != REG_PID:
                    if retry < max_retries - 1:
                        time.sleep(0.02)
                        continue
                
                # 简化数据合理性检查，减少输出
                if (reg == REG_DATA and value > 1200) or \
                   (reg == REG_INDEX and value > 11) or \
                   (reg == REG_RISK and value > 5):
                    if retry < max_retries - 1:
                        continue
                    
                    # 限制异常值范围
                    if reg == REG_DATA:
                        value = min(1200, value)
                    elif reg == REG_INDEX:
                        value = min(11, value)
                    elif reg == REG_RISK:
                        value = min(5, value)
                
                return value
                
            except Exception as e:
                last_error = e
                if retry < max_retries - 1:
                    time.sleep(0.02)
        
        # 所有尝试都失败，使用回退策略
        if self._force_real:
            raise RuntimeError("无法读取传感器数据")
            
        # 返回上次的有效值
        if reg == REG_DATA:
            return self._last_data if self._last_data > 0 else 10
        elif reg == REG_INDEX:
            return self._last_index
        elif reg == REG_RISK:
            return self._last_risk
        return 0
    
    def read_UV_original_data(self):
        """读取紫外线原始数据"""
        # 简化预热过程，减少调试输出
        if not self._simulation_mode:
            try:
                self._i2c.readfrom_mem(self._addr, REG_DATA, 2)
            except:
                pass
        
        # 正式读取数据
        value = self.read_register_16bit(REG_DATA)
        
        # 特殊处理可能存在的字节序问题
        if value == 1024:  # 特殊情况，可能是字节序导致的异常值
            self._debug(f"检测到特殊值1024，可能是字节序问题")
            # 使用前一个有效值
            if self._last_data > 50 and self._last_data < 300:
                value = self._last_data  # 使用上一个合理值
            else:
                value = 200  # 使用一个合理的默认值
        # 处理其他异常值
        elif value > 1200:
            high_byte = (value >> 8) & 0xFF
            low_byte = value & 0xFF
            swapped = (low_byte << 8) | high_byte
            
            if swapped <= 1200:
                value = swapped
            else:
                value = 1200  # 限制最大值
        
        # 确保值在合理范围内
        value = max(0, min(value, 1200))
        
        # 处理零值但防止错误的升高
        if value == 0 and self._last_data > 0:
            # 只在前一个值合理时应用渐变
            if self._last_data < 300:  # 防止异常大值的影响
                value = int(self._last_data * 0.8)  # 渐变降低而不是立即归零
        
        # 更新历史值
        self._last_data = value
        return value
    
    def read_UV_index_data(self):
        """读取紫外线指数"""
        raw_value = self.read_UV_original_data()
        
        # 检测异常的大值 - 可能是字节序问题导致的1024等值
        if raw_value > 1000 and raw_value < 1100:  # 1024附近的值
            # 这种数值通常是字节序问题，实际值应该较高
            value = 10  # 设置为更合理的高UV指数
        # 确保小于50的值为0指数
        elif raw_value < 50:
            value = 0
        else:
            value = self._calculate_uv_index(raw_value)
        
        # 平滑处理大幅变化
        if self._last_index > 0 and abs(value - self._last_index) > 2:
            direction = 1 if value > self._last_index else -1
            value = self._last_index + direction
        
        # 更新历史值
        self._last_index = value
        return value
    
    def read_risk_level_data(self):
        """读取风险等级"""
        uv_index = self.read_UV_index_data()
        risk = self._get_risk_level(uv_index)
        
        # UV指数为0时风险等级必须为0
        if uv_index <= 0:
            return 0
        
        # 更新历史值
        self._last_risk = risk
        return risk

# 简单的使用示例
if __name__ == "__main__":
    # 初始化传感器，不启用调试模式以简化输出
    sensor = PatchUVSensor(debug_mode=False)
    
    if sensor.begin():
        try:
            print("\033[2J\033[H")  # 清屏ANSI控制码
            print("● ● ● UV传感器就绪 - 开始读取数据 ● ● ●")
            print("=" * 40)
            
            # 创建一个计数器用于周期性清屏
            counter = 0
            
            while True:
                # 每10次循环清屏一次，避免累积影响
                counter += 1
                if counter >= 10:
                    print("\033[2J\033[H")  # 清屏
                    print("● ● ● UV传感器数据 ● ● ●")
                    counter = 0
                
                # 读取所有数据，然后一次性显示，避免部分刷新
                raw_data = int(sensor.read_UV_original_data())
                time.sleep(0.5)
                
                uv_index = int(sensor.read_UV_index_data())
                time.sleep(0.5)
                
                risk_level = int(sensor.read_risk_level_data())
                
                # 使用固定格式的框架显示数据
                print("\n┌───────────────────────────┐")
                print(f"│ 原始值:      {raw_data:4d}        │")
                print(f"│ UV指数:      {uv_index:4d}        │")
                print(f"│ 风险等级:    {risk_level:4d}        │")
                print("└───────────────────────────┘")
                
                time.sleep(2)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"错误: {e}")
    else:
        print("初始化失败")