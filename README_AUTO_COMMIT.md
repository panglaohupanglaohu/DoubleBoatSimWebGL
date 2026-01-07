# 自动Git提交系统使用说明
# Auto Git Commit System Usage

## 概述 | Overview

本项目包含自动Git提交系统，每15分钟自动检查代码更改并提交到GitHub。

This project includes an auto Git commit system that automatically checks for code changes every 15 minutes and commits to GitHub.

## 使用方法 | Usage

### 方法1: 使用Node.js脚本（推荐）| Method 1: Node.js Script (Recommended)

```bash
# 安装依赖（如果需要）
npm install

# 运行自动提交脚本
node scripts/auto-commit.js
```

### 方法2: 使用Shell脚本 | Method 2: Shell Script

```bash
# 给脚本添加执行权限
chmod +x scripts/auto-commit.sh

# 运行脚本
./scripts/auto-commit.sh
```

### 方法3: 使用npm脚本 | Method 3: npm Script

在 `package.json` 中添加：

```json
{
  "scripts": {
    "auto-commit": "node scripts/auto-commit.js"
  }
}
```

然后运行：

```bash
npm run auto-commit
```

## 功能特性 | Features

- ✅ 每15分钟自动检查代码更改
- ✅ 自动添加所有更改的文件
- ✅ 自动生成提交信息（包含时间戳）
- ✅ 自动推送到远程仓库（main或master分支）
- ✅ 网络断开时自动重试（15分钟后）
- ✅ 最多重试3次

## 注意事项 | Notes

1. **首次使用前**，请确保已配置Git用户信息：
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. **确保已设置远程仓库**：
   ```bash
   git remote add origin <your-repo-url>
   ```

3. **建议在后台运行**，可以使用以下方式：
   - Linux/Mac: `nohup node scripts/auto-commit.js &`
   - Windows: 使用任务计划程序或PowerShell后台任务

4. **安全提示**：自动提交会提交所有更改，请确保工作目录中只有需要提交的文件。

## 停止自动提交 | Stop Auto Commit

- 按 `Ctrl+C` 停止脚本
- 或使用进程管理工具（如 `pm2`）管理脚本运行

## 日志 | Logs

脚本会在控制台输出详细的日志信息，包括：
- 检查时间
- 代码更改状态
- 提交和推送结果
- 错误信息

## 故障排除 | Troubleshooting

### 问题：推送失败
**解决方案**：
- 检查网络连接
- 检查GitHub认证（SSH密钥或访问令牌）
- 脚本会自动在15分钟后重试

### 问题：提交失败
**可能原因**：
- 没有实际更改
- Git配置问题
- 权限问题

**解决方案**：
- 检查 `git status` 确认是否有更改
- 检查Git配置
- 检查文件权限

## 自定义配置 | Customization

可以修改脚本中的以下参数：

- `INTERVAL`: 检查间隔（默认15分钟）
- `MAX_RETRIES`: 最大重试次数（默认3次）
- `RETRY_DELAY`: 重试延迟（默认15分钟）

