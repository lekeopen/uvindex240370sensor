# Mind+ 用户库项目布局指南

本文档详述了紫外线传感器库的文件夹结构和各个文件的用途，方便开发者了解和修改代码。

## 1. 顶级目录结构

```
UvIndex240370Sensor_New/
├── arduinoC/        - Arduino相关文件
├── python/          - Python相关文件
├── examples/        - 示例程序
├── docs/            - 文档
├── config.json      - 配置文件
├── README.md        - 项目说明
├── package_extension.sh - 打包脚本
└── deploy_to_unihiker.sh - 部署脚本
```

## 2. Python 目录

Python 目录包含与 Python 语言相关的文件，结构如下：

```
python/
├── _images/         - 图标和图片资源
│   ├── featured.png - 扩展特色图
│   └── icon.svg     - 扩展图标
├── _locales/        - 多语言支持文件
│   ├── en.json      - 英文翻译
│   ├── zh-cn.json   - 简体中文翻译
│   └── zh-tw.json   - 繁体中文翻译
├── libraries/       - Python库文件
│   ├── unihiker_uv_patch_v2.py     - 主要驱动库，使用smbus
│   ├── unihiker_uv_patch_v3.py     - V3版本驱动库，使用PinPong
│   └── DFRobot_UVIndex240370Sensor_unihiker.py - 原始驱动库
└── main.ts          - Python积木定义
```

### 2.1 主要库文件说明

- **unihiker_uv_patch_v2.py**: V2 版本的驱动库，使用 smbus 实现 I2C 通信，提供设备自动扫描和错误处理功能。
- **unihiker_uv_patch_v3.py**: V3 版本的驱动库，使用 PinPong 库实现 I2C 通信，适合于集成在 Mind+ 环境中。
- **DFRobot_UVIndex240370Sensor_unihiker.py**: 原始驱动库，提供完整的功能实现，作为参考和备用。

## 3. Arduino 目录

Arduino 目录包含与 Arduino 平台相关的文件，结构如下：

```
arduinoC/
├── _images/         - 图标和图片资源
├── _locales/        - 多语言支持文件
├── libraries/       - Arduino库文件
└── main.ts          - Arduino积木定义
```

## 4. 示例程序

示例程序目录包含多种用途的示例代码，方便用户快速上手：

```
examples/
├── basic_uv_example.py     - 基础使用示例
├── gui_uv_monitor.py       - 行空板GUI界面示例
├── mindplus_integration.py - Mind+集成示例
├── test_library.py         - 库测试脚本
├── unihiker_uv_sensor.py   - 简化版独立库
├── uv_integrated_test.py   - 集成测试示例
└── uv_simple_fix.py        - 简化版修复示例
```

### 4.1 示例程序说明

- **basic_uv_example.py**: 最基本的传感器使用示例，适合初学者。
- **gui_uv_monitor.py**: 带有 GUI 界面的监测示例，在行空板上显示更直观的数据。
- **mindplus_integration.py**: 与 Mind+集成的完整示例，适合 Mind+用户。
- **test_library.py**: 测试库功能的工具脚本，用于验证安装是否正确。
- **unihiker_uv_sensor.py**: 一个简化版的独立库，所有功能整合在一个文件中。
- **uv_integrated_test.py**: 集成测试示例，用于全面测试传感器功能。
- **uv_simple_fix.py**: 简化版的修复方案，为解决问题提供最简单的代码。

## 5. 文档

文档目录包含各类说明文档：

```
docs/
├── USER_GUIDE.md                - 用户指南
├── TECHNICAL_SPEC.md            - 技术规范
├── CONTRIBUTING.md              - 贡献指南
├── CHANGELOG.md                 - 更新日志
├── MINDPLUS_LIBRARY_DEV_GUIDE.md - Mind+用户库开发指南
└── PACKAGING_GUIDE.md           - 打包与发布指南
```

## 6. 工具脚本

项目根目录下的脚本文件：

- **package_extension.sh**: 用于打包生成 Mind+扩展文件(.mpext)的脚本。
- **deploy_to_unihiker.sh**: 用于部署到行空板的脚本，方便测试和调试。

## 7. 配置文件

- **config.json**: 定义了扩展包的基本信息，包括名称、版本、作者、依赖文件等。

## 8. 修改指南

### 8.1 添加新功能

添加新功能时，需要修改以下文件：

1. 在 `python/libraries/unihiker_uv_patch_v2.py` 中添加新方法
2. 在 `python/main.ts` 中添加对应的积木块定义
3. 在 `python/_locales/` 下的各语言文件中添加对应的翻译

### 8.2 修改现有功能

修改现有功能时，确保同时更新：

1. 驱动库文件中的代码
2. 相关的示例程序
3. 文档中的说明

### 8.3 发布新版本

发布新版本时的步骤：

1. 更新 `config.json` 中的版本号
2. 更新 `CHANGELOG.md` 添加新版本的变更记录
3. 运行 `./package_extension.sh` 生成新的扩展包
