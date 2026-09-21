# -*- coding: utf-8 -*-
"""
CarLife 触控事件与实体按键发送器 (Channel 6)
依据源码位置：
- 触控事件封装与坐标映射：sources/com/baidu/carlife/sdk/receiver/view/RemoteDisplayGLView.java:220-225
- 实体按键：sources/d/b/a/a/o/h/e/b.java:1004 (425992)
"""

import threading
import logging
from typing import Optional
from ..protocol import constants, framing, proto_codec

logger = logging.getLogger("CarLife_TouchSender")

class TouchSender:
    def __init__(self, touch_socket, target_width: int = 1280, target_height: int = 720):
        self.touch_socket = touch_socket
        self.target_width = target_width
        self.target_height = target_height
        self._lock = threading.Lock()

    def set_target_resolution(self, width: int, height: int):
        self.target_width = width
        self.target_height = height

    def map_coordinates(self, view_x: float, view_y: float, view_w: float, view_h: float) -> tuple:
        """将 UI 窗口点击坐标等比映射到手机端车机协议分辨率坐标"""
        if view_w <= 0 or view_h <= 0:
            return 0, 0
        clamped_x = max(0.0, min(view_x, view_w))
        clamped_y = max(0.0, min(view_y, view_h))
        target_x = int((clamped_x / view_w) * self.target_width)
        target_y = int((clamped_y / view_h) * self.target_height)
        return target_x, target_y

    def send_touch(self, action: int, x: int, y: int, pointer_x: int = 0, pointer_y: int = 0):
        """
        依据 RemoteDisplayGLView.java:220 发送 MSG_TOUCH_ACTION (425985)
        - action: 0 (DOWN), 1 (UP), 2 (MOVE)
        """
        if not self.touch_socket:
            return

        touch_msg = proto_codec.CarlifeTouchAction(
            action=action,
            x=x,
            y=y,
            pointerx=pointer_x,
            pointery=pointer_y
        )
        payload = touch_msg.SerializeToString()
        packet = framing.pack_message(constants.CHANNEL_TOUCH, constants.MSG_TOUCH_ACTION, payload)

        with self._lock:
            try:
                self.touch_socket.sendall(packet)
            except Exception as e:
                logger.error(f"发送触控事件失败: {e}")

    def send_hardkey(self, keycode: int):
        """
        发送车机物理按键 (425992)
        - keycode: 1 (HOME), 2 (BACK) 等
        """
        if not self.touch_socket:
            return

        key_msg = proto_codec.CarlifeCarHardKeyCode(keycode=keycode)
        payload = key_msg.SerializeToString()
        packet = framing.pack_message(constants.CHANNEL_TOUCH, constants.MSG_HARD_KEY_CODE, payload)

        with self._lock:
            try:
                self.touch_socket.sendall(packet)
                logger.info(f"[按键] 发送车机硬按键: {keycode}")
            except Exception as e:
                logger.error(f"发送实体按键失败: {e}")
