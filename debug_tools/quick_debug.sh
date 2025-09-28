#!/bin/bash
# 快速错误检查 - 立即显示最新错误

echo "🔍 检查最新错误..."

if [ ! -f "debug.log" ]; then
    echo "❌ debug.log 文件不存在"
    exit 1
fi

echo "📊 最后20行日志:"
echo "=================================="
tail -20 debug.log

echo ""
echo "🔥 错误模式匹配:"
echo "=================================="

# 检查常见错误模式
grep -i -n -A 2 -B 1 "error\|exception\|traceback\|syntaxerror\|indentationerror" debug.log | tail -20

echo ""
echo "📈 文件状态:"
echo "=================================="
echo "文件大小: $(wc -l < debug.log) 行"
echo "最后修改: $(stat -f "%Sm" debug.log)"
echo ""
echo "💡 提示: 你现在可以说 'Claude，看debug.log' 我会立即分析所有错误！"