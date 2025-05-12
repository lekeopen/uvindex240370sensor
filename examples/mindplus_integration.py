#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
紫外线传感器 Mind+ 集成版本
为行空板(Unihiker)优化的紫外线传感器驱动
集成了smbus库与错误处理机制
'''

import time
import sys
import os
import random

# 定义紫外线传感器类 (完全内嵌，不依赖外部库)
class UVSensor:
    """行空板紫外线传感器类，内嵌于主程序，不依赖外部库"""
    def __init__(self):
        self._simulation_mode = False  # 模拟模式标志
        self._bus = None               # SMBus对象
        self._bus_num = None           # 总线号
        self._address = None           # 设备地址
        self._device_id = None         # 设备ID
        self._is_connected = False     # 连接状态
        self._last_raw_value = 0       # 上次读取的原始值
        
        # 初始化传感器
        self._initialize()
    
    def _initialize(self):
        """初始化传感器，自动扫描I2C总线"""
        print("[UV传感器] 初始化中...")
        
        # 导入smbus库
        try:
            import smbus
            print("[UV传感器] SMBus库导入成功")
        except ImportError:
            print("[UV传感器] 无法导入SMBus库，启用模拟模式")
            self._simulation_mode = True
            self._is_connected = True
            return
        
        # 常量定义
        DEVICE_ADDR = 0x23      # 主要地址
        DEVICE_ADDR_ALT = 0x38  # 备用地址
        REG_PID = 0x00          # 设备ID寄存器
        DEVICE_PID = 0x427c     # 标准设备ID
        DEVICE_PID_REVERSED = 0x7c42  # 字节序颠倒的设备ID
        
        print("[UV传感器] 开始扫描I2C总线...")
        
        # 优先尝试总线4，因为之前的诊断确认传感器在这个总线上
        bus_list = [4, 1, 0, 2, 3, 5, 6, 7]
        addr_list = [DEVICE_ADDR, DEVICE_ADDR_ALT]
        
        # 尝试所有总线
        for bus_num in bus_list:
            print(f"[UV传感器] 尝试总线 {bus_num}...")
            try:
                bus = smbus.SMBus(bus_num)
                
                # 尝试所有地址
                for addr in addr_list:
                    try:
                        # 尝试读取设备ID
                        data = bus.read_i2c_block_data(addr, REG_PID, 2)
                        device_id = (data[0] << 8) | data[1]
                        print(f"[UV传感器] 总线{bus_num}地址0x{addr:02X}的设备ID: 0x{device_id:04X}")
                        
                        # 验证设备ID (包括字节序颠倒的情况)
                        if device_id == DEVICE_PID or device_id == DEVICE_PID_REVERSED:
                            print(f"[UV传感器] ✓ 总线{bus_num}上找到紫外线传感器(地址0x{addr:02X})")
                            self._bus = bus
                            self._bus_num = bus_num
                            self._address = addr
                            self._device_id = device_id
                            self._is_connected = True
                            print(f"🌞 紫外线传感器连接成功!")
                            print(f"总线: {bus_num}, 地址: 0x{addr:02X}")
                            
                            # 等待传感器稳定
                            print("[UV传感器] 等待传感器稳定 (2秒)...")
                            time.sleep(2)
                            return
                    except Exception as e:
                        pass
                
                # 如果没找到，关闭总线
                bus.close()
            except Exception:
                pass
        
        # 如果所有尝试都失败，启用模拟模式
        print("[UV传感器] 无法找到传感器，启用模拟模式")
        print("✗ 未能找到紫外线传感器")
        print("  - 请确认传感器已正确连接")
        print("  - 检查I2C连接线是否牢固")
        print("  - 确认传感器电源正常")
        print("  - 可能需要重启行空板")
        self._simulation_mode = True
        self._is_connected = True
    
    def read_UV_original_data(self):
        """读取紫外线原始数据"""
        # 模拟模式
        if self._simulation_mode:
            # 生成模拟数据
            self._last_raw_value = max(0, min(20000, self._last_raw_value + random.randint(-500, 500)))
            if self._last_raw_value < 100:  # 保持一些最小值
                self._last_raw_value = random.randint(100, 300)
            return self._last_raw_value
        
        # 真实模式 - 读取传感器数据
        if not self._is_connected:
            print("错误: 未连接传感器，无法读取原始数据")
            return 0
            
        try:
            REG_DATA = 0x06  # 原始数据寄存器
            data = self._bus.read_i2c_block_data(self._address, REG_DATA, 2)
            raw_value = (data[0] << 8) | data[1]
            
            # 数据修正 (处理可能的异常值)
            if raw_value > 30000:  # 极端异常值，可能是字节序问题
                raw_value = ((raw_value & 0xFF) << 8) | ((raw_value >> 8) & 0xFF)
            
            # 更新最后读取的值
            self._last_raw_value = raw_value
            return raw_value
        except Exception as e:
            print(f"错误: 读取UV原始数据失败: {e}")
            return 0
    
    def read_UV_index_data(self):
        """读取UV指数数据"""
        # 模拟模式
        if self._simulation_mode:
            raw = self.read_UV_original_data()
            return min(11, max(0, int(raw / 1800)))
        
        # 真实模式
        if not self._is_connected:
            print("错误: 未连接传感器，无法读取UV指数")
            return 0
            
        try:
            REG_INDEX = 0x07  # UV指数寄存器
            data = self._bus.read_i2c_block_data(self._address, REG_INDEX, 2)
            uv_index = (data[0] << 8) | data[1]
            
            # 数据验证 (UV指数通常在0-11范围内)
            if uv_index > 20:
                uv_index = min(11, max(0, int(self._last_raw_value / 1800)))
            
            return uv_index
        except Exception:
            return 0
    
    def read_risk_level_data(self):
        """读取风险等级数据"""
        # 模拟模式
        if self._simulation_mode:
            uv_index = self.read_UV_index_data()
            # 将UV指数转换为风险等级
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
        
        # 真实模式
        if not self._is_connected:
            print("错误: 未连接传感器，无法读取风险等级")
            return 0
            
        try:
            REG_RISK = 0x08  # 风险等级寄存器
            data = self._bus.read_i2c_block_data(self._address, REG_RISK, 2)
            risk_level = (data[0] << 8) | data[1]
            
            # 数据验证 (风险等级是0-4)
            if risk_level > 4:
                # 如果数据异常，基于UV指数计算
                uv_index = self.read_UV_index_data()
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
        except Exception:
            return 0

# 创建紫外线传感器对象
uv_sensor = UVSensor()

# 主循环
try:
    print("===== 紫外线传感器监测程序 =====")
    print("实时监测环境中的紫外线指数")
    print("按Ctrl+C停止程序")
    print("-------------------------------")
    
    # 风险等级对应的文本描述
    risk_texts = ["低风险", "中等风险", "高风险", "很高风险", "极高风险"]
    
    while True:
        # 读取传感器数据
        uv_raw = uv_sensor.read_UV_original_data()
        uv_index = uv_sensor.read_UV_index_data()
        risk_level = uv_sensor.read_risk_level_data()
        
        # 获取风险描述
        risk_text = risk_texts[risk_level] if 0 <= risk_level < len(risk_texts) else "未知"
        
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
        
        # 显示数据
        print("\n----- 紫外线数据 -----")
        print(f"原始值: {uv_raw} mV")
        print(f"UV指数: {uv_index}")
        print(f"风险等级: {risk_level} ({risk_text})")
        print(f"防护建议: {advice}")
        
        # 等待2秒再次读取
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\n程序已停止")
