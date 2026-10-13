# -*- coding: utf-8 -*-
"""
CarLife 协议常量定义
依据源码位置：
- 通道与端口：sources/d/b/a/a/p/o/e/c.java:16
- UDP 发现端口：sources/d/b/a/a/p/o/e/d.java:146
- 消息 ID 映射表：sources/d/b/a/a/o/h/e/b.java:963-1022
- 触控事件：sources/com/baidu/carlife/sdk/receiver/view/RemoteDisplayGLView.java:220
"""

# ================= 通道 (Channel) 与端口 (Port) =================
CHANNEL_CMD = 1       # 控制/信令通道
PORT_CMD = 7240

CHANNEL_VIDEO = 2     # 视频流通道
PORT_VIDEO = 8240

CHANNEL_AUDIO = 3     # 媒体音频/音乐通道
PORT_AUDIO = 9240

CHANNEL_TTS = 4       # 导航语音/TTS通道
PORT_TTS = 9241

CHANNEL_VR = 5        # 语音识别通道
PORT_VR = 9242

CHANNEL_TOUCH = 6     # 触控/按键交互通道
PORT_TOUCH = 9340

CHANNEL_DATA = 7      # 车辆传感器与数据通道
PORT_DATA = 9440

ALL_CHANNELS = [
    (CHANNEL_CMD, PORT_CMD, "Command/Control"),
    (CHANNEL_VIDEO, PORT_VIDEO, "Video"),
    (CHANNEL_AUDIO, PORT_AUDIO, "MediaAudio"),
    (CHANNEL_TTS, PORT_TTS, "TTSAudio"),
    (CHANNEL_VR, PORT_VR, "VRAudio"),
    (CHANNEL_TOUCH, PORT_TOUCH, "Touch/Input"),
    (CHANNEL_DATA, PORT_DATA, "CarData"),
]

# Wi-Fi 发现广播端口 (车端在此端口监听手机端广播)
UDP_DISCOVERY_PORT = 7999

# ================= ServiceType / 消息 ID 常量 =================
# 1. 握手与版本协商 (Channel 1)
MSG_CMD_HU_PROTOCOL_VERSION = 98305              # 0x00018001: 车端发起版本协商 (CarlifeProtocolVersion)
MSG_CMD_MD_PROTOCOL_VERSION_MATCH_STATUS = 65538 # 0x00010002: 手机回复版本匹配状态 (CarlifeProtocolVersionMatchStatus)
MSG_CMD_HU_STATISTICAL_INFO = 98343              # 0x00018027: 车端发送统计信息 (CarlifeStatisticsInfo)

# 2. 设备信息与鉴权 (Channel 1)
MSG_CMD_HU_INFO = 98307                          # 0x00018003: 车端回复设备信息 (CarlifeDeviceInfo)
MSG_CMD_MD_INFO = 65540                          # 0x00010004: 手机发送设备信息 (CarlifeDeviceInfo)
MSG_CMD_MD_AUTHEN_RESULT = 65611                 # 0x0001004B: 手机发送鉴权结果 (CarlifeAuthenResult)
MSG_CMD_HU_AUTHEN_RESULT = 98380                 # 0x0001804C: 车端确认鉴权结果

# 3. 特征配置 (Channel 1)
MSG_CMD_MD_FEATURE_CONFIG_LIST = 65617           # 0x00010051: 手机请求配置列表 (CarlifeFeatureConfigList)
MSG_CMD_HU_FEATURE_CONFIG_LIST = 98386           # 0x00018052: 车端回复配置列表 (CarlifeFeatureConfigList)

# 手机前后台状态与手机端心跳保活 (Channel 1)
MSG_CMD_MD_FOREGROUND = 65560                     # 0x00010018: 手机端 CarLife 进入前台
MSG_CMD_MD_BACKGROUND = 65561                     # 0x00010019: 手机端 CarLife 退入后台
MSG_CMD_MD_HEARTBEAT = 65563                      # 0x0001001B: 手机端向车机发送的保活心跳 (sources/d/b/a/a/o/h/d.java:154)
MSG_CMD_MD_BACK_TO_HOME = 65569                   # 0x00010021: 返回车机主页 (sources/d/b/a/a/p/m/a/d.java:13)

