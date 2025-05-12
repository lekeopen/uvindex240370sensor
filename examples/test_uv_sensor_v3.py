#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行空板紫外线指数传感器测试程序

这个脚本用于测试修复后的紫外线传感器库能否正常工作。
支持真实传感器和模拟模式。
"""

import time
import sys

try:
    from unihiker_uv_patch_v3 import PatchUVSensor
    print("成功导入修复后的紫外线传感器库")
except ImportError:
    print("错误: 无法导入修复后的库，请先安装库文件")
    print("可以使用 ./deploy_to_unihiker.sh 脚本将库部署到行空板")
    sys.exit(1)

def main():
    print("=== 行空板紫外线传感器测试程序 ===")
    
    # 创建一个传感器实例，如果未连接传感器，使用模拟模式
    try:
        sensor = PatchUVSensor()
        result = sensor.begin()
        
        if result:
            print("✓ 传感器初始化成功!")
            device_id = sensor.read_device_id()
            print(f"  设备ID: 0x{device_id:04X}")
            
            if device_id in [0x427C, 0x7C42]:
                print("✓ 设备ID验证成功")
            else:
                print("⚠ 设备ID不匹配，但将继续测试")
        else:
            print("⚠ 传感器初始化失败，将使用模拟模式")
    except Exception as e:
        print(f"⚠ 错误: {e}")
        print("将启用模拟模式以演示功能")
        sensor = PatchUVSensor(simulation_mode=True)
        sensor.begin()
    
    print("\n开始数据读取测试:")
    
    # 连续读取10次数据
    for i in range(10):
        try:
            raw_data = sensor.read_UV_original_data()
            uv_index = sensor.read_UV_index_data()
            risk_level = sensor.read_risk_level_data()
            
            print(f"[{i+1}] 原始值: {raw_data}, UV指数: {uv_index}, 风险等级: {risk_level}")
            time.sleep(1)
        except Exception as e:
            print(f"读取数据失败: {e}")
            break
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
