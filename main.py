# -*- coding: utf-8 -*-
"""
CarLife PC 端车机模拟测试工具启动入口
Direction B: HeadUnit Simulator for Mobile CarLife Debugging
"""

import sys
import os
import logging
import faulthandler

# 开启 C 级段错误/崩溃追踪
faulthandler.enable()

def exception_hook(exctype, value, tb):
    logging.critical("未捕获的全局异常:", exc_info=(exctype, value, tb))
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook

# 将 tools 根目录加入 Python 模块搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
tools_root = os.path.abspath(os.path.join(current_dir, ".."))
if tools_root not in sys.path:
    sys.path.insert(0, tools_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from carlife_pc_tool.ui.main_window import MainWindow

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s][%(levelname)s][%(name)s]: %(message)s",
        datefmt="%H:%M:%S"
    )

def main():
    setup_logging()
    logger = logging.getLogger("CarLife_HU_Main")
    logger.info("正在启动 CarLife 电脑端车机模拟测试工具...")

    # 适配 Windows 高分屏缩放
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("CarLife_HU_Simulator")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
