# -*- coding: utf-8 -*-
"""
USB AOA 传输与 Connector 单元测试
"""

import unittest
import struct
import socket
import time
import sys
import os

# 将 tools 目录加入路径，以便识别 carlife_pc_tool 顶级包
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from carlife_pc_tool.transport.aoa_transport import (
    AoaManager, AoaTransportSession, ACCESSORY_STRINGS,
    AOA_VID, AOA_PIDS, AOA_GET_PROTOCOL, AOA_SEND_STRING, AOA_START_ACCESSORY
)
from carlife_pc_tool.transport.connector import CarLifeConnector
from carlife_pc_tool.protocol import constants

class TestAoaAndConnector(unittest.TestCase):

    def test_accessory_strings(self):
        """测试配件认证参数符合 accessory_filter.xml 规范"""
        self.assertEqual(ACCESSORY_STRINGS[0], "Baidu")
        self.assertEqual(ACCESSORY_STRINGS[1], "CarLife")
        self.assertEqual(ACCESSORY_STRINGS[3], "1.0.0")

    def test_aoa_constants(self):
        """测试 AOA 协议常量与 VID/PID 定义"""
        self.assertEqual(AOA_VID, 0x18D1)
        self.assertIn(0x2D00, AOA_PIDS)
        self.assertIn(0x2D01, AOA_PIDS)
        self.assertEqual(AOA_GET_PROTOCOL, 51)
        self.assertEqual(AOA_SEND_STRING, 52)
        self.assertEqual(AOA_START_ACCESSORY, 53)

    def test_aoa_header_format(self):
        """测试 AOA 8 字节多路复用头部编解码 (Channel ID 4B, Msg Len 4B, 大端序)"""
        channel_id = 1
        msg_len = 256
        header = struct.pack(">II", channel_id, msg_len)
        self.assertEqual(len(header), 8)

        unpacked_ch, unpacked_len = struct.unpack(">II", header)
        self.assertEqual(unpacked_ch, channel_id)
        self.assertEqual(unpacked_len, msg_len)

    def test_aoa_mock_session_routing(self):
        """测试 AoaTransportSession 的 SocketPair 双向多路复用与解复用路由"""
        class MockEndpoint:
            def __init__(self):
                self.bEndpointAddress = 0x81
                self.written_data = bytearray()
                self.read_queue = bytearray()

            def write(self, data, timeout=1000):
                self.written_data.extend(data)
                return len(data)

            def read(self, size, timeout=500):
                if not self.read_queue:
                    raise Exception("timed out")
                chunk = bytes(self.read_queue[:size])
                del self.read_queue[:size]
                return chunk

        ep_in = MockEndpoint()
        ep_out = MockEndpoint()

        session = AoaTransportSession(None, ep_in, ep_out)
        channel_ids = [constants.CHANNEL_CMD, constants.CHANNEL_VIDEO, constants.CHANNEL_TOUCH]
        client_sockets = session.start(channel_ids)

        self.assertIn(constants.CHANNEL_CMD, client_sockets)
        self.assertIn(constants.CHANNEL_VIDEO, client_sockets)
        self.assertIn(constants.CHANNEL_TOUCH, client_sockets)

        # 模拟 USB 接收：向 ep_in 塞入一段 Channel 1 的 AOA 报文
        test_payload = b"\x00\x04\x00\x00\x00\x00\x00\x01test" # 8B 头 + 4B 内容
        aoa_packet = struct.pack(">II", constants.CHANNEL_CMD, len(test_payload)) + test_payload
        ep_in.read_queue.extend(aoa_packet)

        # 验证 client_sock 能收到剥除 8B AOA 头后的原始载荷
        cmd_sock = client_sockets[constants.CHANNEL_CMD]
        cmd_sock.settimeout(1.0)
        received = cmd_sock.recv(len(test_payload))
        self.assertEqual(received, test_payload)

        # 模拟车端发送：向 client_sock 写入数据，验证 ep_out 收到附带 8B AOA 头的包
        touch_sock = client_sockets[constants.CHANNEL_TOUCH]
        touch_payload = b"TOUCH_EVENT_BYTES"
        touch_sock.sendall(touch_payload)

        # 等待发送线程转发
        time.sleep(0.1)
        self.assertGreaterEqual(len(ep_out.written_data), 8 + len(touch_payload))
        out_ch, out_len = struct.unpack(">II", ep_out.written_data[:8])
        self.assertEqual(out_ch, constants.CHANNEL_TOUCH)
        self.assertEqual(out_len, len(touch_payload))
        self.assertEqual(bytes(ep_out.written_data[8:8+out_len]), touch_payload)

        session.close()

    def test_lan_listener_lifecycle(self):
        """测试局域网监听器的启动与正常停止"""
        connector = CarLifeConnector()
        called = []
        connector.start_lan_discovery(lambda ip: called.append(ip))
        self.assertTrue(connector._udp_running)
        time.sleep(0.05)
        connector.stop_lan_discovery()
        time.sleep(0.05)
        self.assertFalse(connector._udp_running)

if __name__ == "__main__":
    unittest.main()