# 语音麦克风、模块前后台状态与车况同步 (Channel 1)
MSG_CMD_MD_MIC_RECORD_WAKEUP_START = 65570       # 0x00010022: 手机请求开启语音唤醒监听录音 (VR)
MSG_CMD_MD_MIC_RECORD_END = 65571                # 0x00010023: 语音录音结束
MSG_CMD_MD_MIC_RECORD_RECOG_START = 65572        # 0x00010024: 语音识别录音开始
MSG_CMD_MD_MODULE_STATUS_LIST = 65574            # 0x00010026: 手机端各模块状态变更列表 (CarlifeModuleStatusList)
MSG_CMD_MD_NAVI_NEXT_TURN_INFO = 65584           # 0x00010030: 导航诱导转向信息 (CarlifeNaviNextTurnInfo)
MSG_CMD_MD_REQ_VEHICLE_INFO = 65585              # 0x00010031: 手机请求车端传感器支持列表
MSG_CMD_MD_SUBSCRIBE_VEHICLE_INFO = 65587        # 0x00010033: 手机订阅车况
MSG_CMD_MD_UNSUBSCRIBE_VEHICLE_INFO = 65588      # 0x00010034: 手机取消订阅车况
MSG_CMD_MD_REQ_VEHICLE_DATA = 65589              # 0x00010035: 手机拉取车况数据
MSG_CMD_MD_CAR_DATA = 65590                       # 0x00010036: 手机端周期性推送的 GPS 与车载数据流 (sources/d/b/a/a/o/h/d.java:72)
MSG_CMD_MD_REQ_SUBSCRIBE_MOBILE_INFO = 65603     # 0x00010043: 手机请求订阅移动 CarLife 信息
MSG_CMD_MD_SUBSCRIBE_MOBILE_INFO_LIST = 65604    # 0x00010044: 手机订阅移动端信息列表 (CarlifeSubscribeMobileCarLifeInfoList)
MSG_CMD_MD_AUTHEN_RESPONSE = 65609               # 0x00010049: 鉴权响应 (CarlifeAuthenResponse)
MSG_CMD_MD_CONNECT_TIME_SYNC = 65632             # 0x00010060: 连接时间同步 (CarlifeConnectTimeSync)
MSG_CMD_MD_REQ_HU_RSA_PUBLIC_KEY = 65642         # 0x0001006A: 手机请求车机 RSA 公钥
MSG_CMD_MD_AES_KEY_REQUEST = 65644               # 0x0001006C: 手机发送 AES 秘钥请求 (CarlifeMdAesKeyRequest)
MSG_CMD_MD_AES_KEY_DONE = 65646                  # 0x0001006E: AES 秘钥协商完成
MSG_CMD_MD_VEHICLE_CONTROL = 65647               # 0x0001006F: 车辆控制指令 (CarlifeVehicleControl)

# 4. 视频启动协商 (Channel 1)
MSG_CMD_VIDEO_ENCODER_INIT = 65544               # 0x00010008: 手机提供编码参数 (CarlifeVideoEncoderInfo)
MSG_CMD_MD_VIDEO_FRAME_RATE = 65549              # 0x0001000D: 手机视频帧率信息 (CarlifeVideoFrameRate)
MSG_CMD_VIDEO_ENCODER_INIT_DONE = 65551          # 0x0001000F: 手机视频编码器准备好
MSG_CMD_HU_VIDEO_ENCODER_INIT = 98311            # 0x00018007: 车端向手机通知期望的分辨率与帧率 (CarlifeVideoEncoderInfo)
MSG_CMD_VIDEO_ENCODER_START = 98313              # 0x00018009: 车端确认开始推流 (无负载)
MSG_CMD_VIDEO_ENCODER_PAUSE = 98316              # 0x0001800C: 暂停推流
MSG_CMD_VIDEO_ENCODER_RESET = 98311              # 0x00018007: 重置推流 (同 HU_VIDEO_ENCODER_INIT)

# 5. 心跳与流媒体数据 (Channel 1 / Channel 2 / Channel 3/4)
MSG_CMD_HU_HEARTBEAT = 131074                    # 0x00020002: 车端心跳包
MSG_VIDEO_DATA = 131073                          # 0x00020001: 视频帧数据 (H.264 NALU)
MSG_MEDIA_INIT = 196609                          # 0x00030001: 媒体音频初始化 (CarlifeMusicInit)
MSG_MEDIA_DATA = 196610                          # 0x00030002: 媒体音频裸流 (PCM)
MSG_MEDIA_STOP = 196614                          # 0x00030006: 媒体音频停止
MSG_NAVI_TTS_INIT = 262145                       # 0x00040001: 导航TTS初始化 (CarlifeTTSInit)
MSG_NAVI_TTS_STOP = 262146                       # 0x00040002: 导航TTS停止
MSG_NAVI_TTS_DATA = 262147                       # 0x00040003: 导航TTS裸流 (PCM)
MSG_VR_AUDIO_INIT = 327682                       # 0x00050002: 语音识别音频初始化 (CarlifeTTSInit)
MSG_VR_AUDIO_DATA = 327683                       # 0x00050003: 语音识别音频裸流 (PCM)
MSG_VR_AUDIO_STOP = 327684                       # 0x00050004: 语音识别音频停止

