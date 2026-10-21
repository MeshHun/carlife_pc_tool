# -*- coding: utf-8 -*-
import sys
import os
import unittest
from unittest.mock import MagicMock

# 确保父目录被加入以支持相对包导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPointF
from carlife_pc_tool.ui.main_window import VideoDisplayWidget
from carlife_pc_tool.protocol import constants

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

class TestVideoDisplayWidgetTouch(unittest.TestCase):
    def setUp(self):
        self.widget = VideoDisplayWidget()
        self.widget.resize(800, 600)
        self.widget.is_connected = True
        
        self.mock_sender = MagicMock()
        self.mock_sender.target_width = 1280
        self.mock_sender.target_height = 720
        self.widget.set_touch_sender(self.mock_sender)

    def _create_mouse_event(self, event_type, x, y, button=Qt.MouseButton.LeftButton, buttons=Qt.MouseButton.LeftButton):
        pos = QPointF(float(x), float(y))
        return QtGui.QMouseEvent(
            event_type,
            pos,
            pos,
            button,
            buttons,
            Qt.KeyboardModifier.NoModifier
        )

    def test_press_inside_render_area(self):
        # 800x600 控件内，1280x720 比例为 16:9
        # scale = min(800/1280, 600/720) = min(0.625, 0.8333) = 0.625
        # disp_w = 800, disp_h = 450, offset_x = 0, offset_y = 75
        # 有效渲染区域：x 在 [0, 800], y 在 [75, 525]
        offset_x, offset_y, disp_w, disp_h, tw, th = self.widget._calc_render_metrics()
        self.assertEqual((disp_w, disp_h), (800, 450))
        self.assertEqual((offset_x, offset_y), (0, 75))

        # 在中心按下 (400, 300)
        event = self._create_mouse_event(QtCore.QEvent.Type.MouseButtonPress, 400, 300)
        self.widget.mousePressEvent(event)

        self.assertTrue(self.widget._is_touching)
        self.mock_sender.send_touch.assert_called_once_with(constants.ACTION_DOWN, 640, 360)

    def test_press_outside_render_area(self):
        # 在顶部黑边按下 (400, 20)
        event = self._create_mouse_event(QtCore.QEvent.Type.MouseButtonPress, 400, 20)
        self.widget.mousePressEvent(event)

        self.assertFalse(self.widget._is_touching)
        self.mock_sender.send_touch.assert_not_called()

    def test_drag_move_and_exit_boundary(self):
        # 1. 在有效区域按下
        press_event = self._create_mouse_event(QtCore.QEvent.Type.MouseButtonPress, 400, 300)
        self.widget.mousePressEvent(press_event)
        self.assertTrue(self.widget._is_touching)
        self.mock_sender.send_touch.assert_called_with(constants.ACTION_DOWN, 640, 360)

        # 2. 正常在有效区域内移动到 (400, 400)
        # rel_y = 400 - 75 = 325, car_y = int((325/450)*720) = 520
        move_event1 = self._create_mouse_event(QtCore.QEvent.Type.MouseMove, 400, 400)
        self.widget.mouseMoveEvent(move_event1)
        self.assertTrue(self.widget._is_touching)
        self.mock_sender.send_touch.assert_called_with(constants.ACTION_MOVE, 640, 520)

        # 3. 拖动移出渲染区域底部 (400, 550) -> offset_y + disp_h = 525，超出边界
        move_event_out = self._create_mouse_event(QtCore.QEvent.Type.MouseMove, 400, 550)
        self.widget.mouseMoveEvent(move_event_out)

        # 应该直接发送 ACTION_UP，并在边界处释放，同时触控状态重置为 False
        self.mock_sender.send_touch.assert_called_with(constants.ACTION_UP, 640, 720)
        self.assertFalse(self.widget._is_touching)

        # 4. 移出后继续拖动，不应再发送任何事件
        self.mock_sender.reset_mock()
        move_event_out2 = self._create_mouse_event(QtCore.QEvent.Type.MouseMove, 400, 580)
        self.widget.mouseMoveEvent(move_event_out2)
        self.mock_sender.send_touch.assert_not_called()

        # 5. 在外部松开鼠标，不应重复发送 ACTION_UP
        release_event = self._create_mouse_event(QtCore.QEvent.Type.MouseButtonRelease, 400, 580, button=Qt.MouseButton.LeftButton, buttons=Qt.MouseButton.NoButton)
        self.widget.mouseReleaseEvent(release_event)
        self.mock_sender.send_touch.assert_not_called()

    def test_release_inside_render_area(self):
        # 1. 有效区域按下
        press_event = self._create_mouse_event(QtCore.QEvent.Type.MouseButtonPress, 400, 300)
        self.widget.mousePressEvent(press_event)
        self.assertTrue(self.widget._is_touching)

        # 2. 有效区域松开
        release_event = self._create_mouse_event(QtCore.QEvent.Type.MouseButtonRelease, 400, 300, button=Qt.MouseButton.LeftButton, buttons=Qt.MouseButton.NoButton)
        self.widget.mouseReleaseEvent(release_event)
        self.mock_sender.send_touch.assert_called_with(constants.ACTION_UP, 640, 360)
        self.assertFalse(self.widget._is_touching)

if __name__ == '__main__':
    unittest.main()

