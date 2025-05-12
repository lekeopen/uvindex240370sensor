#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
UV传感器库修复验证脚本 - 在任何环境下测试
'''

import os
import sys
import time

# 添加库路径
script_dir = os.path.dirname(os.path.abspath(__file__))
library_path = os.path.join(os.path.dirname(script_dir), "python/libraries")
if os.path.exists(library_path):
    if library_path not in sys.path:
        sys.path.append(library_path)
        print(f"已添加库路径: {library_path}")

# 定义简化版PinPong库模拟类
class MockPinPong:
    class Board:
        def __init__(self, board_type="unihiker"):
            self.board_type = board_type
            print(f"创建模拟Board({board_type})")
            
        def begin(self):
            print("模拟Board.begin()")
            return True
            
        def get_i2c(self, bus_num):
            return MockPinPong.I2C(bus_num)
    
    class I2C:
        def __init__(self, bus=1):
            self.bus = bus
            print(f"创建模拟I2C(bus={bus})")
            
        def readfrom_mem(self, addr, reg, length):
            print(f"模拟readfrom_mem(addr=0x{addr:02X}, reg=0x{reg:02X}, length={length})")
            # 返回模拟数据
            if reg == 0x00:  # 设备ID
                return bytearray([0x7C, 0x42])  # 返回0x7C42
            elif reg == 0x06:  # 原始值
                return bytearray([0x01, 0x2C])  # 返回300
            elif reg == 0x07:  # UV指数
                return bytearray([0x00, 0x03])  # 返回3
            elif reg == 0x08:  # 风险等级
                return bytearray([0x00, 0x02])  # 返回2
            return bytearray([0x00, 0x00])

# 替换PinPong导入
try:
    from pinpong.board import I2C, Board
    print("使用实际的PinPong库")
except ImportError:
    print("PinPong库不可用，使用模拟类")
    sys.modules['pinpong'] = MockPinPong
    sys.modules['pinpong.board'] = MockPinPong
    from pinpong.board import I2C, Board

# 清除unihiker_uv_patch_v3模块缓存(如果存在)
if 'unihiker_uv_patch_v3' in sys.modules:
    del sys.modules['unihiker_uv_patch_v3']

# 现在导入我们的UV传感器库
try:
    print("\n导入UV传感器库...")
    from unihiker_uv_patch_v3 import PatchUVSensor, PINPONG_AVAILABLE
    print(f"✓ 库导入成功! PinPong可用: {PINPONG_AVAILABLE}")
    
    # 创建传感器对象
    print("\n创建传感器对象（调试模式）...")
    sensor = PatchUVSensor(debug_mode=True)
    print("✓ 传感器对象创建成功")
    
    # 尝试初始化
    print("\n初始化传感器...")
    if sensor.begin():
        print("✓ 传感器初始化成功")
        
        # 测试读取数据
        print("\n测试读取数据...")
        
        # 测试传感器数据读取方法
        print("\n读取传感器数据:")
        try:
            raw = sensor.read_UV_original_data()
            print(f"✓ 原始值: {raw}")
            
            index = sensor.read_UV_index_data()
            print(f"✓ UV指数: {index}")
            
            risk = sensor.read_risk_level_data()
            print(f"✓ 风险等级: {risk}")
            
            # 完整测试
            print("\n连续读取测试 (3次):")
            for i in range(3):
                print(f"\n第{i+1}次读取:")
                raw = sensor.read_UV_original_data()
                index = sensor.read_UV_index_data()
                risk = sensor.read_risk_level_data()
                print(f"原始值: {raw}, UV指数: {index}, 风险等级: {risk}")
                time.sleep(0.5)
                
        except Exception as e:
            print(f"✗ 数据读取失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ 传感器初始化失败")
        
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n==== 测试结束 ====")
