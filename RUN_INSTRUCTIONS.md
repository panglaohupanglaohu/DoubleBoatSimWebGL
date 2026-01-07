# 运行说明 | Run Instructions

## 问题解决 | Troubleshooting

如果遇到以下错误：
```
GET http://localhost:3000/public/gui-enhancements.css net::ERR_CONNECTION_REFUSED
GET http://localhost:3000/src/demo-refactored.js net::ERR_CONNECTION_REFUSED
```

## 解决方案 | Solution

### 方法 1：使用 npm start（推荐）

1. 打开终端/命令行
2. 进入项目目录：
   ```bash
   cd D:\DoubleBoatDT
   ```
3. 运行服务器：
   ```bash
   npm start
   ```
4. 服务器会在默认端口（通常是 5000）启动
5. 在浏览器中访问：`http://localhost:5000/index-refactored.html`

### 方法 2：使用指定端口

```bash
npm run start:8000
```

然后访问：`http://localhost:8000/index-refactored.html`

### 方法 3：使用 Python 简单服务器（如果没有 npm）

```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

然后访问：`http://localhost:8000/index-refactored.html`

## 重要提示 | Important Notes

⚠️ **不要直接双击打开 HTML 文件**（file:// 协议）
- 由于浏览器的安全限制，直接打开 HTML 文件无法正确加载 ES6 模块
- 必须通过 HTTP 服务器访问

✅ **必须使用 HTTP 服务器**
- 使用 `npm start` 或其他 HTTP 服务器
- 确保通过 `http://localhost:端口号` 访问

## 检查服务器是否运行

在浏览器中访问：
- `http://localhost:5000/index-refactored.html`（默认端口）
- 或 `http://localhost:8000/index-refactored.html`（如果使用 8000 端口）

如果看到页面正常加载，说明服务器运行正常。

