# -*- coding: utf-8 -*-
"""
CarLife 握手状态机端到端模拟测试
模拟手机端 Server 与车机端 Client 在 Channel 1 上的完整握手时序交互。
"""

import unittest
import socket
import threading
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from carlife_pc_hu.protocol import constants, framing, proto_codec
from carlife_pc_hu.core.state_machine import CarLifeStateMachine, HandshakeState

class TestCarLifeStateMachine(unittest.TestCase):
    def setUp(self):
        # 创建本地模拟服务端 (模拟手机端 Channel 1)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(("127.0.0.1", 0))
        self.server_port = self.server_sock.getsockname()[1]
        self.server_sock.listen(1)

        self.client_sock = None
        self.phone_conn = None
        self.state_machine = None
        self.states_recorded = []

    def tearDown(self):
        if self.state_machine:
            self.state_machine.stop()
        if self.client_sock:
            self.client_sock.close()
        if self.phone_conn:
            self.phone_conn.close()
        self.server_sock.close()

    def test_full_handshake_flow(self):
        """测试完整的握手时序流程"""
        # 1. 启动模拟手机端服务线程
        def _mock_phone_service():
            conn, _ = self.server_sock.accept()
            self.phone_conn = conn
            
            # Step 1: 接收车机发送的 98305 (HU_PROTOCOL_VERSION)
            stype, payload = framing.read_message(conn, constants.CHANNEL_CMD)
            self.assertEqual(stype, constants.MSG_CMD_HU_PROTOCOL_VERSION)
            ver = proto_codec.CarlifeProtocolVersion.FromString(payload)
            self.assertEqual(ver.majorVersion, 4)

            # Step 2: 手机回复 65538 (MD_PROTOCOL_VERSION_MATCH_STATUS)
            status = proto_codec.CarlifeProtocolVersionMatchStatus(matchStatus=1, carlifeProtocolVersion=4)
            conn.sendall(framing.pack_message(constants.CHANNEL_CMD, constants.MSG_CMD_MD_PROTOCOL_VERSION_MATCH_STATUS, status.SerializeToString()))

            # Step 3: 接收车机发送的 98343 (HU_STATISTICAL_INFO)
            stype, payload = framing.read_message(conn, constants.CHANNEL_CMD)
            self.assertEqual(stype, constants.MSG_CMD_HU_STATISTICAL_INFO)

            # Step 4: 手机发送 65540 (MD_INFO)
            md_info = proto_codec.CarlifeDeviceInfo(brand="Xiaomi", model="Mi13", release="Android 14")
            conn.sendall(framing.pack_message(constants.CHANNEL_CMD, constants.MSG_CMD_MD_INFO, md_info.SerializeToString()))

            # Step 5: 接收车机回复的 98307 (HU_INFO)
            stype, payload = framing.read_message(conn, constants.CHANNEL_CMD)
            self.assertEqual(stype, constants.MSG_CMD_HU_INFO)
            hu_info = proto_codec.CarlifeDeviceInfo.FromString(payload)
            self.assertEqual(hu_info.brand, "baidu")
            self.assertEqual(hu_info.os, "Android")

            # Step 6: 手机发送 65611 (MD_AUTHEN_RESULT)
            auth = proto_codec.CarlifeAuthenResult(authenResult=True)
            conn.sendall(framing.pack_message(constants.CHANNEL_CMD, constants.MSG_CMD_MD_AUTHEN_RESULT, auth.SerializeToString()))

            # Step 7: 接收车机确认 98380 (HU_AUTHEN_RESULT)
            stype, payload = framing.read_message(conn, constants.CHANNEL_CMD)
            self.assertEqual(stype, constants.MSG_CMD_HU_AUTHEN_RESULT)

            # Step 8: 接收车机主动发送的 98311 (HU_VIDEO_ENCODER_INIT)
            stype, payload = framing.read_message(conn, constants.CHANNEL_CMD)
            self.assertEqual(stype, constants.MSG_CMD_HU_VIDEO_ENCODER_INIT)

            # Step 9: 手机发送 65544 (VIDEO_ENCODER_INIT)
            enc = proto_codec.CarlifeVideoEncoderInfo(width=1920, height=1080, frameRate=30)
            conn.sendall(framing.pack_message(constants.CHANNEL_CMD, constants.MSG_CMD_VIDEO_ENCODER_INIT, enc.SerializeToString()))

            # Step 10: 接收车机确认开始推流 98313 (VIDEO_ENCODER_START)
            stype, payload = framing.read_message(conn, constants.CHANNEL_CMD)
            self.assertEqual(stype, constants.MSG_CMD_VIDEO_ENCODER_START)

        phone_thread = threading.Thread(target=_mock_phone_service, daemon=True)
        phone_thread.start()

        # 2. 车机客户端连接模拟手机
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect(("127.0.0.1", self.server_port))

        video_ready_event = threading.Event()
        def _on_video_ready(w, h, fps):
            self.assertEqual(w, 1920)
            self.assertEqual(h, 1080)
            video_ready_event.set()

        # 3. 启动状态机
        self.state_machine = CarLifeStateMachine(
            cmd_socket=self.client_sock,
            on_state_change=lambda st: self.states_recorded.append(st),
            on_video_ready=_on_video_ready
        )
        self.state_machine.start()

        # 等待握手完成并收到视频启动信号
        phone_thread.join(timeout=3.0)
        self.assertTrue(video_ready_event.wait(timeout=2.0))
        self.assertEqual(self.state_machine.state, HandshakeState.CONNECTED)
        self.assertIn(HandshakeState.VERSION_NEGOTIATING, self.states_recorded)
        self.assertIn(HandshakeState.CONNECTED, self.states_recorded)

if __name__ == "__main__":
    unittest.main()
