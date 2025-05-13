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
        self._force_real = force_real  # 如果为True，则强制使用真实传感器，不使用模拟模式
        self._simulation_mode = simulation_mode and not force_real
        if not PINPONG_AVAILABLE and not simulation_mode:
            self._simulation_mode = True  # 没有PinPong库时才自动切换到模拟模式
        self._debug_mode = debug_mode
        
        # 上次读取的有效值（用于错误恢复）
        self._last_data = 0
        self._last_index = 0
        self._last_risk = 0  # 默认风险等级为0（无风险）
        
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
        self._debug("初始化模拟模式")
    
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
            self._debug(f"异常大的原始值: {raw_value}，已超出正常范围，强制返回最大值11")
            return 11  # 返回最大值而不是0，避免大幅度跳变
        elif raw_value < 0:  # 处理负值
            self._debug(f"检测到负值原始数据: {raw_value}，强制返回0")
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
        elif uv_index <= 2:
            return 1  # 低
        elif uv_index <= 5:
            return 2  # 中
        elif uv_index <= 7:
            return 3  # 高
        elif uv_index <= 10:
            return 4  # 很高
        else:
            return 5  # 极高
    
    def begin(self):
        """初始化传感器"""
        # 模拟模式直接返回成功
        if self._simulation_mode and not self._force_real:
            self._debug("使用模拟模式")
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
        self._debug("开始全面扫描I2C总线...")
        # 扩大搜索范围，包含更多可能的总线
        buses_to_try = [4, 1, 0, 2, 3, 5, 6, 7]  # 扩大搜索范围
        
        for attempt in range(2):  # 尝试两轮
            for bus in buses_to_try:
                try:
                    self._debug(f"尝试总线 {bus}...（尝试 {attempt+1}/2）")
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
                        self._debug(f"总线{bus}地址0x{self._addr:02X}的设备ID: 0x{device_id:04X}")
                        
                        if self._check_device_id(device_id):
                            self._debug(f"✓ 总线{bus}上找到紫外线传感器(地址0x{self._addr:02X})")
                            self._i2c = i2c
                            self._bus_index = bus
                            print(f"找到紫外线传感器! 总线: {bus}, 地址: 0x{self._addr:02X}")
                            self._initialized = True
                            return True
                        else:
                            self._debug(f"设备ID不匹配: 0x{device_id:04X}")
                    except Exception as e:
                        self._debug(f"读取设备ID失败: {e}")
                except Exception as e:
                    self._debug(f"总线{bus}初始化失败: {e}")
            
            # 第一轮未找到，等待一下再试
            if attempt == 0:
                self._debug("第一轮扫描未找到传感器，等待0.5秒后重试...")
                time.sleep(0.5)
        
        # 未找到有效设备
        if self._force_real:
            print("错误: 未找到紫外线传感器，请检查连接")
            return False
        else:
            self._debug("未找到紫外线传感器，切换到模拟模式")
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
            # 第一次读取时提示用户当前是模拟数据
            if not hasattr(self, '_simulation_warning_shown'):
                print("注意：当前使用模拟数据，非实际传感器读数")
                self._simulation_warning_shown = True
                
            if reg == REG_DATA:
                val = int(self._simulate_data() * 400)  # 模拟原始值
                self._last_data = val
                return val
            elif reg == REG_INDEX:
                val = int(self._simulate_data())  # 模拟指数值
                self._last_index = val
                return val
            elif reg == REG_RISK:
                val = self._get_risk_level(self._last_index)  # 模拟风险等级
                # 确保UV指数为0时风险等级也为0
                if self._last_index <= 0:
                    val = 0
                self._last_risk = val
                return val
            return 0
        
        # 增加稳定性：确保传感器已初始化
        if not self._initialized or not self._i2c:
            if self._force_real:
                raise RuntimeError("传感器未初始化，无法读取数据")
            self._debug("传感器未初始化，返回模拟数据")
            # 切换到模拟模式
            self._simulation_mode = True
            self._init_simulation()
            return self.read_register_16bit(reg)  # 递归调用，将返回模拟数据
            
        # 增加多次重试机制
        max_retries = 5  # 增加重试次数
        last_error = None
        
        # 读取前预热总线 - 减少首次读取错误
        if not hasattr(self, '_bus_warmed_up'):
            try:
                # 尝试读取设备ID作为总线预热
                self._i2c.readfrom_mem(self._addr, REG_PID, 2)
                time.sleep(0.05)  # 稍长的延迟，确保总线稳定
                self._bus_warmed_up = True
            except:
                pass
        
        # 读取实际寄存器 - 增强错误处理功能和稳定性
        max_retries = 4  # 增加重试次数
        last_error = None
        
        for retry in range(max_retries):
            try:
                # 每次都清除可能的总线错误
                if retry > 0:
                    try:
                        # 重置i2c总线 - 尝试重新读取设备ID
                        self._i2c.readfrom_mem(self._addr, REG_PID, 2)
                        time.sleep(0.01 * (retry + 1))  # 逐渐增加延迟时间
                    except:
                        pass
                
                # 使用readfrom_mem方法读取数据 (适配PinPong库)
                data = None
                try:
                    data = self._i2c.readfrom_mem(self._addr, reg, 2)
                except Exception as e:
                    # 特殊处理总线错误
                    self._debug(f"总线读取错误: {e}，尝试替代读取方法")
                    # 尝试直接读取 - 一些PinPong版本有不同的API
                    try:
                        data = self._i2c.read(self._addr, reg, 2)
                    except:
                        raise e  # 如果替代方法也失败，抛出原始异常
                
                # 确保获取到2字节数据
                if not data or len(data) != 2:
                    raise ValueError(f"数据长度错误: {len(data) if data else 0}，需要2字节")
                
                # 尝试两种字节顺序，选择更合理的
                value_normal = (data[0] << 8) | data[1]  # 正常顺序
                value_swapped = (data[1] << 8) | data[0]  # 交换顺序
                
                # 根据寄存器选择更合理的值
                if reg == REG_DATA:
                    # 对于原始数据，合理范围通常是0-5000
                    value = value_normal if value_normal <= 5000 else value_swapped
                    if value_swapped <= 5000 and (value_normal > 5000 or value_swapped > 0):
                        self._debug(f"自动修正字节顺序: {value_normal} -> {value_swapped}")
                elif reg == REG_INDEX:
                    # UV指数范围通常是0-11
                    value = value_normal if value_normal <= 11 else value_swapped
                elif reg == REG_RISK:
                    # 风险等级范围通常是1-5
                    value = value_normal if 1 <= value_normal <= 5 else value_swapped
                    if not (1 <= value <= 5):
                        value = max(1, min(5, value))  # 强制限制在1-5范围
                else:
                    # 其他寄存器使用正常字节顺序
                    value = value_normal
                
                # 第一次成功读取时提示用户
                if not hasattr(self, '_real_data_notice_shown'):
                    print("✓ 正在读取真实传感器数据")
                    self._real_data_notice_shown = True
                
                # 检查数据有效性 - 一些寄存器可能返回0xFFFF表示无效
                if value == 0xFFFF and reg != REG_PID:
                    if retry < max_retries - 1:
                        self._debug(f"读取到无效数据0xFFFF，重试({retry+1}/{max_retries})...")
                        time.sleep(0.02)  # 稍长的延迟后重试
                        continue
                    else:
                        self._debug("多次读取到无效数据，使用上次有效值")
                        break
                
                # 数据合理性检查
                if reg == REG_DATA and value > 5000:
                    if retry < max_retries - 1:
                        self._debug(f"读取到异常原始值{value}，重试...")
                        continue
                elif reg == REG_INDEX and value > 11:
                    if retry < max_retries - 1:
                        self._debug(f"读取到异常UV指数{value}，重试...")
                        continue
                elif reg == REG_RISK and (value < 1 or value > 5):
                    if retry < max_retries - 1:
                        self._debug(f"读取到异常风险等级{value}，重试...")
                        continue
                
                # 数据有效，返回
                return value
                
            except Exception as e:
                last_error = e
                if retry < max_retries - 1:
                    self._debug(f"读取寄存器0x{reg:02X}失败: {e}，重试({retry+1}/{max_retries})...")
                    time.sleep(0.02 * (retry + 1))  # 逐渐增加延迟时间
                else:
                    self._debug(f"读取寄存器0x{reg:02X}失败: {e}，使用上次有效值")
        
        # 所有尝试都失败，使用回退策略
        # 如果强制要求真实数据，则抛出异常
        if self._force_real:
            raise RuntimeError(f"无法读取真实传感器数据，错误: {last_error}")
            
        # 返回上次的有效值
        if reg == REG_DATA:
            return self._last_data if self._last_data > 0 else 10  # 默认低值防止零读数
        elif reg == REG_INDEX:
            return self._last_index if self._last_index > 0 else 0
        elif reg == REG_RISK:
            return self._last_risk if self._last_risk > 0 else 0  # 修正：默认风险等级为0（无风险）
        return 0
    
    def read_UV_original_data(self):
        """读取紫外线原始数据"""
        # 增加一个额外的读取，丢弃第一次读取结果
        # 这有助于清除总线上的脏数据或不完整的传输
        if not self._simulation_mode:
            try:
                # 增加预热次数，连续丢弃多次读取结果
                for _ in range(3):  # 连续预热多次
                    self._i2c.readfrom_mem(self._addr, REG_DATA, 2)
                    time.sleep(0.01)  # 短暂延迟
            except:
                pass
        
        # 正式读取数据
        value = self.read_register_16bit(REG_DATA)
        
        # 数据有效性检查 - 处理异常值
        if value > 10000:  # 处理 10000+ 的大值，通常是字节序问题
            self._debug(f"异常大的原始值: {value}，尝试修正")
            
            # 首先尝试字节序交换
            high_byte = (value >> 8) & 0xFF
            low_byte = value & 0xFF
            swapped = (low_byte << 8) | high_byte
            
            self._debug(f"使用字节序交换后的值: {swapped}")
            
            # 判断交换后的值是否更合理
            if 0 <= swapped <= 5000:
                value = swapped
            elif self._last_data > 0:
                # 如果历史数据存在且当前值变化太大，可能是数据异常
                if abs(value - self._last_data) > 3000:
                    self._debug(f"读数跳变过大 ({self._last_data} -> {value})，使用平滑处理")
                    # 使用历史数据为主的平滑值
                    value = int(0.05 * swapped + 0.95 * self._last_data)
            else:
                # 没有历史值时，取保守值
                value = min(swapped, value % 1000)  # 取较小的值
        
        # 确保值在合理范围内 - 处理极端值
        max_allowed = 5000  # 最大允许原始值
        if value > max_allowed:
            if self._last_data > 0:
                # 限制突变幅度
                max_change = self._last_data * 0.5  # 允许最多50%的变化
                limited_value = min(value, self._last_data + max_change)
                self._debug(f"原始值 {value} 超出合理范围，限制为 {limited_value}")
                value = limited_value
            else:
                value = max_allowed
        
        # 零值处理 - 更严格的零值处理策略
        if value == 0:
            # 当前读数为0
            if not hasattr(self, '_zero_count'):
                self._zero_count = 0
                
            if self._last_data > 0:
                # 有上次有效值且当前读数为0
                self._zero_count += 1
                self._debug("检测到0值，可能是读取错误，保留上次有效值")
                
                # 只有连续多次读到0才接受为真正的0值
                if self._zero_count < 5:  # 增加到至少5次连续零值判定
                    return self._last_data
                else:
                    self._debug(f"连续检测到0值 ({self._zero_count}次)，接受为真实零值")
                    # 不立即归零，而是逐渐降低
                    value = int(self._last_data * 0.5)  # 逐渐降低
            else:
                # 上次值也是0，接受这个0值
                value = 0
        else:
            # 重置零值计数器
            self._zero_count = 0
        
        # 增强平滑滤波 - 使用更严格的平滑处理
        if self._last_data > 0:
            # 计算变化幅度
            change_percent = abs(value - self._last_data) / (self._last_data + 1) * 100
            
            # 更严格的平滑系数
            if change_percent > 80:  # 极大变化，几乎肯定是异常
                smooth_factor = 0.05  # 新值只有5%的权重
                self._debug(f"读数跳变过大 ({self._last_data} -> {value})，使用平滑处理")
                
                # 计算平滑后的值
                smooth_value = int(smooth_factor * value + (1 - smooth_factor) * self._last_data)
                self._debug(f"从原始值 {smooth_value} 计算UV指数: {self._calculate_uv_index(smooth_value)}")
                value = smooth_value
            elif change_percent > 50:  # 大变化
                smooth_factor = 0.2  # 新值只有20%权重
                value = int(smooth_factor * value + (1 - smooth_factor) * self._last_data)
            elif change_percent > 30:  # 中等变化
                smooth_factor = 0.5  # 新值50%权重
                value = int(smooth_factor * value + (1 - smooth_factor) * self._last_data)
        
        # 设置合理范围下限，避免出现太小的值
        value = max(0, value)
        
        # 更新历史值并返回
        self._last_data = value
        return value
    
    def read_UV_index_data(self):
        """读取紫外线指数"""
        # 可靠性优先：首选从原始值计算UV指数，这比直接读取寄存器更可靠
        raw_value = self.read_UV_original_data()
        
        # 创建存储多种计算结果的数组，用于综合判断
        values = []
        calc_value = 0  # 预先定义，避免未定义错误
        
        # 方法1: 从原始值计算UV指数 (最可靠)
        # 增加更严格的有效值判断并限制异常大的原始值
        if raw_value > 1200:  # 超过阈值的原始值直接映射到最大UV指数
            calc_value = 11
            self._debug(f"异常大的原始值: {raw_value}，限制为最大UV指数11")
        elif raw_value >= 10:  # 降低有效值门槛，更多值被视为有效
            calc_value = self._calculate_uv_index(raw_value)
            self._debug(f"从原始值 {raw_value} 计算UV指数: {calc_value}")
            values.append(calc_value)
            # 给计算值更高的权重，增加权重
            values.append(calc_value)
            values.append(calc_value)
        
        # 方法3: 如果有上次有效值，也将其考虑在内 (增加稳定性)
        if self._last_index > 0:
            values.append(self._last_index)
            # 如果原始值为0，给上次值更高权重
            if raw_value == 0:
                values.append(self._last_index)
        
        # 计算最终值
        if not values:
            # 没有可靠值，默认为0
            self._debug("无可靠UV指数读数，默认为0")
            value = 0
        elif len(values) == 1:
            # 只有一个值，直接使用
            value = values[0]
        else:
            # 多个值，使用加权平均
            # 如果原始值显示很高的UV指数，优先采用
            if raw_value >= 1000 and calc_value > self._last_index:
                value = calc_value
            elif raw_value == 0 and self._last_index > 0:
                # 读数为零但曾有非零值，保守处理
                value = int(self._last_index * 0.8)  # 缓慢降低
            else:
                # 正常情况下使用平均值
                value = int(sum(values) / len(values))
        
        # 确保值在合理范围内 (0-11)
        value = max(0, min(value, 11))
        
        # 零值特殊处理：增加更严格的零值处理策略
        if value == 0 and self._last_index > 0:
            # 使用计数器记录连续零值
            if not hasattr(self, '_zero_index_count'):
                self._zero_index_count = 1
            else:
                # 增加零值计数
                self._zero_index_count += 1
            
            # 连续5次零值才接受为真实的零值 (增加判定次数)
            if self._zero_index_count < 5:
                self._debug(f"连续检测到0值指数 ({self._zero_index_count}/5)，仍使用上次有效值")
                return self._last_index
            else:
                # 即使连续5次读到0，也不立即归零，而是逐渐降低
                new_value = max(0, self._last_index - 1)  # 每次最多降低1个等级
                self._debug(f"连续多次检测到0值指数，逐渐降低 ({self._last_index} -> {new_value})")
                value = new_value
                
        # 如果不是零值或已经处理过零值，重置计数器
        elif value > 0:
            self._zero_index_count = 0
            
        # 平滑处理：大幅变化时逐渐过渡
        if self._last_index > 0 and abs(value - self._last_index) > 2:
            # 变化超过2个单位，使用平滑过渡
            direction = 1 if value > self._last_index else -1
            smooth_value = self._last_index + direction  # 每次只变化1个单位
            self._debug(f"UV指数变化过大 ({self._last_index} -> {value})，平滑为: {smooth_value}")
            value = smooth_value
            
        # 更新历史值并返回
        self._last_index = value
        return value
    
    def read_risk_level_data(self):
        """读取风险等级"""
        # 直接从UV指数计算风险等级 - 不再尝试读取寄存器
        # 因为测试显示寄存器读取不可靠
        uv_index = self.read_UV_index_data()
        risk = self._get_risk_level(uv_index)
        self._debug(f"从UV指数 {uv_index} 计算风险等级: {risk}")
        
        # 特殊处理：UV指数为0时，风险等级必须为0
        if uv_index <= 0:
            self._last_risk = 0
            return 0
            
        # 平滑处理：避免风险等级频繁跳变
        if self._last_risk > 0 and abs(risk - self._last_risk) > 1:
            # 风险等级变化超过1级，使用渐变
            direction = 1 if risk > self._last_risk else -1
            smooth_value = self._last_risk + direction  # 每次只变化1级
            self._debug(f"风险等级变化过大 ({self._last_risk} -> {risk})，平滑为: {smooth_value}")
            risk = smooth_value
        
        # 确保风险等级在合理范围内(0-5)
        risk = max(0, min(risk, 5))
        
        # 更新历史值并返回
        self._last_risk = risk
        return risk

