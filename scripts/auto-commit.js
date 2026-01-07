/**
 * 自动Git提交脚本（Node.js版本）
 * Auto Git Commit Script (Node.js version)
 * 每15分钟自动提交一次代码
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const INTERVAL = 15 * 60 * 1000; // 15分钟
const MAX_RETRIES = 3;
const RETRY_DELAY = 15 * 60 * 1000; // 15分钟后重试

function log(message) {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${message}`);
}

function checkGitStatus() {
  try {
    const status = execSync('git status --porcelain', { encoding: 'utf-8' });
    return status.trim().length > 0;
  } catch (error) {
    log('❌ 检查Git状态失败 | Failed to check git status: ' + error.message);
    return false;
  }
}

function commitAndPush() {
  try {
    // 添加所有更改
    execSync('git add -A', { stdio: 'inherit' });
    
    // 生成提交信息
    const commitMsg = `Auto commit: ${new Date().toISOString()} - 自动测试和代码更新 | Auto test and code update`;
    
    // 尝试提交
    try {
      execSync(`git commit -m "${commitMsg}"`, { stdio: 'inherit' });
      log('✅ 提交成功 | Commit successful');
    } catch (error) {
      log('⚠️ 提交失败（可能没有更改）| Commit failed (may be no changes)');
      return false;
    }
    
    // 尝试推送到远程
    let pushed = false;
    const branches = ['main', 'master'];
    
    for (const branch of branches) {
      try {
        execSync(`git push origin ${branch}`, { stdio: 'inherit' });
        log(`✅ 推送到 ${branch} 成功 | Push to ${branch} successful`);
        pushed = true;
        break;
      } catch (error) {
        log(`⚠️ 推送到 ${branch} 失败 | Push to ${branch} failed: ${error.message}`);
      }
    }
    
    if (!pushed) {
      log('⚠️ 所有推送尝试失败，将在15分钟后重试 | All push attempts failed, will retry in 15 minutes');
      return false;
    }
    
    return true;
  } catch (error) {
    log('❌ 提交/推送过程出错 | Error during commit/push: ' + error.message);
    return false;
  }
}

function retryCommitAndPush(retryCount = 0) {
  if (retryCount >= MAX_RETRIES) {
    log('❌ 达到最大重试次数，等待下次循环 | Max retries reached, waiting for next cycle');
    return;
  }
  
  const success = commitAndPush();
  
  if (!success && retryCount < MAX_RETRIES - 1) {
    log(`⏳ 等待 ${RETRY_DELAY / 1000} 秒后重试... | Waiting ${RETRY_DELAY / 1000} seconds before retry...`);
    setTimeout(() => {
      retryCommitAndPush(retryCount + 1);
    }, RETRY_DELAY);
  }
}

function main() {
  log('🚀 自动Git提交系统启动 | Auto Git commit system started');
  log(`⏰ 检查间隔: ${INTERVAL / 1000} 秒 | Check interval: ${INTERVAL / 1000} seconds`);
  
  setInterval(() => {
    if (checkGitStatus()) {
      log('📝 检测到代码更改，准备提交 | Code changes detected, preparing commit...');
      retryCommitAndPush();
    } else {
      log('✅ 没有代码更改 | No code changes');
    }
  }, INTERVAL);
  
  // 立即检查一次
  if (checkGitStatus()) {
    log('📝 检测到代码更改，准备提交 | Code changes detected, preparing commit...');
    retryCommitAndPush();
  }
}

// 启动
main();

