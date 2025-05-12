# 远程仓库管理指南

本指南详细说明了如何在本地开发与远程仓库之间高效地管理项目资源，特别是针对 README 文件和 MPEXT 扩展文件的处理。

## 管理工具概览

本项目包含三个主要的管理脚本，位于 `scripts/` 目录下：

1. **prepare_remote_readme.sh** - 管理 README.md 文件，使其针对远程仓库进行优化
2. **manage_remote_mpext.sh** - 管理 MPEXT 文件，确保远程仓库只保留最新版本
3. **prepare_remote_repo.sh** - 综合管理脚本，执行上述两个脚本并提供完整的远程仓库发布流程

## 自动化规则

这些脚本遵循以下规则：

- **本地项目目录**：保留最新的 3 个 MPEXT 文件
- **远程 Git 仓库**：只保留最新的 1 个 MPEXT 文件
- **README 文件**：本地与远程使用不同版本的 README 文件，远程版本针对 GitHub 优化

## 文件对应关系

| 文件名           | 用途                           | 位置       |
| ---------------- | ------------------------------ | ---------- |
| README.md        | 当前活跃的 README 文件         | 项目根目录 |
| README_LOCAL.md  | 本地开发用的 README 备份       | 项目根目录 |
| README_REMOTE.md | 针对远程仓库优化的 README 模板 | 项目根目录 |

## 使用方法

### 准备发布到远程仓库

使用综合管理脚本一键完成所有发布前准备工作：

```bash
./scripts/prepare_remote_repo.sh
```

此脚本会执行以下操作：

1. 检查并列出当前 MPEXT 文件状态
2. 准备远程仓库专用的 README.md
3. 管理 MPEXT 文件，只保留最新版本
4. 执行最终状态检查并提供推送选项
5. 可选创建版本标签

### 仅更新远程仓库专用的 README

如果只需更新 README 文件，可以单独运行：

```bash
./scripts/prepare_remote_readme.sh
```

### 仅管理 MPEXT 文件

如果只需管理 MPEXT 文件，可以单独运行：

```bash
./scripts/manage_remote_mpext.sh
```

## 恢复本地 README

发布到远程仓库后，如需恢复本地开发用的 README，执行：

```bash
cp README_LOCAL.md README.md
```

## 自定义远程 README

如需修改远程仓库专用的 README 内容，请编辑 `README_REMOTE.md` 文件，而不是直接修改 `README.md`。

## 常见问题

### 没有 README_REMOTE.md 文件

如果缺少 `README_REMOTE.md` 文件，可以复制当前的 README.md 并根据需要修改：

```bash
cp README.md README_REMOTE.md
```

然后编辑 `README_REMOTE.md` 文件，添加针对 GitHub 的徽章、说明等内容。

### 版本号不一致

如果 MPEXT 文件名中的版本号与 `config.json` 中的版本号不一致，脚本会提供警告。请确保更新 `config.json` 中的版本号，并重新构建 MPEXT 文件。

### 手动推送到远程仓库

如果自动推送失败或选择稍后手动推送，请使用：

```bash
git push origin <分支名>
```

## 帮助与支持

如有问题，请联系项目维护者：

- **作者**: rockts
- **邮箱**: gaopeng@lekee.cc
