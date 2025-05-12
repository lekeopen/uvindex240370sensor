#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
紫外线传感器基础示例 - 行空板优化版
'''

import time
import sys
import os

try:
    # 尝试添加可能的库路径
    paths = [
        "/usr/lib/python3/dist-packages",
        "/usr/local/lib/python3/dist-packages",
        os.path.expanduser("~/.local/lib/python3/dist-packages"),
        "/usr/share/unihiker/lib",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python/libraries")
    ]
    
    # 添加路径
    for path in paths:
        if path not in sys.path and os.path.exists(path):
            sys.path.append(path)
            print("添加库搜索路径:", path)
            
    # 导入优化版紫外线传感器库 - v3版本
    from unihiker_uv_patch_v3 import PatchUVSensor
    
    # 创建传感器对象 - 调试模式下会输出更多信息
    uv_sensor = PatchUVSensor(debug_mode=True)
    
    # 初始化传感器 - 会自动扫描适合的I2C总线和地址
    if uv_sensor.begin():
        print("✅ 传感器初始化成功")
        
        # 循环读取数据
        while True:
            # 读取紫外线原始数据
            raw_value = uv_sensor.read_UV_original_data()
            print(f"原始数据: {raw_value}")
            
            # 读取UV指数
            uv_index = uv_sensor.read_UV_index_data()
            print(f"UV指数: {uv_index}")
            
            # 读取风险等级
            risk_level = uv_sensor.read_risk_level_data()
            risk_names = ["低", "中等", "高", "很高", "极高"]
            risk_name = risk_names[risk_level] if 0 <= risk_level < len(risk_names) else "未知"
            print(f"风险等级: {risk_level} ({risk_name})")
            
            print("-" * 30)
            time.sleep(1)  # 每秒读取一次
            
    else:
        print("❌ 传感器初始化失败")
    
except Exception as e:
    print(f"程序出错: {e}")
