# 错误监控配置 (Sentry)

## 安装

```bash
pip install sentry-sdk
```

## 配置

在 `src/backend/main.py` 中添加:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    environment=config.get('environment', 'development'),
)
```

## 环境变量

在 `.env` 文件中添加:

```
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
SENTRY_ENVIRONMENT=development
```

## 本地开发

本地开发时可不启用 Sentry，或使用本地错误日志:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/error.log'),
        logging.StreamHandler()
    ]
)
```

## 日志目录

```bash
mkdir -p logs
```
