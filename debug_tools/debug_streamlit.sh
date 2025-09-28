#!/bin/bash
# Streamlit Debug Helper - 让Claude能看到你的终端输出
# 用法: ./debug_streamlit.sh

echo "🔍 启动Streamlit调试模式..."

# 清理旧的日志文件
rm -f debug.log

# 启动Streamlit，所有输出重定向到debug.log
echo "📝 所有输出将写入 debug.log 文件"
echo "🚀 启动应用: http://localhost:8501"
echo "⚡ Claude可以实时读取debug.log来帮你修复错误"
echo ""

# 运行streamlit，同时输出到终端和文件
streamlit run ../app.py 2>&1 | tee debug.log