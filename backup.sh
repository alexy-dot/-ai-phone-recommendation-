#!/bin/bash

# Git实时备份脚本
# 使用方法: ./backup.sh "提交信息"

echo "🚀 开始Git实时备份..."

# 检查是否有参数
if [ -z "$1" ]; then
    echo "❌ 请提供提交信息"
    echo "使用方法: ./backup.sh \"您的提交信息\""
    exit 1
fi

# 获取提交信息
COMMIT_MESSAGE="$1"

echo "📝 提交信息: $COMMIT_MESSAGE"

# 检查Git状态
echo "🔍 检查Git状态..."
git status --short

# 添加所有更改
echo "📦 添加所有更改..."
git add .

# 检查是否有更改需要提交
if git diff --cached --quiet; then
    echo "ℹ️ 没有更改需要提交"
    exit 0
fi

# 提交更改
echo "💾 提交更改..."
git commit -m "$COMMIT_MESSAGE"

# 显示提交结果
echo "✅ 备份完成！"
echo "📋 最新提交:"
git log --oneline -1

echo "🎉 Git实时备份成功！" 