# 6. 触控与按键 (Channel 6)
MSG_TOUCH_ACTION = 425985                        # 0x00068001: 触控事件 (CarlifeTouchAction)
MSG_TOUCH_ACTION_DOWN = 425986                   # 0x00068002
MSG_TOUCH_ACTION_UP = 425987                     # 0x00068003
MSG_TOUCH_ACTION_MOVE = 425988                   # 0x00068004
MSG_TOUCH_ACTION_CLICK = 425989                  # 0x00068005
MSG_TOUCH_MULTI_POINT = 425998                   # 0x0006800E: 多点触控
MSG_HARD_KEY_CODE = 425992                       # 0x00068008: 实体按键 (CarlifeCarHardKeyCode)

# 7. 车况数据 (Channel 7)
MSG_CAR_SPEED = 98319                            # 0x0001800F: 车速 (CarlifeCarSpeed)
MSG_CAR_GPS = 98320                              # 0x00018010: GPS信息 (CarlifeCarGps)
MSG_CAR_GYRO = 98321                             # 0x00018011: 陀螺仪 (CarlifeGyroscope)
MSG_CAR_ACCEL = 98322                            # 0x00018012: 加速度 (CarlifeAcceleration)
MSG_CAR_OIL = 98323                              # 0x00018013: 油耗 (CarlifeOil)
MSG_CAR_GEAR = 98345                             # 0x00018029: 挡位 (CarlifeGearInfo)

