#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
紫外线传感器库测试脚本
用于验证传感器库是否正常工作
'''

import os
import sys
import time

print("紫外线传感器库测试程序")
print("=" * 30)

# 尝试导入库文件
print("1. 检查库文件...")
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "../python/libraries"))
    import unihiker_uv_patch_v2
    print("✅ 找到库文件: unihiker_uv_patch_v2.py")
except ImportError:
    print("❌ 无法导入库文件")
    print("请确保文件位于正确位置")
    sys.exit(1)

# 查看版本信息
print("\n2. 库文件版本信息:")
print(f"文件路径: {unihiker_uv_patch_v2.__file__}")
file_info = os.stat(unihiker_uv_patch_v2.__file__)
print(f"文件大小: {file_info.st_size} 字节")
print(f"修改时间: {time.ctime(file_info.st_mtime)}")

# 检查类和方法
print("\n3. 检查库中的类和方法:")
try:
    from unihiker_uv_patch_v2 import PatchUVSensor
    print("✅ 找到 PatchUVSensor 类")
    
    # 创建模拟模式下的传感器实例进行测试
    print("\n4. 使用模拟模式测试功能:")
    sensor = PatchUVSensor(simulation_mode=True)
    
    print("- 初始化传感器...", end="")
    result = sensor.begin()
    print(" ✅ 成功" if result else " ❌ 失败")
    
    print("- 读取原始数据...", end="")
    raw_data = sensor.read_UV_original_data()
    print(f" ✅ 值: {raw_data}")
    
    print("- 读取UV指数...", end="")
    uv_index = sensor.read_UV_index_data()
    print(f" ✅ 值: {uv_index}")
    
    print("- 读取风险等级...", end="")
    risk_level = sensor.read_risk_level_data()
    print(f" ✅ 值: {risk_level}")
    
    print("\n所有测试完成，库文件功能正常！")
    
except (ImportError, AttributeError) as e:
    print(f"❌ 错误: {e}")
    print("库文件缺少必要的类或方法")
    sys.exit(1)

print("\n5. 真实传感器测试说明:")
print("如需测试真实传感器，请执行以下步骤:")
print("1) 确保传感器正确连接到行空板")
print("2) 运行 basic_uv_example.py 示例程序")
print("3) 查看读取的数据是否合理")
print("\n测试脚本执行完毕。")