# 简单的使用示例
if __name__ == "__main__":
    print("===== 紫外线传感器测试程序 - PinPong专用版V3 =====")
    
    # 尝试导入额外显示所需的模块
    try:
        import os
        HAS_OS = True
    except ImportError:
        HAS_OS = False
    
    # 初始化传感器，启用调试
    sensor = PatchUVSensor(debug_mode=True)
    
    if sensor.begin():
        print("✓ 行空板紫外线传感器初始化成功！")
        
        try:
            print("\n按Ctrl+C停止程序\n")
            time.sleep(1)  # 给用户看初始信息的时间
            
            while True:
                # 清屏功能 - 避免重叠
                if HAS_OS:
                    os.system('cls' if os.name == 'nt' else 'clear')
                else:
                    # 备用ANSI清屏方法，适用于大多数终端
                    print("\033[H\033[J", end="")
                
                # 读取传感器数据
                uv_data = sensor.read_UV_original_data()
                uv_index = sensor.read_UV_index_data()
                risk_level = sensor.read_risk_level_data()
                
                # 格式化输出，固定宽度
                print("\n===== 紫外线传感器数据 =====")
                print(f"原始值:   {uv_data:6d}")  # 增加宽度和额外空格
                print(f"UV指数:   {uv_index:2d}")
                print(f"风险等级: {risk_level:2d}")
                
                # 显示风险级别文字说明
                risk_texts = ["无风险", "低", "中", "高", "很高", "极高"]
                risk_text = risk_texts[risk_level] if 0 <= risk_level <= 5 else "未知"
                print(f"风险说明: {risk_text}")
                
                # 显示数据时间
                current_time = time.strftime("%H:%M:%S", time.localtime())
                print(f"\n数据更新时间: {current_time}")
                print("=" * 30)
                
                # 等待一段时间再更新
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n程序已停止")
        except Exception as e:
            print(f"\n程序出错: {e}")
    else:
        print("✗ 紫外线传感器初始化失败")