# 消息名称反向映射表 (用于日志解析，依据 sources/d/b/a/a/o/h/e/b.java 及协议规范)
MSG_NAMES = {
    # 握手与基础控制
    MSG_CMD_HU_PROTOCOL_VERSION: "HU_PROTOCOL_VERSION",
    MSG_CMD_MD_PROTOCOL_VERSION_MATCH_STATUS: "MD_PROTOCOL_VERSION_MATCH_STATUS",
    MSG_CMD_HU_STATISTICAL_INFO: "HU_STATISTICAL_INFO",
    MSG_CMD_HU_INFO: "HU_INFO",
    MSG_CMD_MD_INFO: "MD_INFO",
    MSG_CMD_MD_AUTHEN_RESULT: "MD_AUTHEN_RESULT",
    MSG_CMD_MD_AUTHEN_RESPONSE: "MD_AUTHEN_RESPONSE",
    MSG_CMD_HU_AUTHEN_RESULT: "HU_AUTHEN_RESULT",
    MSG_CMD_MD_FEATURE_CONFIG_LIST: "MD_FEATURE_CONFIG_LIST",
    MSG_CMD_HU_FEATURE_CONFIG_LIST: "HU_FEATURE_CONFIG_LIST",
    MSG_CMD_MD_FOREGROUND: "MD_FOREGROUND",
    MSG_CMD_MD_BACKGROUND: "MD_BACKGROUND",
    MSG_CMD_MD_HEARTBEAT: "MD_HEARTBEAT",
    MSG_CMD_MD_BACK_TO_HOME: "MD_BACK_TO_HOME",
    
    # 语音与模块状态
    MSG_CMD_MD_MIC_RECORD_WAKEUP_START: "MD_MIC_RECORD_WAKEUP_START",
    MSG_CMD_MD_MIC_RECORD_END: "MD_MIC_RECORD_END",
    MSG_CMD_MD_MIC_RECORD_RECOG_START: "MD_MIC_RECORD_RECOG_START",
    MSG_CMD_MD_MODULE_STATUS_LIST: "MD_MODULE_STATUS_LIST",
    MSG_CMD_MD_NAVI_NEXT_TURN_INFO: "MD_NAVI_NEXT_TURN_INFO",
    MSG_CMD_MD_REQ_VEHICLE_INFO: "MD_REQ_VEHICLE_INFO",
    MSG_CMD_MD_SUBSCRIBE_VEHICLE_INFO: "MD_SUBSCRIBE_VEHICLE_INFO",
    MSG_CMD_MD_UNSUBSCRIBE_VEHICLE_INFO: "MD_UNSUBSCRIBE_VEHICLE_INFO",
    MSG_CMD_MD_REQ_VEHICLE_DATA: "MD_REQ_VEHICLE_DATA",
    MSG_CMD_MD_CAR_DATA: "MD_CAR_DATA",
    MSG_CMD_MD_REQ_SUBSCRIBE_MOBILE_INFO: "MD_REQ_SUBSCRIBE_MOBILE_INFO",
    MSG_CMD_MD_SUBSCRIBE_MOBILE_INFO_LIST: "MD_SUBSCRIBE_MOBILE_INFO_LIST",
    MSG_CMD_MD_CONNECT_TIME_SYNC: "MD_CONNECT_TIME_SYNC",
    MSG_CMD_MD_REQ_HU_RSA_PUBLIC_KEY: "MD_REQ_HU_RSA_PUBLIC_KEY",
    MSG_CMD_MD_AES_KEY_REQUEST: "MD_AES_KEY_REQUEST",
    MSG_CMD_MD_AES_KEY_DONE: "MD_AES_KEY_DONE",
    MSG_CMD_MD_VEHICLE_CONTROL: "MD_VEHICLE_CONTROL",

    # 视频通道
    MSG_CMD_VIDEO_ENCODER_INIT: "VIDEO_ENCODER_INIT",
    MSG_CMD_MD_VIDEO_FRAME_RATE: "MD_VIDEO_FRAME_RATE",
    MSG_CMD_VIDEO_ENCODER_INIT_DONE: "VIDEO_ENCODER_INIT_DONE",
    MSG_CMD_HU_VIDEO_ENCODER_INIT: "HU_VIDEO_ENCODER_INIT",
    MSG_CMD_VIDEO_ENCODER_START: "VIDEO_ENCODER_START",
    MSG_CMD_VIDEO_ENCODER_PAUSE: "VIDEO_ENCODER_PAUSE",
    MSG_CMD_VIDEO_ENCODER_RESET: "VIDEO_ENCODER_RESET",
    MSG_VIDEO_DATA: "VIDEO_DATA",

    # 音频通道
    MSG_CMD_HU_HEARTBEAT: "HU_HEARTBEAT",
    MSG_MEDIA_INIT: "MEDIA_INIT",
    MSG_MEDIA_DATA: "MEDIA_DATA",
    MSG_MEDIA_STOP: "MEDIA_STOP",
    MSG_NAVI_TTS_INIT: "NAVI_TTS_INIT",
    MSG_NAVI_TTS_STOP: "NAVI_TTS_STOP",
    MSG_NAVI_TTS_DATA: "NAVI_TTS_DATA",
    MSG_VR_AUDIO_INIT: "VR_AUDIO_INIT",
    MSG_VR_AUDIO_DATA: "VR_AUDIO_DATA",
    MSG_VR_AUDIO_STOP: "VR_AUDIO_STOP",

    # 触控与按键
    MSG_TOUCH_ACTION: "TOUCH_ACTION",
    MSG_TOUCH_ACTION_DOWN: "TOUCH_ACTION_DOWN",
    MSG_TOUCH_ACTION_UP: "TOUCH_ACTION_UP",
    MSG_TOUCH_ACTION_MOVE: "TOUCH_ACTION_MOVE",
    MSG_TOUCH_ACTION_CLICK: "TOUCH_ACTION_CLICK",
    MSG_TOUCH_MULTI_POINT: "TOUCH_MULTI_POINT",
    MSG_HARD_KEY_CODE: "HARD_KEY_CODE",

    # 车况数据
    MSG_CAR_SPEED: "CAR_SPEED",
    MSG_CAR_GPS: "CAR_GPS",
    MSG_CAR_GYRO: "CAR_GYRO",
    MSG_CAR_ACCEL: "CAR_ACCEL",
    MSG_CAR_OIL: "CAR_OIL",
    MSG_CAR_GEAR: "CAR_GEAR",

    # HUD 导航转向消息
    MSG_CMD_MD_NAVI_NEXT_TURN_INFO: "MD_NAVI_NEXT_TURN_INFO",
}

# ================= 触控动作类型 =================
ACTION_DOWN = 0
ACTION_UP = 1
ACTION_MOVE = 2

# ================= 常用硬按键码 =================
KEYCODE_HOME = 1
KEYCODE_BACK = 2
KEYCODE_PHONE_CALL = 3
KEYCODE_PHONE_END = 4
KEYCODE_MEDIA = 5

# ================= HUD 转向动作码枚举 (CarlifeNaviNextTurnInfo.nextTurn) =================
HUD_TURN_ACTIONS = {
    1: "直行",
    2: "右前方转弯",
    3: "右转",
    4: "右后方转弯",
    5: "掉头",
    6: "左后方转弯",
    7: "左转",
    8: "左前方转弯",
    9: "到达途经点",
    10: "到达目的地",
    11: "进入环岛",
    12: "驶出环岛",
    16: "掉头",
    24: "靠最右侧车道",
    25: "靠最左侧车道",
    80: "右前方分支",
    81: "左前方分支",
}
