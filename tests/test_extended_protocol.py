# -*- coding: utf-8 -*-
"""
扩展协议消息常量与 Protobuf 编解码单元测试
覆盖新增的车载传感器、多屏HUD订阅、蓝牙电话与鉴权协议。
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carlife_pc_tool.protocol import constants, proto_codec

class TestExtendedProtocol(unittest.TestCase):
    def test_constants_completeness(self):
        """测试所有关键通信消息常量ID与映射名称的完整性"""
        expected_constants = [
            (constants.MSG_CMD_HU_PROTOCOL_VERSION, 98305, "HU_PROTOCOL_VERSION"),
            (constants.MSG_CMD_PROTOCOL_VERSION_MATCH_STATUS, 65538, "PROTOCOL_VERSION_MATCH_STATUS"),
            (constants.MSG_CMD_HU_INFO, 98307, "HU_INFO"),
            (constants.MSG_CMD_MD_INFO, 65540, "MD_INFO"),
            (constants.MSG_CMD_HU_BT_OOB_INFO, 98309, "HU_BT_OOB_INFO"),
            (constants.MSG_CMD_MD_BT_OOB_INFO, 65542, "MD_BT_OOB_INFO"),
            (constants.MSG_CMD_VIDEO_ENCODER_FRAME_RATE_CHANGE, 98316, "VIDEO_ENCODER_FRAME_RATE_CHANGE"),
            (constants.MSG_CMD_VIDEO_ENCODER_FRAME_RATE_CHANGE_DONE, 65549, "VIDEO_ENCODER_FRAME_RATE_CHANGE_DONE"),
            (constants.MSG_CMD_SCREEN_ON, 65560, "SCREEN_ON"),
            (constants.MSG_CMD_SCREEN_OFF, 65561, "SCREEN_OFF"),
            (constants.MSG_CMD_SCREEN_USERPRESENT, 65562, "SCREEN_USERPRESENT"),
            (constants.MSG_CMD_FOREGROUND, 65563, "FOREGROUND"),
            (constants.MSG_CMD_BACKGROUND, 65564, "BACKGROUND"),
            (constants.MSG_CMD_GO_TO_DESKTOP, 65569, "GO_TO_DESKTOP"),
            (constants.MSG_CMD_GO_TO_FOREGROUND, 98341, "GO_TO_FOREGROUND"),
            (constants.MSG_CMD_LAUNCH_MODE_NORMAL, 98333, "LAUNCH_MODE_NORMAL"),
            (constants.MSG_CMD_LAUNCH_MODE_PHONE, 98334, "LAUNCH_MODE_PHONE"),
            (constants.MSG_CMD_LAUNCH_MODE_MAP, 98335, "LAUNCH_MODE_MAP"),
            (constants.MSG_CMD_LAUNCH_MODE_MUSIC, 98336, "LAUNCH_MODE_MUSIC"),
            (constants.MSG_CMD_MIC_RECORD_WAKEUP_START, 65570, "MIC_RECORD_WAKEUP_START"),
            (constants.MSG_CMD_MIC_RECORD_END, 65571, "MIC_RECORD_END"),
            (constants.MSG_CMD_MIC_RECORD_RECOG_START, 65572, "MIC_RECORD_RECOG_START"),
            (constants.MSG_CMD_MODULE_STATUS, 65574, "MODULE_STATUS"),
            (constants.MSG_CMD_MODULE_CONTROL, 98344, "MODULE_CONTROL"),
            (constants.MSG_CMD_NAVI_NEXT_TURN_INFO, 65584, "NAVI_NEXT_TURN_INFO"),
            (constants.MSG_CMD_NAVI_ASSITANTGUIDE_INFO, 65607, "NAVI_ASSITANTGUIDE_INFO"),
            (constants.MSG_CMD_CAR_DATA_SUBSCRIBE, 65585, "CAR_DATA_SUBSCRIBE"),
            (constants.MSG_CMD_CAR_DATA_SUBSCRIBE_DONE, 98354, "CAR_DATA_SUBSCRIBE_DONE"),
            (constants.MSG_CMD_MEDIA_INFO, 65589, "MEDIA_INFO"),
            (constants.MSG_CMD_MEDIA_PROGRESS_BAR, 65590, "MEDIA_PROGRESS_BAR"),
            (constants.MSG_CMD_BT_HFP_REQUEST, 65600, "BT_HFP_REQUEST"),
            (constants.MSG_CMD_BT_HFP_INDICATION, 98369, "BT_HFP_INDICATION"),
            (constants.MSG_CMD_BT_HFP_CONNECTION, 98370, "BT_HFP_CONNECTION"),
            (constants.MSG_CMD_BT_HFP_RESPONSE, 98382, "BT_HFP_RESPONSE"),
            (constants.MSG_CMD_CARLIFE_DATA_SUBSCRIBE, 98371, "CARLIFE_DATA_SUBSCRIBE"),
            (constants.MSG_CMD_CARLIFE_DATA_SUBSCRIBE_DONE, 65604, "CARLIFE_DATA_SUBSCRIBE_DONE"),
            (constants.MSG_CMD_CARLIFE_DATA_SUBSCRIBE_START, 98373, "CARLIFE_DATA_SUBSCRIBE_START"),
            (constants.MSG_CMD_CARLIFE_DATA_SUBSCRIBE_STOP, 98374, "CARLIFE_DATA_SUBSCRIBE_STOP"),
            (constants.MSG_CMD_HU_AUTHEN_REQUEST, 98376, "HU_AUTHEN_REQUEST"),
            (constants.MSG_CMD_MD_AUTHEN_RESPONSE, 65609, "MD_AUTHEN_RESPONSE"),
            (constants.MSG_CMD_HU_AUTHEN_RESULT, 98378, "HU_AUTHEN_RESULT"),
            (constants.MSG_CMD_MD_AUTHEN_RESULT, 65611, "MD_AUTHEN_RESULT"),
            (constants.MSG_MEDIA_INIT, 196609, "MEDIA_INIT"),
            (constants.MSG_MEDIA_STOP, 196610, "MEDIA_STOP"),
            (constants.MSG_MEDIA_PAUSE, 196611, "MEDIA_PAUSE"),
            (constants.MSG_MEDIA_RESUME_PLAY, 196612, "MEDIA_RESUME_PLAY"),
            (constants.MSG_MEDIA_DATA, 196614, "MEDIA_DATA"),
            (constants.MSG_NAVI_TTS_INIT, 262145, "NAVI_TTS_INIT"),
            (constants.MSG_NAVI_TTS_END, 262146, "NAVI_TTS_END"),
            (constants.MSG_NAVI_TTS_DATA, 262147, "NAVI_TTS_DATA"),
            (constants.MSG_VR_DATA, 360449, "VR_DATA"),
            (constants.MSG_VR_AUDIO_INIT, 327682, "VR_AUDIO_INIT"),
            (constants.MSG_VR_AUDIO_DATA, 327683, "VR_AUDIO_DATA"),
            (constants.MSG_VR_AUDIO_STOP, 327684, "VR_AUDIO_STOP"),
            (constants.MSG_TOUCH_ACTION, 425985, "TOUCH_ACTION"),
            (constants.MSG_TOUCH_CAR_HARD_KEY_CODE, 425992, "TOUCH_CAR_HARD_KEY_CODE"),
        ]

        for const_val, expected_val, expected_name in expected_constants:
            self.assertEqual(const_val, expected_val, f"Constant value mismatch for {expected_name}")
            self.assertIn(const_val, constants.MSG_NAMES, f"Constant {expected_name} missing from MSG_NAMES")
            self.assertEqual(constants.MSG_NAMES[const_val], expected_name)

    def test_vehicle_sensors_codec(self):
        """测试车辆传感器数据 Protobuf 编解码"""
        # GPS
        gps = proto_codec.CarlifeCarGps(
            antennaState=1,
            signalQuality=3,
            latitude=39908700,
            longitude=116397500,
            height=50,
            speed=72,
            heading=180,
            year=2026,
            month=10,
            day=16,
            hrs=11,
            min=5,
            sec=30,
            fix=1,
            satsUsed=12,
            timeStamp=1700000000
        )
        gps_decoded = proto_codec.CarlifeCarGps.FromString(gps.SerializeToString())
        self.assertEqual(gps_decoded.latitude, 39908700)
        self.assertEqual(gps_decoded.speed, 72)
        self.assertEqual(gps_decoded.satsUsed, 12)

        # Gyroscope
        gyro = proto_codec.CarlifeGyroscope(gyroType=1, gyroX=0.12, gyroy=-0.05, gyroZ=0.88, timeStamp=1000)
        gyro_decoded = proto_codec.CarlifeGyroscope.FromString(gyro.SerializeToString())
        self.assertAlmostEqual(gyro_decoded.gyroX, 0.12)
        self.assertAlmostEqual(gyro_decoded.gyroy, -0.05)

        # Acceleration
        acc = proto_codec.CarlifeAcceleration(accX=0.01, accY=0.02, accZ=9.8, timeStamp=2000)
        acc_decoded = proto_codec.CarlifeAcceleration.FromString(acc.SerializeToString())
        self.assertAlmostEqual(acc_decoded.accZ, 9.8)

        # Gear & Oil
        gear = proto_codec.CarlifeGearInfo(gear=3)
        self.assertEqual(proto_codec.CarlifeGearInfo.FromString(gear.SerializeToString()).gear, 3)

        oil = proto_codec.CarlifeOil(level=65, range=450, lowFuleWarning=False)
        oil_decoded = proto_codec.CarlifeOil.FromString(oil.SerializeToString())
        self.assertEqual(oil_decoded.level, 65)
        self.assertEqual(oil_decoded.range, 450)
        self.assertFalse(oil_decoded.lowFuleWarning)

    def test_navi_assistant_and_hud_codec(self):
        """测试电子狗巡航辅助诱导与多屏订阅列表"""
        # CarlifeNaviAssitantGuideInfo
        guide = proto_codec.CarlifeNaviAssitantGuideInfo(
            action=1,
            assistantType=2,
            trafficSignType=5,
            totalDistance=1000,
            remainDistance=350,
            cameraSpeed=60
        )
        guide_decoded = proto_codec.CarlifeNaviAssitantGuideInfo.FromString(guide.SerializeToString())
        self.assertEqual(guide_decoded.assistantType, 2)
        self.assertEqual(guide_decoded.cameraSpeed, 60)
        self.assertEqual(guide_decoded.remainDistance, 350)

        # CarlifeSubscribeMobileCarLifeInfoList
        sub_list = proto_codec.CarlifeSubscribeMobileCarLifeInfoList(cnt=2)
        s1 = sub_list.subscribemobileCarLifeInfo.add()
        s1.moduleID = 2  # NAVI
        s1.supportFlag = True
        s1.frequency = 1
        s2 = sub_list.subscribemobileCarLifeInfo.add()
        s2.moduleID = 8  # EDOG
        s2.supportFlag = True
        s2.frequency = 1
        sub_decoded = proto_codec.CarlifeSubscribeMobileCarLifeInfoList.FromString(sub_list.SerializeToString())
        self.assertEqual(sub_decoded.cnt, 2)
        self.assertEqual(len(sub_decoded.subscribemobileCarLifeInfo), 2)
        self.assertEqual(sub_decoded.subscribemobileCarLifeInfo[1].moduleID, 8)

    def test_bt_hfp_and_audio_codec(self):
        """测试蓝牙电话协议族与 TTS 音频初始化"""
        # HFP Request
        req = proto_codec.CarlifeBTHfpRequest(command=1, phoneNum="13800138000", dtmfCode=0)
        req_decoded = proto_codec.CarlifeBTHfpRequest.FromString(req.SerializeToString())
        self.assertEqual(req_decoded.phoneNum, "13800138000")

        # HFP Indication
        ind = proto_codec.CarlifeBTHfpIndication(state=2, phoneNum="10086", phoneName="中国移动", address="00:11:22:33:44:55")
        ind_decoded = proto_codec.CarlifeBTHfpIndication.FromString(ind.SerializeToString())
        self.assertEqual(ind_decoded.phoneName, "中国移动")
        self.assertEqual(ind_decoded.address, "00:11:22:33:44:55")

        # TTS Init
        tts = proto_codec.CarlifeTTSInit(sampleRate=16000, channelConfig=1, sampleFormat=16)
        tts_decoded = proto_codec.CarlifeTTSInit.FromString(tts.SerializeToString())
        self.assertEqual(tts_decoded.sampleRate, 16000)
        self.assertEqual(tts_decoded.sampleFormat, 16)

if __name__ == "__main__":
    unittest.main()
