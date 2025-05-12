#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
紫外线传感器测试程序 - 行空板PinPong专用版V3测试
'''

import time
import sys
import os

print("==== 行空板紫外线传感器V3库测试 ====")
print("测试时间:", time.strftime("%Y-%m-%d %H:%M:%S"))

# 添加库路径
library_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python/libraries")
if os.path.exists(library_path):
    sys.path.append(library_path)
    print("添加库路径:", library_path)

# 尝试导入UV传感器库
try:
    from unihiker_uv_patch_v3 import PatchUVSensor
    print("✓ UV传感器库导入成功")
    
    # 创建传感器对象
    print("\n初始化传感器...")
    sensor = PatchUVSensor(debug_mode=True)
    
    # 初始化传感器
    if sensor.begin():
        print("✓ 传感器初始化成功")
        
        try:
            print("\n开始读取数据 (按Ctrl+C停止)...\n")
            count = 1
            while True:
                print(f"--- 第 {count} 次读取 ---")
                
                # 读取原始数据
                raw_value = sensor.read_UV_original_data()
                print(f"原始值: {raw_value}")
                
                # 读取UV指数
                uv_index = sensor.read_UV_index_data()
                print(f"UV指数: {uv_index}")
                
                # 读取风险等级
                risk_level = sensor.read_risk_level_data()
                risk_names = ["", "低", "中等", "高", "很高", "极高"]
                risk_name = risk_names[risk_level] if 1 <= risk_level <= 5 else "未知"
                print(f"风险等级: {risk_level} ({risk_name})")
                
                print("")
                count += 1
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n用户停止测试")
        except Exception as e:
            print(f"\n测试出错: {e}")
    else:
        print("✗ 传感器初始化失败")
        
except ImportError as e:
    print(f"✗ UV传感器库导入失败: {e}")
    print("请确认 unihiker_uv_patch_v3.py 文件已放在正确位置")
except Exception as e:
    print(f"✗ 测试出错: {e}")

print("\n==== 测试结束 ====")
