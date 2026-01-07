# GLB模型文件说明 | GLB Model Files Notice

## 📦 文件位置 | File Location

由于GLB模型文件超过GitHub的文件大小限制（50-100MB），这些文件**未包含在Git仓库中**。

Because GLB model files exceed GitHub's file size limit (50-100MB), these files are **NOT included in the Git repository**.

## 📥 如何获取GLB文件 | How to Get GLB Files

### 当前使用的模型文件 | Currently Used Model File:
- **文件名 | Filename**: `GLB_20251223141542.glb`
- **大小 | Size**: 80.88 MB
- **路径 | Path**: `public/GLB_20251223141542.glb`

### 获取方式 | How to Obtain:

1. **从原始源获取** | Get from original source
   - 如果您有原始的GLB模型文件，请将其放置在 `public/` 目录下
   - If you have the original GLB model file, place it in the `public/` directory

2. **联系项目维护者** | Contact project maintainer
   - 通过云盘/网盘等方式获取大文件
   - Get the large file via cloud storage/network drive

3. **使用Git LFS（推荐）** | Use Git LFS (Recommended)
   ```bash
   # 安装 Git LFS | Install Git LFS
   git lfs install
   
   # 跟踪GLB文件 | Track GLB files
   git lfs track "public/*.glb"
   
   # 添加并提交 | Add and commit
   git add .gitattributes public/*.glb
   git commit -m "Add GLB files with Git LFS"
   git push
   ```

## ⚠️ 重要提示 | Important Notice

在运行项目之前，请确保 `public/` 目录下有至少一个GLB模型文件，否则船体模型将无法加载。

Before running the project, ensure there is at least one GLB model file in the `public/` directory, otherwise the ship model will not load.

## 📋 当前.gitignore设置 | Current .gitignore Settings

```
# Exclude large GLB files (>50MB) - download separately
public/*.glb
```

## 🔧 如果需要包含GLB文件 | To Include GLB Files

如果您想将GLB文件包含在Git仓库中，请使用Git LFS：

If you want to include GLB files in the Git repository, use Git LFS:

```bash
# 从.gitignore中移除GLB排除规则
# Remove GLB exclusion from .gitignore
# 然后安装并配置Git LFS
# Then install and configure Git LFS
```

---

**最后更新 | Last Updated**: 2026-01-07  
**版本 | Version**: v3.1.0

