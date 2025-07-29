#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git实时备份脚本
使用方法: python backup.py "提交信息"
"""

import os
import sys
import subprocess
from datetime import datetime

def run_command(command):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def git_backup(commit_message):
    """执行Git备份"""
    print("🚀 开始Git实时备份...")
    print(f"📝 提交信息: {commit_message}")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 1. 检查Git状态
    print("🔍 检查Git状态...")
    success, stdout, stderr = run_command("git status --short")
    if not success:
        print(f"❌ 检查Git状态失败: {stderr}")
        return False
    
    if not stdout.strip():
        print("ℹ️ 没有更改需要提交")
        return True
    
    print("📋 更改的文件:")
    for line in stdout.strip().split('\n'):
        if line.strip():
            print(f"  {line}")
    
    # 2. 添加所有更改
    print("\n📦 添加所有更改...")
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"❌ 添加文件失败: {stderr}")
        return False
    
    # 3. 检查是否有更改需要提交
    success, stdout, stderr = run_command("git diff --cached --quiet")
    if success:
        print("ℹ️ 没有更改需要提交")
        return True
    
    # 4. 提交更改
    print("💾 提交更改...")
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ 提交失败: {stderr}")
        return False
    
    # 5. 显示提交结果
    print("✅ 备份完成！")
    success, stdout, stderr = run_command("git log --oneline -1")
    if success:
        print(f"📋 最新提交: {stdout.strip()}")
    
    print("🎉 Git实时备份成功！")
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("❌ 请提供提交信息")
        print("使用方法: python backup.py \"您的提交信息\"")
        print("\n💡 示例:")
        print("  python backup.py \"修复LLM异步调用问题\"")
        print("  python backup.py \"添加新的推荐算法\"")
        print("  python backup.py \"优化用户界面\"")
        return
    
    commit_message = sys.argv[1]
    success = git_backup(commit_message)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 