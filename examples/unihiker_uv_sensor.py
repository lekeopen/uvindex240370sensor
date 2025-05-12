#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
行空板(UniHiker)紫外线传感器简化库
不依赖外部库，整合在单个文件中，便于直接使用
'''

import time
import random
import os
import sys

class UniUVSensor:
    """行空板紫外线传感器简化版类"""
    
    def __init__(self, debug_mode=False, simulation_mode=False):
        """初始化传感器
        
        Args:
            debug_mode (bool): 是否启用调试输出
            simulation_mode (bool): 是否使用模拟模式
        """
        self._debug_mode = debug_mode
        self._simulation_mode = simulation_mode
        self._bus = None
        self._bus_num = None
        self._address = None
        self._device_id = None
        self._is_connected = False
        self._last_raw_value = random.randint(100, 300)
        
        if self._debug_mode:
            print("[UV传感器] 初始化中...")
    
    def begin(self):
        """初始化传感器
        
        Returns:
            bool: 是否成功初始化
        """
        if self._simulation_mode:
            self._is_connected = True
            if self._debug_mode:
                print("[UV传感器] 模拟模式已激活")
            return True
        
        return self._scan_i2c_buses()
    
    def _scan_i2c_buses(self):
        """扫描可用的I2C总线和设备
        
        Returns:
            bool: 是否找到传感器
        """
        if self._debug_mode:
            print("[UV传感器] 扫描I2C总线...")
        
        # 导入smbus库
        try:
            import smbus
        except ImportError:
            if self._debug_mode:
                print("[UV传感器] 无法导入smbus库，切换到模拟模式")
            self._simulation_mode = True
            self._is_connected = True
            return True
        
        # 常量定义
        DEVICE_ADDR = 0x23      # 行空板上的默认地址
        DEVICE_ADDR_ALT = 0x38  # 标准地址
        REG_PID = 0x00          # PID寄存器地址
        DEVICE_PID = 0x427c     # 原始设备ID
        DEVICE_PID_REVERSED = 0x7c42  # 字节序颠倒的设备ID
        
        # 尝试常用的总线，以总线4为优先
        bus_list = [4, 1, 0, 2, 3, 5, 6, 7]
        addr_list = [DEVICE_ADDR, DEVICE_ADDR_ALT]
        
        # 扫描所有总线和地址组合
        for bus_num in bus_list:
            if self._debug_mode:
                print(f"[UV传感器] 尝试总线 {bus_num}...")
            try:
                bus = smbus.SMBus(bus_num)
                
                for addr in addr_list:
                    try:
                        # 读取设备ID
                        data = bus.read_i2c_block_data(addr, REG_PID, 2)
                        device_id = (data[0] << 8) | data[1]
                        
                        if self._debug_mode:
                            print(f"[UV传感器] 总线{bus_num}地址0x{addr:02X}的设备ID: 0x{device_id:04X}")
                        
                        # 验证设备ID，同时支持原始ID和字节序颠倒的ID
                        if device_id == DEVICE_PID or device_id == DEVICE_PID_REVERSED:
                            if self._debug_mode:
                                print(f"[UV传感器] ✓ 在总线{bus_num}地址0x{addr:02X}找到传感器")
                            
                            self._bus = bus
                            self._bus_num = bus_num
                            self._address = addr
                            self._device_id = device_id
                            self._is_connected = True
                            return True
                    except Exception as e:
                        if self._debug_mode:
                            print(f"[UV传感器] 总线{bus_num}地址0x{addr:02X}尝试失败: {e}")
                
                bus.close()
            except Exception as e:
                if self._debug_mode:
                    print(f"[UV传感器] 总线{bus_num}打开失败: {e}")
        
        # 如果未找到设备，启用模拟模式
        if self._debug_mode:
            print("[UV传感器] ✗ 未找到传感器")
        
        self._simulation_mode = True
        return False
    
    def read_raw(self):
        """读取原始数据
        
        Returns:
            int: 原始数据值
        """
        if self._simulation_mode:
            # 模拟数据
            self._last_raw_value = max(100, min(20000, 
                                    self._last_raw_value + random.randint(-500, 500)))
            return self._last_raw_value
        
        if not self._is_connected:
            return 0
        
        try:
            data = self._bus.read_i2c_block_data(self._address, 0x06, 2)
            raw_value = (data[0] << 8) | data[1]
            return raw_value
        except Exception as e:
            if self._debug_mode:
                print(f"[UV传感器] 读取原始数据失败: {e}")
            return 0
    
    def read_uv_index(self):
        """读取UV指数
        
        Returns:
            int: UV指数(0-11)
        """
        if self._simulation_mode:
            raw = self.read_raw()
            return min(11, max(0, int(raw / 1800)))
        
        if not self._is_connected:
            return 0
        
        try:
            data = self._bus.read_i2c_block_data(self._address, 0x07, 2)
            uv_index = (data[0] << 8) | data[1]
            
            # 数据验证: 如果值为0或异常大，则从原始值计算
            if uv_index == 0 or uv_index > 20:
                raw_value = self.read_raw()
                uv_index = min(11, max(0, int(raw_value / 1800)))
            
            return uv_index
        except Exception as e:
            if self._debug_mode:
                print(f"[UV传感器] 读取UV指数失败: {e}")
            return 0
    
    def read_risk_level(self):
        """读取风险等级
        
        Returns:
            int: 风险等级(0-4)
            0: 低风险
            1: 中等风险
            2: 高风险
            3: 很高风险
            4: 极高风险
        """
        if self._simulation_mode:
            uv_index = self.read_uv_index()
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
        
        if not self._is_connected:
            return 0
        
        try:
            data = self._bus.read_i2c_block_data(self._address, 0x08, 2)
            risk_level = (data[0] << 8) | data[1]
            
            # 数据验证: 如果值异常，则从UV指数计算
            if risk_level > 4:
                uv_index = self.read_uv_index()
                if uv_index <= 2:
                    risk_level = 0
                elif uv_index <= 5:
                    risk_level = 1
                elif uv_index <= 7:
                    risk_level = 2
                elif uv_index <= 10:
                    risk_level = 3
                else:
                    risk_level = 4
            
            return risk_level
        except Exception as e:
            if self._debug_mode:
                print(f"[UV传感器] 读取风险等级失败: {e}")
            return 0

if __name__ == "__main__":
    # 简单测试程序
    print("行空板紫外线传感器测试")
    print("="*40)
    
    # 创建传感器对象并尝试初始化
    sensor = UniUVSensor(debug_mode=True)
    
    if sensor.begin():
        print("传感器初始化成功!")
        
        # 读取并显示数据
        for i in range(5):
            raw = sensor.read_raw()
            uv = sensor.read_uv_index()
            risk = sensor.read_risk_level()
            
            risk_names = ["低", "中等", "高", "很高", "极高"]
            risk_name = risk_names[risk] if 0 <= risk < len(risk_names) else "未知"
            
            print(f"原始值: {raw}, UV指数: {uv}, 风险等级: {risk} ({risk_name})")
            time.sleep(1)
    else:
        print("传感器初始化失败，使用模拟模式")
        # 使用模拟模式读取数据
        for i in range(3):
            raw = sensor.read_raw()
            uv = sensor.read_uv_index()
            risk = sensor.read_risk_level()
            print(f"[模拟] 原始值: {raw}, UV指数: {uv}, 风险等级: {risk}")
            time.sleep(1)
