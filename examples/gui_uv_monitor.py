#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
紫外线传感器GUI示例 - 行空板优化版
使用unihiker的LCD显示屏展示紫外线数据
'''

import time
import sys
import os

try:
    # 尝试导入unihiker库
    from unihiker import GUI
except ImportError:
    print("未找到unihiker库，这个示例需要在行空板上运行")
    sys.exit(1)

try:
    # 导入优化版紫外线传感器库
    from unihiker_uv_patch_v2 import PatchUVSensor
    
    # 创建GUI对象
    gui = GUI()
    gui.clear()
    
    # 创建传感器对象
    uv_sensor = PatchUVSensor(debug_mode=False)
    
    # 初始化传感器
    gui.draw_text(0, 0, "紫外线传感器初始化中...", 18)
    gui.display()
    
    if uv_sensor.begin():
        gui.clear()
        gui.draw_text(0, 0, "紫外线指数监测", 20, 0x00BFFF)
        gui.draw_line(0, 25, 240, 25, 0xAAAAAA)
        gui.display()
        
        # 定义风险等级颜色
        risk_colors = [0x00FF00, 0xFFFF00, 0xFFA500, 0xFF0000, 0x8B0000]
        risk_names = ["低风险", "中等风险", "高风险", "很高风险", "极高风险"]
        
        # 循环读取数据
        while True:
            # 清除数据区域
            gui.draw_rect(0, 30, 240, 210, 0x000000, True)
            
            # 读取数据
            raw_value = uv_sensor.read_UV_original_data()
            uv_index = uv_sensor.read_UV_index_data()
            risk_level = uv_sensor.read_risk_level_data()
            
            # 显示数据
            gui.draw_text(10, 40, f"原始值: {raw_value}", 16)
            gui.draw_text(10, 70, f"UV指数: {uv_index}", 24, 0x00BFFF)
            
            # 风险等级文本和颜色
            if 0 <= risk_level < len(risk_colors):
                risk_color = risk_colors[risk_level]
                risk_name = risk_names[risk_level]
            else:
                risk_color = 0xFFFFFF
                risk_name = "未知风险"
            
            gui.draw_text(10, 110, f"风险等级: {risk_name}", 18, risk_color)
            
            # 画UV指数条形图
            bar_width = min(20 * uv_index, 200)  # 最大宽度200
            gui.draw_rect(10, 150, 200, 20, 0x444444, True)
            if bar_width > 0:
                gui.draw_rect(10, 150, bar_width, 20, risk_color, True)
            
            # 防护建议
            if risk_level <= 1:
                advice = "无需特别防护"
            elif risk_level == 2:
                advice = "建议涂防晒霜,戴帽子"
            elif risk_level == 3:
                advice = "避免长时间户外活动"
            else:
                advice = "请待在室内,避免外出"
            
            gui.draw_text(10, 180, f"建议: {advice}", 16, 0xFFFFFF)
            
            # 更新显示
            gui.display()
            time.sleep(1)
            
    else:
        gui.clear()
        gui.draw_text(0, 40, "紫外线传感器初始化失败", 18, 0xFF0000)
        gui.draw_text(0, 70, "请检查连接", 16)
        gui.display()
        time.sleep(5)
    
except Exception as e:
    # 错误处理
    if 'gui' in locals():
        gui.clear()
        gui.draw_text(0, 40, f"错误: {str(e)}", 16, 0xFF0000)
        gui.display()
    else:
        print(f"错误: {e}")
    time.sleep(5)
