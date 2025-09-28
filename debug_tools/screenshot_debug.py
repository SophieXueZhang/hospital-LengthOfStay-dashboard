#!/usr/bin/env python3
"""
自动截图调试系统
Claude Code可以看到你看到的一切错误
"""

import subprocess
import time
from datetime import datetime
import os

class ScreenshotDebugger:
    def __init__(self):
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def take_screenshot(self, description="debug"):
        """截取当前屏幕"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{description}_{timestamp}.png"
        filepath = f"{self.screenshots_dir}/{filename}"

        # macOS截图命令
        result = subprocess.run([
            "screencapture",
            "-x",  # 不播放声音
            "-t", "png",
            filepath
        ], capture_output=True)

        if result.returncode == 0:
            print(f"📸 截图已保存: {filepath}")
            print(f"🤖 现在你可以说: 'Claude，分析截图 {filename}'")
            return filepath
        else:
            print("❌ 截图失败")
            return None

    def take_browser_screenshot(self):
        """专门截取浏览器窗口（如果支持）"""
        return self.take_screenshot("browser_error")

    def auto_screenshot_on_error(self):
        """当检测到错误时自动截图"""
        print("🔍 监控错误并自动截图...")
        print("💡 当检测到错误时会自动截图")
        print("📱 你也可以按任意键手动截图")

        try:
            while True:
                # 简单的手动触发
                input("\n按回车键截图调试 (Ctrl+C 退出): ")
                screenshot_path = self.take_screenshot("manual_debug")
                if screenshot_path:
                    print(f"✅ 截图完成！")
                    print(f"💬 现在说: 'Claude，分析这个截图错误'")

        except KeyboardInterrupt:
            print("\n👋 截图调试已停止")

def main():
    print("🚀 启动截图调试系统")
    print("=" * 40)

    debugger = ScreenshotDebugger()

    print("选择模式:")
    print("1. 立即截图")
    print("2. 手动触发模式")
    print("3. 只截取浏览器")

    choice = input("\n请选择 (1-3): ").strip()

    if choice == "1":
        debugger.take_screenshot("immediate")
    elif choice == "2":
        debugger.auto_screenshot_on_error()
    elif choice == "3":
        debugger.take_browser_screenshot()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()