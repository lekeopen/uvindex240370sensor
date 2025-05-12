# 贡献指南

感谢您对紫外线传感器库的关注！本文档将指导您如何为这个项目做出贡献。

## 开发环境设置

1. 克隆或下载项目代码
2. 确保您具有以下开发环境：
   - Python 3.6+
   - 行空板(UniHiker)或兼容设备
   - Mind+ 软件(可选，用于测试积木功能)

## 代码结构

主要文件和目录：

- `python/libraries/`: Python 库文件
  - `unihiker_uv_patch_v2.py`: 主要传感器驱动
  - `DFRobot_UVIndex240370Sensor_unihiker.py`: 原始驱动库
- `python/main.ts`: 定义 Mind+积木块
- `examples/`: 示例程序
- `docs/`: 文档文件
- `package_extension.sh`: 打包脚本

## 贡献流程

### 报告问题

如果您发现了问题，请提交问题报告，包括：

1. 使用的硬件和软件版本
2. 问题的详细描述
3. 如何重现该问题
4. 如果可能，附上代码示例和输出日志

### 提交更改

如果您想贡献代码，请遵循以下步骤：

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/your-feature`)
3. 提交您的更改 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建新的 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码风格
- 为所有函数和类添加清晰的文档字符串
- 在关键代码处添加注释
- 为新功能添加测试用例

## 测试

添加新功能或修复问题后，请执行以下测试：

1. **单元测试**:

   - 运行`examples`目录中的示例程序
   - 验证所有功能正常工作

2. **集成测试**:

   - 在 Mind+中测试积木功能
   - 确保与旧版本兼容

3. **文档测试**:
   - 确保更新了相关文档
   - 验证示例代码能正常运行

## 版本控制

我们使用语义化版本(Semantic Versioning)命名方案：

- **主版本号**: 不兼容的 API 更改
- **次版本号**: 向后兼容的功能新增
- **修订号**: 向后兼容的问题修复

## 发布流程

1. 更新`config.json`中的版本号
2. 更新 README 和 CHANGELOG
3. 运行`./package_extension.sh`打包
4. 测试新扩展包
5. 提交发布请求

## 文档

为您的更改添加或更新文档：

- 如果添加了新功能，请在技术文档中说明
- 更新用户指南以反映新的使用方法
- 给示例程序添加注释

## 开发建议

### 新增传感器功能

如果您想添加新功能：

```python
class PatchUVSensor:
    # ...现有代码...

    def your_new_function(self, parameter):
        """您的新功能的文档字符串

        Args:
            parameter: 参数说明

        Returns:
            返回值说明
        """
        # 功能实现
        return result
```

然后在`main.ts`中添加对应积木：

```typescript
/**
 * 您的新积木块
 */
//% block="您的新积木[param]"
//% param.shadow="dropdown" param.options=ParamOptions param.defl=ParamOptions.Option1
//% weight=80
//% blockId=yourNewBlock
//% blockType="reporter"
export function yourNewBlock(parameter: any): number {
 const param = parameter.param.code;
 Generator.addCode(`uv.your_new_function(${param})`);
 return 0;
}
```

### 优化建议

- **性能优化**: 减少不必要的 I2C 通信
- **错误处理**: 添加更详细的错误信息
- **用户体验**: 改进文档和示例
- **兼容性**: 测试并支持更多硬件平台

## 联系我们

如有任何问题或建议，请联系：

- 邮箱: gaopeng@lekee.cc
- 官网: https://www.dfrobot.com
