#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
UV传感器库简单验证脚本 - 行空板PinPong版
'''

import os
import sys

# 添加库路径
library_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python/libraries")
if os.path.exists(library_path):
    sys.path.append(library_path)
    print("库路径:", library_path)

try:
    # 导入修复后的库
    print("尝试导入库...")
    from unihiker_uv_patch_v3 import PatchUVSensor
    print("库导入成功!")
    
    # 尝试创建对象
    print("尝试创建传感器对象...")
    sensor = PatchUVSensor(simulation_mode=True)  # 使用模拟模式，确保即使没有硬件也能工作
    print("传感器对象创建成功!")
    
    # 尝试初始化
    print("尝试初始化...")
    if sensor.begin():
        print("初始化成功!")
    else:
        print("初始化失败!")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
