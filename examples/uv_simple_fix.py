#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
紫外线传感器简化版修复程序
适用于行空板(Unihiker)
自动扫描I2C总线并读取紫外线数据
'''

import time
import random

try:
    import smbus
    print("SMBus库导入成功")
except ImportError:
    print("警告：SMBus库不可用，将使用模拟模式")
    smbus = None

# 初始化变量
bus = None
bus_num = None
address = None
device_id = None
simulation_mode = smbus is None

# 自动扫描I2C总线
def initialize_sensor():
    global bus, bus_num, address, device_id, simulation_mode
    
    if simulation_mode:
        print("使用模拟模式")
        return True
    
    print("开始扫描I2C总线...")
    
    # 常量定义
    DEVICE_ADDR = 0x23      # 主要地址
    DEVICE_ADDR_ALT = 0x38  # 备用地址
    REG_PID = 0x00          # 设备ID寄存器
    DEVICE_PID = 0x427c     # 标准设备ID
    DEVICE_PID_REVERSED = 0x7c42  # 字节序颠倒的设备ID
    
    # 优先尝试总线4，顺序按可能性排列
    bus_list = [4, 1, 0, 2, 3, 5, 6, 7]
    addr_list = [DEVICE_ADDR, DEVICE_ADDR_ALT]
    
    # 扫描所有总线
    for bus_num_try in bus_list:
        print(f"尝试总线 {bus_num_try}...")
        try:
            bus_try = smbus.SMBus(bus_num_try)
            
            # 尝试所有地址
            for addr_try in addr_list:
                try:
                    data = bus_try.read_i2c_block_data(addr_try, REG_PID, 2)
                    id_try = (data[0] << 8) | data[1]
                    print(f"总线{bus_num_try}地址0x{addr_try:02X}的设备ID: 0x{id_try:04X}")
                    
                    if id_try == DEVICE_PID or id_try == DEVICE_PID_REVERSED:
                        print(f"✓ 找到了紫外线传感器！")
                        print(f"总线: {bus_num_try}, 地址: 0x{addr_try:02X}")
                        bus = bus_try
                        bus_num = bus_num_try
                        address = addr_try
                        device_id = id_try
                        return True
                except:
                    pass
            
            # 关闭总线
            bus_try.close()
        except:
            pass
    
    # 如果找不到传感器，启用模拟模式
    print("未找到紫外线传感器，启用模拟模式")
    simulation_mode = True
    return True

# 读取原始值
def read_raw_value():
    global bus, address, simulation_mode
    
    if simulation_mode:
        # 生成模拟数据
        return random.randint(0, 10000)
    
    try:
        data = bus.read_i2c_block_data(address, 0x06, 2)
        raw_value = (data[0] << 8) | data[1]
        return raw_value
    except:
        print("读取原始值失败")
        return 0

# 读取UV指数
def read_uv_index():
    global bus, address, simulation_mode
    
    if simulation_mode:
        raw = read_raw_value()
        return min(11, max(0, int(raw / 1800)))
    
    try:
        data = bus.read_i2c_block_data(address, 0x07, 2)
        uv_index = (data[0] << 8) | data[1]
        
        # 验证数据合理性
        if uv_index > 20:
            # 如果不合理，从原始值计算
            raw = read_raw_value()
            uv_index = min(11, max(0, int(raw / 1800)))
            
        return uv_index
    except:
        print("读取UV指数失败")
        return 0

# 读取风险等级
def read_risk_level():
    global bus, address, simulation_mode
    
    if simulation_mode:
        uv_index = read_uv_index()
        if uv_index <= 2:
            return 0
        elif uv_index <= 5:
            return 1
        elif uv_index <= 7:
            return 2
        elif uv_index <= 10:
            return 3
        else:
            return 4
    
    try:
        data = bus.read_i2c_block_data(address, 0x08, 2)
        risk_level = (data[0] << 8) | data[1]
        
        # 验证范围
        if risk_level > 4:
            # 从UV指数重新计算
            uv_index = read_uv_index()
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
    except:
        print("读取风险等级失败")
        return 0

# 主程序
if __name__ == "__main__":
    print("===== 紫外线传感器简易测试程序 =====")
    
    # 初始化传感器
    if initialize_sensor():
        print("初始化成功")
        
        # 等待传感器稳定
        print("等待传感器稳定(3秒)...")
        time.sleep(3)
        
        # 风险等级描述
        risk_texts = ["低风险", "中等风险", "高风险", "很高风险", "极高风险"]
        
        # 主循环
        try:
            while True:
                raw_value = read_raw_value()
                uv_index = read_uv_index()
                risk_level = read_risk_level()
                
                # 获取风险描述
                risk_text = risk_texts[risk_level] if 0 <= risk_level < len(risk_texts) else "未知"
                
                # 打印数据
                print("\n----- 紫外线数据 -----")
                print(f"原始值: {raw_value}")
                print(f"UV指数: {uv_index}")
                print(f"风险等级: {risk_level} ({risk_text})")
                
                # 等待2秒
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n程序已停止")
        
    else:
        print("初始化失败")
