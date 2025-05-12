# MPEXT 文件管理指南

本文档说明如何使用脚本来管理 `.mpext` 扩展文件，确保本地和远程仓库保持整洁。

## 自动化管理规则

1. **本地项目目录**：只保留最新的 3 个 `.mpext` 文件
2. **远程 Git 仓库**：只保留最新的 1 个 `.mpext` 文件

## 使用方法

### 构建新扩展并自动清理旧文件

执行以下命令构建新的扩展包，并自动清理旧的 `.mpext` 文件，只保留最新的 3 个：

```bash
./scripts/build_extension.sh
```

### 管理远程仓库中的 MPEXT 文件

执行以下命令确保远程仓库中只保留最新的 1 个 `.mpext` 文件：

```bash
./scripts/manage_remote_mpext.sh
```

然后执行 `git push` 将更改推送到远程仓库。

## 注意事项

- 这些脚本应在项目根目录下执行
- 在提交前请确保最新的 `.mpext` 文件已经过测试
- `manage_remote_mpext.sh` 脚本会自动创建 git 提交，您只需要执行 `git push`

## 手动管理方法

如果需要手动管理 `.mpext` 文件：

1. **查看所有 mpext 文件**：
   ```bash
   ls -la *.mpext
   ```

2. **只保留最新的 3 个文件**：
   ```bash
   ls -t *.mpext | tail -n +4 | xargs rm -f
   ```

3. **在 Git 中移除旧的 mpext 文件**：
   ```bash
   git rm --cached 旧文件名.mpext
   git add 新文件名.mpext
   git commit -m "更新 mpext 文件"
   git push
   ```
