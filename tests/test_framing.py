# -*- coding: utf-8 -*-
"""
协议封包与 Protobuf 编解码单元测试
"""

import unittest
import struct
import sys
import os

# 将上级目录加入路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from protocol import constants, framing, proto_codec
except ImportError:
    from carlife_pc_tool.protocol import constants, framing, proto_codec

class TestCarLifeProtocol(unittest.TestCase):
    def test_cmd_header_framing(self):
        """测试控制通道 8 字节包头大端序封包与解析"""
        cmd_id = constants.MSG_CMD_HU_PROTOCOL_VERSION
        payload = b"\x08\x04\x10\x00"
        packet = framing.pack_message(constants.CHANNEL_CMD, cmd_id, payload)
        
        self.assertEqual(len(packet), 8 + len(payload))
        # 验证大端序字节：0~1 长度, 2~3 保留, 4~7 命令ID
        payload_len, reserved, stype = struct.unpack(">HHI", packet[:8])
        self.assertEqual(payload_len, len(payload))
        self.assertEqual(reserved, 0)
        self.assertEqual(stype, cmd_id)
        
        unpacked_len, _, unpacked_stype = framing.unpack_header(constants.CHANNEL_CMD, packet[:8])
        self.assertEqual(unpacked_len, len(payload))
        self.assertEqual(unpacked_stype, cmd_id)

    def test_media_header_framing(self):
        """测试媒体通道 12 字节包头大端序封包与解析"""
        cmd_id = constants.MSG_VIDEO_DATA
        payload = b"FAKE_H264_NALU_DATA"
        timestamp = 12345678
        packet = framing.pack_message(constants.CHANNEL_VIDEO, cmd_id, payload, seq_or_ts=timestamp)
        
        self.assertEqual(len(packet), 12 + len(payload))
        payload_len, seq_ts, stype = struct.unpack(">III", packet[:12])
        self.assertEqual(payload_len, len(payload))
        self.assertEqual(seq_ts, timestamp)
        self.assertEqual(stype, cmd_id)

    def test_version_protobuf(self):
        """测试协议版本序列化与反序列化"""
        v = proto_codec.CarlifeProtocolVersion(majorVersion=4, minorVersion=0)
        data = v.SerializeToString()
        v2 = proto_codec.CarlifeProtocolVersion.FromString(data)
        self.assertEqual(v2.majorVersion, 4)
        self.assertEqual(v2.minorVersion, 0)

    def test_touch_action_protobuf(self):
        """测试触控消息序列化与反序列化"""
        touch = proto_codec.CarlifeTouchAction(
            action=constants.ACTION_DOWN,
            x=640,
            y=360,
            pointerx=0,
            pointery=0
        )
        data = touch.SerializeToString()
        touch2 = proto_codec.CarlifeTouchAction.FromString(data)
        self.assertEqual(touch2.action, constants.ACTION_DOWN)
        self.assertEqual(touch2.x, 640)
        self.assertEqual(touch2.y, 360)

    def test_video_encoder_info(self):
        """测试视频编码参数反序列化"""
        enc = proto_codec.CarlifeVideoEncoderInfo(width=1920, height=1080, frameRate=30)
        data = enc.SerializeToString()
        enc2 = proto_codec.CarlifeVideoEncoderInfo.FromString(data)
        self.assertEqual(enc2.width, 1920)
        self.assertEqual(enc2.height, 1080)
        self.assertEqual(enc2.frameRate, 30)

if __name__ == "__main__":
    unittest.main()
