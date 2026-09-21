# -*- coding: utf-8 -*-
"""
CarLife 握手与控制状态机 (Channel 1)
依据源码位置：
- 握手时序与心跳：sources/d/b/a/a/p/m/a/c.java:58-133
- 统计与设备信息：sources/d/b/a/a/p/h.java:52
- 特征协商与配置：sources/d/b/a/a/p/m/a/f.java:39-81
- 视频启动应答：sources/d/b/a/a/p/k/b.java:43-98
"""

import threading
import time
import logging
from typing import Optional, Callable
from ..protocol import constants, framing, proto_codec

logger = logging.getLogger("CarLife_StateMachine")

class HandshakeState:
    DISCONNECTED = "未连接"
    CONNECTING = "连接中"
    VERSION_NEGOTIATING = "版本协商中"
    DEVICE_INFO_EXCHANGING = "交换设备信息"
    AUTHEN_CONFIRMING = "鉴权确认中"
    CONFIG_EXCHANGING = "特征配置协商"
    VIDEO_PREPARING = "视频流准备中"
    CONNECTED = "已连接并推流"

class CarLifeStateMachine:
    def __init__(self, cmd_socket, on_state_change: Optional[Callable[[str], None]] = None,
                 on_log: Optional[Callable[[str, int, bytes], None]] = None,
                 on_video_ready: Optional[Callable[[int, int, int], None]] = None):
        self.cmd_socket = cmd_socket
        self.on_state_change = on_state_change
        self.on_log = on_log
        self.on_video_ready = on_video_ready

        self.state = HandshakeState.DISCONNECTED
        self.is_running = False
        self.last_heartbeat_time = 0.0
        self._reader_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None

        # 手机端与视频端信息
        self.phone_device_info = None
        self.video_width = 1280
        self.video_height = 720
        self.video_fps = 30

    def set_state(self, new_state: str):
        self.state = new_state
        logger.info(f"状态切换 -> {new_state}")
        if self.on_state_change:
            self.on_state_change(new_state)

    def start(self):
        """连接建立后启动控制通道读线程并主动发起握手"""
        self.is_running = True
        self._reader_thread = threading.Thread(target=self._cmd_reader_loop, daemon=True, name="CarLife_CmdReader")
        self._reader_thread.start()

        # 依据 sources/d/b/a/a/p/m/a/c.java:126 onConnectionAttached
        # 车机主动向手机发送 MSG_CMD_HU_PROTOCOL_VERSION (98305)
        self.send_protocol_version()

    def stop(self):
        self.is_running = False
        self.set_state(HandshakeState.DISCONNECTED)

    def send_cmd(self, service_type: int, payload: bytes = b""):
        """向 Channel 1 发送控制消息"""
        try:
            packet = framing.pack_message(constants.CHANNEL_CMD, service_type, payload)
            self.cmd_socket.sendall(packet)
            msg_name = constants.MSG_NAMES.get(service_type, f"UNKNOWN_0x{service_type:08X}")
            logger.debug(f"[TX CMD] {msg_name} (ID: {service_type}, len: {len(payload)})")
            if self.on_log:
                self.on_log(f"-> 发送: {msg_name}", service_type, payload)
        except Exception as e:
            logger.error(f"发送信令失败 (type {service_type}): {e}")
            self.stop()

    def send_protocol_version(self):
        """发送协议版本协商 (98305)"""
        self.set_state(HandshakeState.VERSION_NEGOTIATING)
        ver = proto_codec.CarlifeProtocolVersion(majorVersion=4, minorVersion=0)
        self.send_cmd(constants.MSG_CMD_HU_PROTOCOL_VERSION, ver.SerializeToString())

    def send_statistics_info(self):
        """
        发送车机统计信息 (98343)
        依据 sources/d/b/a/a/p/h.java:52 与 sources/com/baidu/carlifevehiclef/VehicleApplication.java:124-125
        """
        stat = proto_codec.CarlifeStatisticsInfo(
            channel="20029999",  # 原生百度车机通用公开测试渠道号 (VehicleApplication.java:124)
            cuid="12345678",      # 原生车机固定 CUID (VehicleApplication.java:125)
            versionCode=16,       # AndroidManifest.xml:3
            versionName="4.0.0",  # AndroidManifest.xml:4
            connectCount=0,
            connectSuccessCount=0,
            connectTime=0,
            crashCycle=""
        )
        self.send_cmd(constants.MSG_CMD_HU_STATISTICAL_INFO, stat.SerializeToString())

    def send_hu_device_info(self):
        """
        发送车机设备硬件与系统信息 (98307)
        依据 sources/d/b/a/a/p/m/a/c.java:91 与 sources/d/b/a/a/o/c.java:368
        严禁使用 Windows 等非移动端标识，必须伪装为原生 Android 车机平台
        """
        dev = proto_codec.CarlifeDeviceInfo(
            os="Android",         # 原生车机 cVar.e0() 返回固定为 "Android" (c.java:368)
            board="universal",
            bootloader="unknown",
            brand="baidu",        # 原生默认 brand (c.java:91)
            cpuAbi="arm64-v8a",
            cpuAbi2="armeabi-v7a",
            device="carlife",
            display=f"{self.video_width}x{self.video_height}",
            fingerprint="baidu/carlife/carlife:11/RQ3A.211001.001/1:user/release-keys",
            hardware="universal",
            host="carlife-build",
            cid="RQ3A.211001.001",
            manufacturer="baidu",
            model="CarLifeVehicle",
            product="carlife",
            serial="unknown",
            codename="REL",
            incremental="1",
            sdk="30",
            sdkInt=30,
            release="11",
            carlifeversion="4.0.0"
        )
        self.send_cmd(constants.MSG_CMD_HU_INFO, dev.SerializeToString())

    def send_video_encoder_init(self):
        """
        发送车机视频编码初始化参数 (98311)
        依据 sources/d/b/a/a/p/k/b.java:132-136
        通知手机当前车机显示器的宽、高与期望帧率
        """
        enc = proto_codec.CarlifeVideoEncoderInfo(
            width=self.video_width,
            height=self.video_height,
            frameRate=self.video_fps
        )
        self.send_cmd(constants.MSG_CMD_HU_VIDEO_ENCODER_INIT, enc.SerializeToString())

    def send_video_encoder_start(self):
        """发送视频编码器启动指令 (98313，依据 sources/d/b/a/a/p/k/b.java:90)"""
        self.send_cmd(constants.MSG_CMD_VIDEO_ENCODER_START)

    def _start_heartbeat(self):
        """依据 sources/d/b/a/a/p/m/a/c.java:44-55 启动 1000ms 心跳保活守护线程"""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return

        def _hb_loop():
            logger.info("[*] 心跳保活线程启动 (周期 1000ms)...")
            while self.is_running:
                time.sleep(1.0)
                if not self.is_running:
                    break
                # 发送 MSG_CMD_HU_HEARTBEAT (131074)
                self.send_cmd(constants.MSG_CMD_HU_HEARTBEAT)

        self._heartbeat_thread = threading.Thread(target=_hb_loop, daemon=True, name="CarLife_Heartbeat")
        self._heartbeat_thread.start()

    def _cmd_reader_loop(self):
        """Channel 1 接收与状态机处理循环"""
        logger.info("[*] 控制通道监听线程已启动")
        while self.is_running:
            msg = framing.read_message(self.cmd_socket, constants.CHANNEL_CMD)
            if msg is None:
                logger.warning("控制通道连接断开")
                self.stop()
                break

            service_type, payload = msg
            msg_name = constants.MSG_NAMES.get(service_type, f"UNKNOWN_0x{service_type:08X}")
            logger.debug(f"[RX CMD] {msg_name} (ID: {service_type}, len: {len(payload)})")
            if self.on_log:
                self.on_log(f"<- 收到: {msg_name}", service_type, payload)

            self._handle_message(service_type, payload)

    def _handle_message(self, service_type: int, payload: bytes):
        """依据源码状态机处理具体信令"""
        # 1. 收到版本匹配状态 (65538)
        if service_type == constants.MSG_CMD_MD_PROTOCOL_VERSION_MATCH_STATUS:
            status = proto_codec.CarlifeProtocolVersionMatchStatus.FromString(payload)
            logger.info(f"[握手] 手机版本匹配结果: matchStatus={status.matchStatus}, ver={status.carlifeProtocolVersion}")
            if status.matchStatus == 1:
                # 依据 c.java:81 发送统计信息，并启动心跳
                self.send_statistics_info()
                self._start_heartbeat()
                self.set_state(HandshakeState.DEVICE_INFO_EXCHANGING)

        # 2. 收到手机设备信息 (65540)
        elif service_type == constants.MSG_CMD_MD_INFO:
            self.phone_device_info = proto_codec.CarlifeDeviceInfo.FromString(payload)
            logger.info(f"[设备信息] 手机品牌: {self.phone_device_info.brand}, 型号: {self.phone_device_info.model}, OS: {self.phone_device_info.release}")
            # 依据 c.java:90 回复车端设备信息
            self.send_hu_device_info()
            self.set_state(HandshakeState.AUTHEN_CONFIRMING)

        # 3. 收到鉴权结果 (65611)
        elif service_type == constants.MSG_CMD_MD_AUTHEN_RESULT:
            auth = proto_codec.CarlifeAuthenResult.FromString(payload)
            logger.info(f"[鉴权] 手机端鉴权结果: {auth.authenResult}")
            # 依据 sources/d/b/a/a/p/m/a/c.java:94 车端先回复 98380 确认
            self.send_cmd(constants.MSG_CMD_HU_AUTHEN_RESULT)
            self.set_state(HandshakeState.CONFIG_EXCHANGING)

            # 依据 sources/d/b/a/a/p/m/a/c.java:100 与 sources/d/b/a/a/p/k/b.java:170-176:
            # 鉴权后车机必须主动向手机发送 98311 (HU_VIDEO_ENCODER_INIT)，促使手机启动视频协商
            self.send_video_encoder_init()

        # 4. 收到特征配置列表 (65617)
        elif service_type == constants.MSG_CMD_MD_FEATURE_CONFIG_LIST:
            # 依据 sources/d/b/a/a/p/m/a/f.java:69-80 回复车机支持的特征
            fc_list = proto_codec.CarlifeFeatureConfigList()
            fc_list.cnt = 3
            fc_list.huBtAudioSupport = False
            fc_list.huBtName = "CarLife_PC"
            fc_list.huBtMAC = "00:11:22:33:44:55"

            # 注入原生默认 Feature 配置 (VehicleApplication.java:120)
            f1 = fc_list.featureConfig.add()
            f1.key = "USB_MTU"
            f1.value = 16384
            f2 = fc_list.featureConfig.add()
            f2.key = "I_FRAME_INTERVAL"
            f2.value = 300
            f3 = fc_list.featureConfig.add()
            f3.key = "CONNECT_TYPE"
            f3.value = 2

            self.send_cmd(constants.MSG_CMD_HU_FEATURE_CONFIG_LIST, fc_list.SerializeToString())
            self.set_state(HandshakeState.VIDEO_PREPARING)

        # 5. 收到视频编码器参数 (65544)
        elif service_type == constants.MSG_CMD_VIDEO_ENCODER_INIT:
            enc = proto_codec.CarlifeVideoEncoderInfo.FromString(payload)
            if enc.width > 0:
                self.video_width = enc.width
            if enc.height > 0:
                self.video_height = enc.height
            if enc.frameRate > 0:
                self.video_fps = enc.frameRate
            logger.info(f"[视频] 手机确认视频编码参数: {self.video_width}x{self.video_height} @ {self.video_fps}fps")

            # 依据 sources/d/b/a/a/p/k/b.java:90 车端回复 98313 启动视频推流
            self.send_video_encoder_start()
            self.set_state(HandshakeState.CONNECTED)
            if self.on_video_ready:
                self.on_video_ready(self.video_width, self.video_height, self.video_fps)

        # 6. 收到手机端视频编码器就绪通知 (65551)
        elif service_type == constants.MSG_CMD_VIDEO_ENCODER_INIT_DONE:
            logger.info("[视频] 收到手机端视频编码器就绪通知 (65551)")
            # 依据 sources/d/b/a/a/p/k/b.java:66-68，再次发送 98311 进行确认
            self.send_video_encoder_init()

        # 7. 心跳回复 (131074)
        elif service_type == constants.MSG_CMD_HU_HEARTBEAT:
            self.last_heartbeat_time = time.time()
