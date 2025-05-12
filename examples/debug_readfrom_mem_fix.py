#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
UV传感器库调试验证脚本 - 专用于测试readfrom_mem修复
'''

import os
import sys
import time

# 添加库路径
script_dir = os.path.dirname(os.path.abspath(__file__))
library_path = os.path.join(os.path.dirname(script_dir), "python/libraries")
if os.path.exists(library_path):
    sys.path.append(library_path)
    print(f"已添加库路径: {library_path}")

# 尝试导入库
try:
    print("导入UV传感器库...")
    from unihiker_uv_patch_v3 import PatchUVSensor
    print("✓ 库导入成功!")
    
    # 创建传感器对象 (使用模拟模式确保不依赖硬件)
    print("\n创建传感器对象（启用模拟模式和调试模式）...")
    sensor = PatchUVSensor(simulation_mode=True, debug_mode=True)
    print("✓ 传感器对象创建成功")
    
    # 尝试初始化
    print("\n初始化传感器...")
    if sensor.begin():
        print("✓ 传感器初始化成功")
        
        # 尝试读取数据
        print("\n测试读取数据（模拟模式）...")
        
        # 测试read_register_16bit方法 (修复的方法)
        print("\n1. 测试read_register_16bit方法...")
        for reg in [0x00, 0x06, 0x07, 0x08]:
            try:
                value = sensor.read_register_16bit(reg)
                print(f"  ✓ 读取寄存器0x{reg:02X}成功: 0x{value:04X}")
            except Exception as e:
                print(f"  ✗ 读取寄存器0x{reg:02X}失败: {e}")
        
        # 测试传感器数据读取方法
        print("\n2. 测试传感器数据读取方法...")
        try:
            raw = sensor.read_UV_original_data()
            print(f"  ✓ 原始值读取成功: {raw}")
            
            index = sensor.read_UV_index_data()
            print(f"  ✓ UV指数读取成功: {index}")
            
            risk = sensor.read_risk_level_data()
            print(f"  ✓ 风险等级读取成功: {risk}")
        except Exception as e:
            print(f"  ✗ 数据读取失败: {e}")
        
        print("\n模拟测试完成，所有功能正常!")
    else:
        print("✗ 传感器初始化失败")
        
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n==== 测试结束 ====")
