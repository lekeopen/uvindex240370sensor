# -*- coding: utf-8 -*-
'''!
  @file       unihiker_uv_patch_v3.py
  @brief      行空板(Unihiker)紫外线指数传感器(240370)补丁文件 - Pinpong专用版
  @copyright  Copyright (c) 2021-2025 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license    The MIT License (MIT)
  @version    V3.0.2
  @date       2025-5-12
  
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
        self._last_risk = 1  # 默认风险等级为1（低）
        
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
        # 异常数据处理
        if raw_value > 10000:
            self._debug(f"异常大的原始值: {raw_value}，可能是读取错误")
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
        if uv_index <= 2:
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
                self._last_risk = val
                return val
            return 0
        
        # 读取实际寄存器 - 增强错误处理功能
        for retry in range(3):  # 最多重试3次
            try:
                # 使用readfrom_mem方法读取数据 (适配PinPong库)
                data = self._i2c.readfrom_mem(self._addr, reg, 2)
                value = (data[0] << 8) | data[1]
                
                # 第一次成功读取时提示用户
                if not hasattr(self, '_real_data_notice_shown'):
                    print("✓ 正在读取真实传感器数据")
                    self._real_data_notice_shown = True
                
                # 检查数据有效性 - 一些寄存器可能返回0xFFFF表示无效
                if value == 0xFFFF and reg != REG_PID:  # 设备ID可能是0xFFFF
                    if retry < 2:  # 如果不是最后一次尝试
                        self._debug(f"读取到无效数据0xFFFF，重试({retry+1}/3)...")
                        time.sleep(0.01)  # 短暂延迟后重试
                        continue
                    else:
                        # 最后一次尝试仍失败，使用上次有效值
                        self._debug("多次读取到无效数据，使用上次有效值")
                        break
                
                # 数据有效，返回
                return value
                
            except Exception as e:
                if retry < 2:  # 如果不是最后一次尝试
                    self._debug(f"读取寄存器0x{reg:02X}失败: {e}，重试({retry+1}/3)...")
                    time.sleep(0.01)  # 短暂延迟后重试
                else:
                    self._debug(f"读取寄存器0x{reg:02X}失败: {e}，使用上次有效值")
        
        # 所有尝试都失败，使用回退策略
        # 如果强制要求真实数据，则抛出异常
        if self._force_real:
            raise RuntimeError(f"无法读取真实传感器数据，多次尝试均失败")
            
        # 返回上次的有效值
        if reg == REG_DATA:
            return self._last_data
        elif reg == REG_INDEX:
            return self._last_index
        elif reg == REG_RISK:
            return self._last_risk
        return 0
    
    def read_UV_original_data(self):
        """读取紫外线原始数据"""
        value = self.read_register_16bit(REG_DATA)
        
        # 数据有效性检查
        if value > 10000:  # 修改阈值为更合理的10000
            self._debug(f"异常大的原始值: {value}，尝试修正")
            
            # 尝试字节序交换
            high_byte = (value >> 8) & 0xFF
            low_byte = value & 0xFF
            swapped = (low_byte << 8) | high_byte
            
            if swapped < 5000:  # 更严格的合理范围检查
                self._debug(f"使用字节序交换后的值: {swapped}")
                value = swapped
            else:
                # 限制到合理范围
                if self._last_data > 0:
                    self._debug(f"无法修正异常值，使用上次有效值: {self._last_data}")
                    return self._last_data
                else:
                    value = value % 2000  # 强制限制在更小的范围内
                    self._debug(f"原始值被限制为: {value}")
        
        # 确保值在合理范围内 - 根据官方文档更严格的限制
        value = max(0, min(value, 5000))
        
        # 如果值为0但之前有效，可能是读取错误
        if value == 0 and self._last_data > 0:
            self._debug("检测到0值，可能是读取错误，保留上次有效值")
            return self._last_data
        
        # 使用平滑滤波 - 如果有上次值，做一些平滑处理
        if self._last_data > 0:
            # 如果新值与旧值差异过大（超过50%），怀疑是异常读数
            if abs(value - self._last_data) > (self._last_data * 0.5):
                self._debug(f"读数跳变过大 ({self._last_data} -> {value})，使用平滑处理")
                # 使用加权平均 - 新值占30%，旧值占70%
                value = int(0.3 * value + 0.7 * self._last_data)
                
        self._last_data = value
        return value
    
    def read_UV_index_data(self):
        """读取紫外线指数"""
        # 直接从原始值计算UV指数，更可靠
        raw_value = self.read_UV_original_data()
        
        # 如果原始值有效（大于50），使用计算方式
        if raw_value >= 50:
            value = self._calculate_uv_index(raw_value)
            self._debug(f"从原始值 {raw_value} 计算UV指数: {value}")
        else:
            # 如果原始值无效，尝试读取寄存器的值
            value = self.read_register_16bit(REG_INDEX)
            
            # 如果寄存器值异常，使用上次有效值
            if value > 11:
                if self._last_index > 0:
                    self._debug(f"寄存器UV指数 {value} 异常，使用上次值: {self._last_index}")
                    value = self._last_index
                else:
                    self._debug(f"寄存器UV指数 {value} 异常，重置为0")
                    value = 0
        
        # 确保值在合理范围内 (0-11)
        value = max(0, min(value, 11))
        
        # 如果值为0但之前有效且在室内不太可能为0，可能是读取错误
        if value == 0 and self._last_index > 0:
            self._debug("检测到0值指数，可能是读取错误，保留上次有效值")
            return self._last_index
            
        self._last_index = value
        return value
    
    def read_risk_level_data(self):
        """读取风险等级"""
        value = self.read_register_16bit(REG_RISK)
        
        # 如果风险等级不在合理范围内，从UV指数计算
        if value < 1 or value > 5:
            uv_index = self.read_UV_index_data()
            value = self._get_risk_level(uv_index)
            self._debug(f"从UV指数 {uv_index} 计算风险等级: {value}")
        
        # 确保值在有效范围内(1-5)
        value = max(1, min(value, 5))
        self._last_risk = value
        return value

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
                risk_texts = ["", "低", "中", "高", "很高", "极高"]
                risk_text = risk_texts[risk_level] if 1 <= risk_level <= 5 else "未知"
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