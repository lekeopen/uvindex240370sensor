#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
紫外线传感器Mind+集成程序
使用增强版补丁库直接在本地读取紫外线传感器数据，不依赖外部库
'''

import time
import sys
import os

# 首先定义一个简化版的补丁库，直接内嵌在本文件中
class PatchUVSensor:
    """简化版行空板紫外线传感器类，直接内嵌于主程序"""
    def __init__(self, simulation_mode=False, debug_mode=True):
        self._simulation_mode = simulation_mode
        self._debug_mode = debug_mode
        self._bus = None
        self._bus_num = None
        self._address = None
        self._device_id = None
        self._is_connected = False
        import random
        self._last_raw_value = random.randint(100, 300)
        
    def _debug_print(self, msg):
        if self._debug_mode:
            print(msg)
    
    def begin(self):
        """初始化传感器，自动扫描可用总线和地址"""
        if self._simulation_mode:
            self._is_connected = True
            self._debug_print("[UV传感器] 模拟模式已激活")
            return True
        
        self._debug_print("[UV传感器] 使用SMBUS接口初始化传感器")
        return self._scan_i2c_buses()
    
    def _scan_i2c_buses(self):
        """扫描所有可能的I2C总线和地址"""
        self._debug_print("[UV传感器] 开始扫描I2C总线...")
        
        # 导入smbus库用于I2C通信
        try:
            import smbus
        except ImportError:
            self._debug_print("[UV传感器] 无法导入smbus库，尝试模拟模式")
            self._simulation_mode = True
            self._is_connected = True
            return True
        
        # 定义常量
        DEVICE_ADDR = 0x23      # 行空板上的默认地址
        DEVICE_ADDR_ALT = 0x38  # 标准地址
        REG_PID = 0x00          # PID寄存器地址
        DEVICE_PID = 0x427c     # 设备ID
        DEVICE_PID_REVERSED = 0x7c42  # 字节序颠倒的设备ID
        
        # 重点尝试总线4，因为诊断工具已经确认传感器在这个总线上
        bus_list = [4, 1, 0, 2, 3, 5, 6, 7]  # 优先尝试总线4和常用总线
        addr_list = [DEVICE_ADDR, DEVICE_ADDR_ALT]
        
        # 尝试所有总线
        for bus_num in bus_list:
            self._debug_print(f"[UV传感器] 尝试总线 {bus_num}...")
            try:
                bus = smbus.SMBus(bus_num)
                
                # 尝试常用地址
                for addr in addr_list:
                    try:
                        # 尝试读取设备ID
                        data = bus.read_i2c_block_data(addr, REG_PID, 2)
                        device_id = (data[0] << 8) | data[1]
                        self._debug_print(f"[UV传感器] 总线{bus_num}地址0x{addr:02X}的设备ID: 0x{device_id:04X}")
                        
                        # 验证设备ID，包括字节序颠倒的情况
                        if device_id == DEVICE_PID or device_id == DEVICE_PID_REVERSED:
                            # 找到了！
                            self._debug_print(f"[UV传感器] ✓ 总线{bus_num}上找到紫外线传感器(地址0x{addr:02X})")
                            self._bus = bus
                            self._bus_num = bus_num
                            self._address = addr
                            self._device_id = device_id
                            self._is_connected = True
                            print(f"🌞 紫外线传感器连接成功!")
                            print(f"总线: {bus_num}, 地址: 0x{addr:02X}")
                            return True
                    except Exception as e:
                        pass
                
                # 如果没找到，关闭总线继续尝试
                bus.close()
            except Exception:
                pass
        
        # 如果所有尝试都失败，则启用模拟模式
        self._debug_print("[UV传感器] 无法找到传感器，启用模拟模式")
        self._simulation_mode = True
        self._is_connected = True
        print("⚠️ 未找到紫外线传感器，启用模拟模式")
        return True
    
    def read_UV_original_data(self):
        """读取紫外线原始数据"""
        import random
        # 模拟模式返回模拟数据
        if self._simulation_mode:
            # 生成真实的随机波动数据
            self._last_raw_value = max(100, min(20000, self._last_raw_value + random.randint(-500, 500)))
            return self._last_raw_value
        
        # 读取数据
        try:
            REG_DATA = 0x06
            data = self._bus.read_i2c_block_data(self._address, REG_DATA, 2)
            raw_value = (data[0] << 8) | data[1]
            
            # 数据修正（如果需要）
            if raw_value > 30000:  # 异常大的值可能是字节序问题
                raw_value = ((raw_value & 0xFF) << 8) | ((raw_value >> 8) & 0xFF)
            
            return raw_value
        except Exception as e:
            self._debug_print(f"[UV传感器] 读取UV原始数据失败: {e}")
            return 0
    
    def read_UV_index_data(self):
        """读取UV指数数据"""
        # 模拟模式
        if self._simulation_mode:
            raw = self.read_UV_original_data()
            return min(11, max(0, int(raw / 1800)))
        
        # 读取数据
        try:
            REG_INDEX = 0x07
            data = self._bus.read_i2c_block_data(self._address, REG_INDEX, 2)
            uv_index = (data[0] << 8) | data[1]
            
            # 数据修正
            if uv_index > 20:  # UV指数通常不会超过20
                uv_index = min(11, max(0, uv_index % 12))
            
            return uv_index
        except Exception:
            return 0
    
    def read_risk_level_data(self):
        """读取风险等级数据"""
        # 模拟模式
        if self._simulation_mode:
            uv_index = self.read_UV_index_data()
            if uv_index <= 2:
                return 0  # 低风险
            elif uv_index <= 5:
                return 1  # 中等风险
            elif uv_index <= 7:
                return 2  # 高风险
            elif uv_index <= 10:
                return 3  # 很高风险
            else:
                return 4  # 极高风险
        
        # 读取数据
        try:
            REG_RISK = 0x08
            data = self._bus.read_i2c_block_data(self._address, REG_RISK, 2)
            risk_level = (data[0] << 8) | data[1]
            
            # 检查风险等级范围
            if risk_level > 4:  # 风险等级是0-4
                risk_level = min(4, max(0, risk_level % 5))
            
            return risk_level
        except Exception:
            return 0

# 主程序开始 ================================================

print("====== 紫外线传感器测试程序 (内嵌版) ======")

# 创建传感器对象
print("[初始化] 创建紫外线传感器对象...")
sensor = PatchUVSensor(debug_mode=True)

# 初始化传感器
print("[初始化] 开始自动扫描传感器...")
if sensor.begin():
    print("[初始化] ✅ 初始化成功")
    
    # 等待传感器稳定
    print("[初始化] 等待传感器稳定(3秒)...")
    time.sleep(3)
    
    # 主循环
    print("[运行] 开始读取传感器数据")
    try:
        while True:
            # 读取数据
            uv_data = sensor.read_UV_original_data()
            uv_index = sensor.read_UV_index_data()
            risk_level = sensor.read_risk_level_data()
            
            # 风险等级名称
            risk_texts = ["低风险", "中风险", "高风险", "很高风险", "极高风险"]
            risk_name = risk_texts[risk_level] if 0 <= risk_level < len(risk_texts) else "未知"
            
            # 输出数据
            print("\n----- 紫外线数据 -----")
            print(f"原始值: {uv_data} mV")
            print(f"UV指数: {uv_index}")
            print(f"风险等级: {risk_level} ({risk_name})")
            
            # 根据UV指数提供建议
            if uv_index <= 2:
                advice = "安全，无需特别防护"
            elif uv_index <= 5:
                advice = "中等风险，建议涂抹防晒霜"
            elif uv_index <= 7:
                advice = "高风险，建议使用防晒霜并穿戴防护服"
            elif uv_index <= 10:
                advice = "很高风险，尽量避免外出"
            else:
                advice = "极高风险，避免外出，必须全面防护"
            
            print(f"防护建议: {advice}")
            
            # 等待2秒再次读取
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[程序] 程序已手动停止")
    except Exception as e:
        print(f"\n[程序] 发生错误: {e}")
else:
    print("[初始化] ❌ 初始化失败")
