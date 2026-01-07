#!/bin/bash
# 自动Git提交脚本
# Auto Git Commit Script
# 每15分钟自动提交一次代码

INTERVAL=900  # 15分钟 = 900秒
MAX_RETRIES=3
RETRY_DELAY=900  # 15分钟后重试

while true; do
  # 检查是否有未提交的更改
  if [ -n "$(git status --porcelain)" ]; then
    echo "$(date): 检测到代码更改，准备提交 | Code changes detected, preparing commit..."
    
    # 添加所有更改
    git add -A
    
    # 生成提交信息
    COMMIT_MSG="Auto commit: $(date '+%Y-%m-%d %H:%M:%S') - 自动测试和代码更新 | Auto test and code update"
    
    # 尝试提交
    RETRY_COUNT=0
    SUCCESS=false
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$SUCCESS" = false ]; do
      if git commit -m "$COMMIT_MSG" 2>/dev/null; then
        echo "$(date): 提交成功 | Commit successful"
        
        # 尝试推送到远程
        if git push origin main 2>/dev/null || git push origin master 2>/dev/null; then
          echo "$(date): 推送成功 | Push successful"
          SUCCESS=true
        else
          echo "$(date): 推送失败，将在15分钟后重试 | Push failed, will retry in 15 minutes"
          sleep $RETRY_DELAY
          RETRY_COUNT=$((RETRY_COUNT + 1))
        fi
      else
        echo "$(date): 提交失败，可能是没有更改或网络问题 | Commit failed, may be no changes or network issue"
        SUCCESS=true  # 即使提交失败也继续，可能是没有实际更改
      fi
    done
    
    if [ "$SUCCESS" = false ]; then
      echo "$(date): 达到最大重试次数，等待下次循环 | Max retries reached, waiting for next cycle"
    fi
  else
    echo "$(date): 没有代码更改 | No code changes"
  fi
  
  # 等待指定时间
  sleep $INTERVAL
done

