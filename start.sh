#!/bin/bash

# Start the hospital management dashboard
echo "启动医院管理仪表盘..."
echo "请确保已安装所需依赖: pip install -r requirements.txt"
echo ""
echo "应用将在以下地址运行:"
echo "本地访问: http://localhost:8501"
echo "网络访问: http://192.168.1.113:8501"
echo ""
echo "按 Ctrl+C 停止应用"
echo ""

streamlit run app.py