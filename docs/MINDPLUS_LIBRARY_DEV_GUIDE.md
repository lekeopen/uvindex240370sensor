# Mind+ 用户库开发指南

本文档简要说明 Mind+用户库的开发规范和目录结构。

## 项目结构

Mind+用户库标准结构如下：

```
项目根目录/
├── arduinoC/        - Arduino相关文件
│   ├── _images/     - 图标和图片资源
│   ├── _locales/    - 多语言支持文件
│   │   ├── en.json      - 英文翻译
│   │   ├── zh-cn.json   - 简体中文翻译
│   │   └── zh-tw.json   - 繁体中文翻译
│   ├── libraries/   - Arduino库文件
│   └── main.ts      - Arduino积木定义文件
├── python/          - Python相关文件
│   ├── _images/     - 图标和图片资源
│   │   ├── featured.png - 扩展特色图
│   │   └── icon.svg     - 扩展图标
│   ├── _locales/    - 多语言支持文件
│   │   ├── en.json      - 英文翻译
│   │   ├── zh-cn.json   - 简体中文翻译
│   │   └── zh-tw.json   - 繁体中文翻译
│   ├── libraries/   - Python库文件
│   └── main.ts      - Python积木定义文件
├── examples/        - 示例程序
├── docs/            - 文档
├── config.json      - 项目配置文件
└── README.md        - 项目说明
```

## 配置文件格式

`config.json`是 Mind+用户库的核心配置文件，定义了库的基本信息和文件组织：

```json
{
 "name": {
  "zh-cn": "中文名称",
  "en": "English Name"
 },
 "description": {
  "zh-cn": "中文描述",
  "zh-tw": "繁体中文描述",
  "en": "English description"
 },
 "author": "作者名称",
 "email": "作者邮箱",
 "license": "许可证（如MIT）",
 "isBoard": false,
 "id": "库唯一标识符",
 "platform": ["win", "mac", "linux"],
 "version": "版本号",
 "mode": ["arduinoC", "python"],
 "asset": {
  "arduinoC": {
   "dir": "arduinoC/",
   "board": ["支持的开发板列表"],
   "main": "main.ts",
   "files": ["所需文件列表"]
  },
  "python": {
   "dir": "python/",
   "main": "main.ts",
   "files": ["所需文件列表"]
  }
 }
}
```

## 积木块定义

积木块在`main.ts`文件中定义，使用 TypeScript 语法:

```typescript
//% color="#00BCD4" icon="\uf185" block="积木类别名称"
//% version="版本号"
namespace pythonBlockNamespace {
 //% block="积木显示文本"
 //% weight=100
 //% blockId=uniqueBlockId
 //% blockType="command"
 export function blockFunction(): void {
  Generator.addImport(`import 需要的Python库`);
  Generator.addCode(`Python代码实现`);
 }
}
```

## 多语言支持

多语言在`_locales`目录的 JSON 文件中定义：

```json
{
 "namespace.blockFunction": "积木显示文本",
 "namespace.enumName.0": "选项1",
 "namespace.enumName.1": "选项2"
}
```

## 打包方法

Mind+用户库打包为`.mpext`文件，本质上是一个 ZIP 文件，包含所有必要的文件。使用`package_extension.sh`脚本可以自动完成打包过程。

## 最佳实践

1. **清晰的文档**: 提供详细的使用说明和示例
2. **错误处理**: 添加全面的错误处理和用户友好的提示
3. **兼容性**: 确保与不同硬件平台和 Mind+版本兼容
4. **版本控制**: 使用语义化版本控制
5. **本地化**: 提供多语言支持，特别是中英文
6. **示例程序**: 提供简单而实用的示例程序

## 开发流程

1. 规划功能和积木块设计
2. 开发和测试底层库
3. 编写 main.ts 定义积木块
4. 添加多语言支持
5. 准备示例和文档
6. 打包和测试扩展
7. 发布和维护

## 参考资料

- [Mind+官方网站](https://mindplus.cc/)
- [Mind+扩展开发文档](https://mindplus.dfrobot.com.cn/extensions-guide)
- [TypeScript 文档](https://www.typescriptlang.org/docs/)
