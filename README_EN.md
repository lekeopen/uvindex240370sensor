# Gravity: 240370 UV Index Sensor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-0.1.0-blue.svg)](https://github.com/rockts/lekeopen-uvindex240370sensor)

<div align="center">
  <img src="./arduinoC/_images/featured.png" width="400" alt="UV Index Sensor"/>
</div>

**Language**: [English](README_EN.md) | [中文](README.md)

## 📋 Introduction

This is a DFRobot Gravity 240370 UV Index Sensor extension optimized for Unihiker. It detects ultraviolet intensity in the 240-370nm wavelength range, covering UVA, UVB, and UVC spectrums. Through low-level processing, it directly outputs UV index levels from 0-11 and risk warnings from 1-5. This extension package solves I2C communication issues on the Unihiker board and optimizes device recognition and data processing logic. It specifically fixes UV index and risk level calculation issues for certain raw values (3, 6, 14, 48, 512).

## ✨ Key Features

- 🌈 Wavelength range 240-370nm, covering UVA/UVB/UVC
- 🔢 Direct output of UV index and risk level, no conversion needed
- 🛠️ Fixed Unihiker PinPong library I2C communication issues
- 📊 Improved UV index calculation and error handling
- 🌐 Supports both Arduino and Unihiker platforms
- 🔌 Provides Mind+ visual programming support

## 📥 Download & Installation

Download the latest extension package from the [Releases](https://github.com/rockts/lekeopen-uvindex240370sensor/releases) page.

- Current version: [rockts-lekeopen-uvindex240370sensor-thirdex-V0.1.0.mpext](https://github.com/rockts/lekeopen-uvindex240370sensor/raw/main/rockts-lekeopen-uvindex240370sensor-thirdex-V0.1.0.mpext)

## 🚀 Usage

### Using with Mind+

1. Download the latest `.mpext` extension file
2. Open Mind+, click "Extensions" → "Manage Extensions" → "Import Local Extension"
3. Select the downloaded extension package to install
4. Find the "Gravity: 240370 UV Index Sensor" blocks in the blocks area
5. Use the blocks to read UV index, raw data, or risk level

### Using with Python

```python
from unihiker_uv_patch_v3 import PatchUVSensor

# Create sensor object
sensor = PatchUVSensor()
sensor.begin()

# Read data
raw_value = sensor.read_UV_original_data()
uv_index = sensor.read_UV_index_data()
risk_level = sensor.read_risk_level_data()

print(f"Raw value: {raw_value}")
print(f"UV index: {uv_index}")
print(f"Risk level: {risk_level}")
```

### Using with Arduino

```cpp
#include <DFRobot_UVIndex240370Sensor.h>

DFRobot_UVIndex240370Sensor UVSensor;

void setup() {
  Serial.begin(115200);

  // Initialize sensor
  UVSensor.begin();
}

void loop() {
  // Read raw value
  uint16_t raw = UVSensor.getRaw();

  // Read UV index
  uint8_t index = UVSensor.getUvIndex();

  // Read risk level
  uint8_t riskLevel = UVSensor.getRiskLevel();

  Serial.print("Raw value: ");
  Serial.println(raw);

  Serial.print("UV index: ");
  Serial.println(index);

  Serial.print("Risk level: ");
  Serial.println(riskLevel);

  delay(1000);
}
```

## 🌡️ UV Risk Level Guide

| UV Index | Risk Level | Protection Recommendations                                  |
| -------- | ---------- | ----------------------------------------------------------- |
| 0-2      | Low        | Safe for outdoor activities, no special protection needed   |
| 3-5      | Moderate   | Recommend sunscreen and sunglasses for outdoor activities   |
| 6-7      | High       | Avoid midday sun exposure, use SPF15+ sunscreen             |
| 8-10     | Very High  | Minimize outdoor activities, take comprehensive protection  |
| 11+      | Extreme    | Avoid sun exposure when possible, full protection mandatory |

## 🔧 Hardware Connection

### Arduino Connection

| Sensor Pin | Arduino Pin          |
| ---------- | -------------------- |
| VCC        | 5V/3.3V              |
| GND        | GND                  |
| SDA        | A4 (UNO) / 20 (MEGA) |
| SCL        | A5 (UNO) / 21 (MEGA) |

### Unihiker Connection

| Sensor Pin | Unihiker Pin |
| ---------- | ------------ |
| VCC        | 3.3V         |
| GND        | GND          |
| SDA        | SDA          |
| SCL        | SCL          |

## 📝 Sensor Specifications

- **Supply voltage**: 3.3V - 5V
- **Communication interface**: I2C
- **Wavelength range**: 240-370nm
- **Measurement range**: UV index 0-11+
- **Accuracy**: ±1 UV index
- **Response time**: <1s
- **Operating temperature**: -20℃ to 85℃
- **Dimensions**: 29.0 × 22.0 mm

## 📁 Repository Structure

**Repository type**: This is the published repository structure that contains only the essential files needed for use.

### Repository Structure

```
/
├── config.json               # Extension configuration file
├── LICENSE                   # MIT license
├── README.md                 # Chinese documentation
├── README_EN.md              # English documentation
├── lekeopen-uvindex240370sensor-V0.1.0.mpext  # Latest version of extension package
├── arduinoC/                 # Arduino platform files (simplified structure)
│   ├── _images/
│   ├── _locales/
│   ├── libraries/
│   │   └── libraries.zip     # Packaged Arduino libraries
│   └── main.ts               # Arduino blocks definition file
└── python/                   # Python platform files (simplified structure)
    ├── _images/
    ├── _locales/
    ├── libraries/
    │   └── libraries.zip     # Packaged Python libraries
    └── main.ts               # Python blocks definition file
```

## 🔄 Version History

- **0.1.0** (2025.05.14)

  - Restructured the project, optimized code organization
  - Removed development directories, keeping the remote repository clean
  - Fixed UV index calculation for specific raw values (0, 3, 6, 14, 48, 512)
  - Enhanced `.gitignore` rules to prevent unnecessary file commits
  - Fixed critical data acquisition and processing issues

- **0.0.9** (2025.05.13)
  - Streamlined code structure, removed debug information
  - Optimized sensor initialization logic
  - Acknowledged original project authors
- **0.0.8** (2025.05.13)
  - Fixed abnormal UV index when raw value is 1024
  - Optimized data processing logic, enhanced data consistency
  - Resolved issue where raw value was 0 but UV index was 1
- **0.0.7** (2025.05.13)
  - Fixed Mind+ import error
  - Ensured proper packaging of libraries.zip files
  - Optimized packaging scripts
- **0.0.6** (2025.05.13)
  - Optimized data display format, resolved terminal data overlap issues
  - Used ASCII frame formatting for improved readability
  - Added screen clearing control to prevent data accumulation
- **0.0.5** (2025.05.13)
  - Fixed risk level calculation error when UV index is 1
  - Improved data output methods, added text labels
  - Created automated scripts to manage remote repository
- **0.0.4** (2025.05.13)
  - Fixed byte order issues, optimized data processing logic
  - Enhanced zero value handling and data smoothing filters
  - Resolved data jumps and reading errors
- **0.0.3** (2025.05.13)
  - Fixed Arduino Uno compatibility issues
  - Added extension package management features
  - Optimized library file structure
- **0.0.2** (2025.05.13)
  - Improved error handling mechanisms
  - Enhanced device recognition logic
- **0.0.1** (2025.05.12)
  - Initial release
  - Support for Unihiker and Arduino platforms
  - Basic UV index measurement functionality

## 👨‍💻 Contributing

Issues and feature requests are welcome. If you want to contribute code, please fork and submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
