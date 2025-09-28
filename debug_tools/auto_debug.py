#!/usr/bin/env python3
"""
智能错误监控 - 零copy paste调试系统
Claude Code自动错误检测和分析
"""

import time
import os
import re
from pathlib import Path

class ErrorMonitor:
    def __init__(self, log_file="debug.log"):
        self.log_file = Path(__file__).parent / log_file
        self.last_size = 0
        self.error_patterns = [
            r"Error:",
            r"Exception:",
            r"Traceback",
            r"SyntaxError:",
            r"ImportError:",
            r"ModuleNotFoundError:",
            r"AttributeError:",
            r"TypeError:",
            r"ValueError:",
            r"KeyError:",
            r"IndentationError:",
            r"NameError:",
            r"File \".*\", line \d+",
            r"streamlit.*error",
            r"WARNING:",
            r"CRITICAL:",
        ]

    def check_for_errors(self):
        """检查新的错误"""
        if not self.log_file.exists():
            return None

        current_size = self.log_file.stat().st_size
        if current_size <= self.last_size:
            return None

        # 读取新内容
        with open(self.log_file, 'r', encoding='utf-8') as f:
            f.seek(self.last_size)
            new_content = f.read()

        self.last_size = current_size

        # 检查是否有错误
        errors = []
        lines = new_content.split('\n')

        for i, line in enumerate(lines):
            for pattern in self.error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # 收集错误上下文
                    start = max(0, i-2)
                    end = min(len(lines), i+5)
                    context = '\n'.join(lines[start:end])
                    errors.append({
                        'line': line.strip(),
                        'context': context,
                        'timestamp': time.strftime('%H:%M:%S')
                    })
                    break

        return errors if errors else None

    def format_error_report(self, errors):
        """格式化错误报告"""
        report = f"🔥 发现 {len(errors)} 个错误！\n"
        report += "=" * 50 + "\n"

        for i, error in enumerate(errors, 1):
            report += f"\n错误 #{i} ({error['timestamp']}):\n"
            report += f"📍 {error['line']}\n"
            report += f"\n上下文:\n{error['context']}\n"
            report += "-" * 30 + "\n"

        return report

def main():
    print("🚀 启动智能错误监控...")
    print("💡 现在你只需要说 'Claude，看错误' 我就能立即分析！")
    print("🔄 监控文件: debug.log")
    print("⏹️  按 Ctrl+C 停止")

    monitor = ErrorMonitor()

    try:
        while True:
            errors = monitor.check_for_errors()
            if errors:
                report = monitor.format_error_report(errors)
                print(f"\n{report}")
                print("📢 Claude! 发现新错误，请分析 debug.log")

            time.sleep(2)  # 每2秒检查一次
    except KeyboardInterrupt:
        print("\n👋 错误监控已停止")

if __name__ == "__main__":
    main()