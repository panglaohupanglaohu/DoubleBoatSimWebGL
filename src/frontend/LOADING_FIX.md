# 🔍 GLB 加载问题诊断

**时间**: 2026-03-13 21:38

## 问题现象
- 进度条没有进度
- 一直显示"连接中..."

## 已确认
- ✅ GLB 文件可访问 (curl 测试通过)
- ✅ 文件大小 79MB
- ✅ 前端服务器运行正常

## 可能原因

### 1. Three.js GLTFLoader 进度回调问题
GLTFLoader 的 `onProgress` 回调在某些情况下可能不触发，特别是：
- 文件较大时
- 网络速度慢时
- 浏览器缓存影响

### 2. ES Module 加载问题
从 CDN 加载 Three.js 模块可能有：
- 跨域问题
- 版本兼容性
- 加载超时

### 3. 浏览器限制
- 大文件下载限制
- 本地文件访问限制

## 解决方案

### 方案 1: 使用 Fetch 预加载 (推荐)
```javascript
// 先用 fetch 下载，显示进度
const response = await fetch('GLB_20251223141542.glb');
const blob = await response.blob();
const url = URL.createObjectURL(blob);

// 然后用 GLTFLoader 加载 blob
loader.parse(reader.result, '', (gltf) => {
    // ...
});
```

### 方案 2: 简化模型
使用 Draco 压缩或简化模型，从 79MB 减小到 10-20MB

### 方案 3: 使用简化模型
暂时使用简化的 BoxGeometry 双体船，保证可演示

## 立即行动

1. **访问诊断页面**: `http://localhost:3000/test-glb-direct.html`
   - 查看实际下载速度
   - 确认文件是否可完整下载

2. **如果下载成功**: Three.js 代码问题
3. **如果下载失败**: 服务器/网络问题
