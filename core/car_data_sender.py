# -*- coding: utf-8 -*-
"""
CarLife 车辆传感器与车况数据模拟器 (Channel 7)
依据源码位置：
- 车速与GPS定义：sources/d/b/a/a/o/h/e/b.java:1018-1019
"""

import time
import threading
import logging
from ..protocol import constants, framing, proto_codec

logger = logging.getLogger("CarLife_CarDataSender")

class CarDataSender:
    def __init__(self, data_socket):
        self.data_socket = data_socket
        self._lock = threading.Lock()

    def send_speed(self, speed_kmh: int):
        """发送实时车速 (98322)"""
        if not self.data_socket:
            return

        speed_msg = proto_codec.CarlifeCarSpeed(
            speed=speed_kmh,
            timeStamp=int(time.time() * 1000)
        )
        payload = speed_msg.SerializeToString()
        packet = framing.pack_message(constants.CHANNEL_DATA, constants.MSG_CAR_SPEED, payload)

        with self._lock:
            try:
                self.data_socket.sendall(packet)
                logger.debug(f"[车况] 发送模拟车速: {speed_kmh} km/h")
            except Exception as e:
                logger.error(f"发送车速数据失败: {e}")
