#!/bin/bash
# 一键截图调试 - 最简单的方案

# 创建截图目录
mkdir -p screenshots

# 生成文件名
timestamp=$(date +%Y%m%d_%H%M%S)
filename="debug_${timestamp}.png"
filepath="screenshots/${filename}"

echo "📸 正在截图..."

# 截图
screencapture -x -t png "$filepath"

if [ $? -eq 0 ]; then
    echo "✅ 截图成功: $filepath"
    echo ""
    echo "🤖 现在你可以说:"
    echo "   'Claude，分析截图 $filename'"
    echo "   或者"
    echo "   'Claude，看这个错误截图'"
    echo ""
    echo "📁 截图路径: $(pwd)/$filepath"
else
    echo "❌ 截图失败"
fi