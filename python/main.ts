//% color="#00BCD4" icon="\uf185" block="紫外线传感器"
//% version="1.1.0"

enum UVDataType {
    原始数据,
    UV指数,
    风险等级
}


declare interface Generator {
    addImport(code: string): void;
    addCode(code: string): void;
    addObject(key: string, value: string): void;
}
declare const Generator: Generator;

namespace pythonUVIndex240370Sensor {
    //% block="初始化紫外线传感器" 
    //% weight=100
    //% blockId=initSensor
    //% blockType="command"
    export function initSensor(): void {
        Generator.addImport(`import time
import sys
import os

# 调试信息
IS_DEBUG = True
def debug(msg):
    if IS_DEBUG:
        print(f"[DEBUG] {msg}")

# 尝试导入行空板专用库 - 仅使用V3版本(最稳定版本)
try:
    # 添加可能的库路径
    paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "libraries"),
        "/usr/lib/python3/dist-packages",
        "/usr/local/lib/python3/dist-packages",
        os.path.expanduser("~/.local/lib/python3/dist-packages"),
        "/usr/share/unihiker/lib"
    ]
    
    # 添加所有可能路径
    for path in paths:
        if path not in sys.path and os.path.exists(path):
            debug(f"添加库搜索路径: {path}")
            sys.path.append(path)
    
    debug("尝试导入PinPong专用库V3...")
    from unihiker_uv_patch_v3 import PatchUVSensor
    print("检测到行空板环境，使用行空板PinPong专用库 V3")
    USE_UNIHIKER_LIB = True
    debug("PinPong专用库V3导入成功")
except ImportError as e:
    debug(f"PinPong专用库V3导入失败: {str(e)}")
    # 尝试导入标准库
    try:
        debug("尝试导入标准库...")
        from DFRobot_UVIndex240370Sensor import DFRobot_UVIndex240370Sensor_I2C
        USE_UNIHIKER_LIB = False
        debug("标准库导入成功")
    except ImportError as e:
        print(f"错误: 无法导入UV传感器库: {str(e)}")
        print("请确保已正确安装相关库文件")
        USE_UNIHIKER_LIB = False`);
        Generator.addCode(`# 定义传感器错误处理类
class DummySensor:
    def read_UV_index_data(self): 
        print("错误: 未连接传感器，无法读取UV指数")
        return 0
    def read_UV_original_data(self): 
        print("错误: 未连接传感器，无法读取原始数据")
        return 0
    def read_risk_level_data(self): 
        print("错误: 未连接传感器，无法读取风险等级")
        return 0
    def begin(self): 
        return False
        
# 初始化传感器
try:
    if USE_UNIHIKER_LIB:
        debug("使用行空板专用库初始化...")
        # 行空板专用库 - 自动扫描总线和地址
        # 强制使用真实传感器数据，不允许使用模拟数据
        uv = PatchUVSensor(debug_mode=True, force_real=True)
        try:
            success = uv.begin()
            if success:
                print("✓ 行空板紫外线传感器初始化成功！")
            else:
                print("✗ 未能找到紫外线传感器")
                print("  - 请确认传感器已正确连接")
                print("  - 检查I2C连接线是否牢固")
                print("  - 确认传感器电源正常")
                print("  - 可能需要重启行空板")
                # 使用前面定义的DummySensor
                uv = DummySensor()
        except Exception as e:
            print(f"✗ 传感器初始化错误: {e}")
            print("  - 请检查传感器连接")
            print("  - 确认I2C接口正确连接")
            # 使用前面定义的DummySensor
            uv = DummySensor()
    else:
        debug("使用标准库初始化...")
        # 尝试多种总线组合
        bus_success = False
        
        # 尝试的总线列表 (不同平台可能不同)
        bus_list = [1, 0, 2, 3]
        
        for bus in bus_list:
            if bus_success:
                break
                
            try:
                debug(f"尝试总线 {bus}...")
                uv = DFRobot_UVIndex240370Sensor_I2C(bus)
                success = uv.begin()
                
                if success:
                    print(f"✓ 紫外线传感器初始化成功！(总线 {bus})")
                    bus_success = True
                    break
            except Exception as e:
                debug(f"总线 {bus} 初始化失败: {str(e)}")
                
        if not bus_success:
            print("✗ 未能初始化紫外线传感器")
            print("  - 请检查传感器连接")
            print("  - 确认I2C接口正确连接")
            print("  - 确保已启用所需的I2C总线")

except Exception as e:
    print(f"✗ 传感器初始化错误: {str(e)}")
    print("请检查传感器连接或者是否已安装所需库文件")
    # 使用前面定义的DummySensor
    uv = DummySensor()
    
# 确保传感器对象已初始化
if 'uv' not in locals():
    print("✗ 未能找到传感器硬件")
    uv = DummySensor()
        
time.sleep(0.5)`);
    }

    /**
     * 读取紫外线数值
     */
    //% block="读取紫外线[eType]"
    //% eType.shadow="dropdown" eType.options=UVDataType eType.defl=UVDataType.UV指数
    //% weight=90
    //% blockId=readUV
    //% blockType="reporter"
    export function readUV(parameter: any): number {
        const type = parameter.eType.code;
        if (type === "UV指数") {
            Generator.addCode(`int(uv.read_UV_index_data())`);
        } else if (type === "原始数据") {
            Generator.addCode(`int(uv.read_UV_original_data())`);
        } else if (type === "风险等级") {
            Generator.addCode(`int(uv.read_risk_level_data())`);
        } else {
            Generator.addCode(`0`);
        }
        return 0;
    }
}