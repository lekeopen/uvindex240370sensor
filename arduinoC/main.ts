enum eDataType {
    OriginalData,
    IndexData,
    RiskLevelData,
}

//% color="#eb2f96"
namespace arduinoUVIndex240370Sensor {
    //% block="init UV Sensor I2C address as 0x23"
    //% blockType="command"
    export function initUVIndex240370Sensor_I2C() {
        Generator.addInclude('DFRobot_UVIndex240370Sensor', '#include "DFRobot_UVIndex240370Sensor.h"');
        Generator.addObject(`UVIndex240370Sensor`, `DFRobot_UVIndex240370Sensor`, `UVIndex240370Sensor(&Wire);`);
        Generator.addSetupTop(`UVIndex240370Sensor.begin`, `UVIndex240370Sensor.begin();`);
    }
    
    //% block="read UV [eType]"
    //% eType.shadow="dropdown" eType.options=eDataType eType.defl=eDataType.OriginalData
    //% blockType="reporter"
    export function readUv(parameter: any, block: any) {
        let type = parameter.eType.code;
        Generator.addInclude('DFRobot_UVIndex240370Sensor', '#include "DFRobot_UVIndex240370Sensor.h"');
        Generator.addObject(`UVIndex240370Sensor`, `DFRobot_UVIndex240370Sensor`, `UVIndex240370Sensor(&Wire);`);
        Generator.addSetupTop(`UVIndex240370Sensor.begin`, `UVIndex240370Sensor.begin();`);
        if(type === "OriginalData"){
            Generator.addCode(`UVIndex240370Sensor.readUvOriginalData()`);
        } else if(type === "IndexData"){
            Generator.addCode(`UVIndex240370Sensor.readUvIndexData()`);
        } else if(type === "RiskLevelData"){
            Generator.addCode(`UVIndex240370Sensor.readRiskLevelData()`);
        }
    }
}