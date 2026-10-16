# -*- coding: utf-8 -*-
"""
CarLife 协议常量定义
依据文档与源码位置：
- 通信协议规范：《百度CarLife车机手机互联方案接入详细指南V2.1.1.pdf》表 10.2-1 等章节
- 手机端源码：sources/com/baidu/carlife/core/CommonParams.java
- 通道与端口：sources/com/baidu/carlife/core/CommonParams.java:678-691
- 消息 ID 映射与测试用例：sources/com/baidu/carlife/core/carlifetest/TestCases.java:1033-1442
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

# ================= ServiceType / 消息 ID 常量 (Channel 1: 控制通道) =================

# 1. 握手与协议版本协商
MSG_CMD_HU_PROTOCOL_VERSION = 98305              # 0x00018001: 车端发起版本协商 (CarlifeProtocolVersion)
MSG_CMD_PROTOCOL_VERSION_MATCH_STATUS = 65538    # 0x00010002: 手机回复版本匹配状态 (CarlifeProtocolVersionMatchStatus)
MSG_CMD_MD_PROTOCOL_VERSION_MATCH_STATUS = 65538 # 兼容别名

# 2. 设备信息与蓝牙配对 (OOB)
MSG_CMD_HU_INFO = 98307                          # 0x00018003: 车端发送设备信息 (CarlifeDeviceInfo)
MSG_CMD_MD_INFO = 65540                          # 0x00010004: 手机发送设备信息 (CarlifeDeviceInfo)
MSG_CMD_HU_BT_OOB_INFO = 98309                   # 0x00018005: 车端发送蓝牙 OOB 信息 (CarlifeBTPairInfo)
MSG_CMD_MD_BT_OOB_INFO = 65542                   # 0x00010006: 手机发送蓝牙 OOB 信息 (CarlifeBTPairInfo)

# 3. 视频参数协商与推流控制
MSG_CMD_HU_VIDEO_ENCODER_INIT = 98311            # 0x00018007: 车端向手机通知期望的分辨率与帧率 (CarlifeVideoEncoderInfo)
MSG_CMD_VIDEO_ENCODER_INIT = 65544               # 0x00010008: 手机提供编码参数 (CarlifeVideoEncoderInfo)
MSG_CMD_VIDEO_ENCODER_INIT_DONE = 65544          # 0x00010008: 手机视频编码器准备好
MSG_CMD_VIDEO_ENCODER_START = 98313              # 0x00018009: 车端请求开始推流 (无负载)
MSG_CMD_VIDEO_ENCODER_PAUSE = 98314              # 0x0001800A: 车端请求暂停推流 (无负载)
MSG_CMD_VIDEO_ENCODER_RESET = 98315              # 0x0001800B: 车端请求重置推流 (无负载)
MSG_CMD_VIDEO_ENCODER_FRAME_RATE_CHANGE = 98316  # 0x0001800C: 车机请求改变帧率 (CarlifeVideoFrameRate)
MSG_CMD_VIDEO_ENCODER_FRAME_RATE_CHANGE_DONE = 65549 # 0x0001000D: 手机响应帧率改变 (CarlifeVideoFrameRate)
MSG_CMD_MD_VIDEO_FRAME_RATE = 65549              # 兼容别名
MSG_CMD_PAUSE_MEDIA = 98318                      # 0x0001800E: 暂停媒体
MSG_CMD_VIDEO_ENCODER_JPEG = 98390               # 0x00018056: 车机请求 JPEG 截图
MSG_CMD_VIDEO_ENCODER_JPEG_ACK = 65623           # 0x00010057: 手机回复 JPEG 截图确认

# 4. 车身数据通道控制与上报 (Channel 7 / Channel 1)
MSG_CMD_CAR_VELOCITY = 98319                     # 0x0001800F: 车速 (CarlifeCarSpeed)
MSG_CAR_SPEED = 98319                            # 兼容别名
MSG_CMD_CAR_GPS = 98320                          # 0x00018010: GPS信息 (CarlifeCarGps)
MSG_CAR_GPS = 98320                              # 兼容别名
MSG_CMD_CAR_GYROSCOPE = 98321                    # 0x00018011: 陀螺仪 (CarlifeGyroscope)
MSG_CAR_GYRO = 98321                             # 兼容别名
MSG_CMD_CAR_ACCELERATION = 98322                 # 0x00018012: 加速度 (CarlifeAcceleration)
MSG_CAR_ACCEL = 98322                            # 兼容别名
MSG_CMD_CAR_OIL = 98323                          # 0x00018013: 油量 (CarlifeOil)
MSG_CAR_OIL = 98323                              # 兼容别名
MSG_CMD_CAR_DATA_GEAR = 98345                    # 0x00018029: 挡位 (CarlifeGearInfo)
MSG_CAR_GEAR = 98345                             # 兼容别名

# 5. 电话状态通知
MSG_CMD_TELE_STATE_CHANGE_INCOMING = 65556       # 0x00010014: 来电
MSG_CMD_TELE_STATE_CHANGE_OUTGOING = 65557       # 0x00010015: 去电
MSG_CMD_TELE_STATE_CHANGE_IDLE = 65558           # 0x00010016: 电话空闲/挂断
MSG_CMD_TELE_STATE_CHANGE_INCALLING = 65559       # 0x00010017: 通话中

# 6. 屏幕与前后台状态通知
MSG_CMD_SCREEN_ON = 65560                        # 0x00010018: 手机亮屏
MSG_CMD_SCREEN_OFF = 65561                       # 0x00010019: 手机灭屏
MSG_CMD_SCREEN_USERPRESENT = 65562               # 0x0001001A: 手机解锁
MSG_CMD_FOREGROUND = 65563                       # 0x0001001B: 手机端 CarLife 进入前台
MSG_CMD_BACKGROUND = 65564                       # 0x0001001C: 手机端 CarLife 退入后台
MSG_CMD_MD_FOREGROUND = 65563                    # 兼容别名
MSG_CMD_MD_BACKGROUND = 65564                    # 兼容别名
MSG_CMD_MD_HEARTBEAT = 65563                     # 历史兼容别名 (实际为 FOREGROUND 信令)
MSG_CMD_GO_TO_DESKTOP = 65569                    # 0x00010021: 返回车机主页/桌面 (手机->车机)
MSG_CMD_MD_BACK_TO_HOME = 65569                  # 兼容别名
MSG_CMD_GO_TO_FOREGROUND = 98341                 # 0x00018025: 车机拉起手机端进入前台
MSG_CMD_REQUEST_GO_TO_FOREGROUND = 65592         # 0x00010038: 手机请求车机拉到前台

# 7. 车机启动模式 (Launch Mode)
MSG_CMD_LAUNCH_MODE_NORMAL = 98333               # 0x0001801D: 主界面模式
MSG_CMD_LAUNCH_MODE_PHONE = 98334                # 0x0001801E: 电话模式
MSG_CMD_LAUNCH_MODE_MAP = 98335                  # 0x0001801F: 导航地图模式
MSG_CMD_LAUNCH_MODE_MUSIC = 98336                # 0x00018020: 音乐媒体模式

# 8. 麦克风与语音录音控制
MSG_CMD_MIC_RECORD_WAKEUP_START = 65570          # 0x00010022: 唤醒监听录音开启
MSG_CMD_MIC_RECORD_END = 65571                   # 0x00010023: 录音结束
MSG_CMD_MIC_RECORD_RECOG_START = 65572           # 0x00010024: 识别录音开启
MSG_CMD_MIC_RECORD_PREPARE_START = 65649         # 0x00010071: 录音准备开始
MSG_CMD_MIC_RECORD_PREPARE_DONE = 98418          # 0x00018072: 录音准备完成
MSG_CMD_MIC_SOUND_EFFECT_START = 65651           # 0x00010073: 提示音开始
MSG_CMD_MIC_SOUND_EFFECT_DONE = 98420            # 0x00018074: 提示音完成

# 9. 模块状态变更与控制
MSG_CMD_MODULE_STATUS = 65574                    # 0x00010026: 手机端模块状态变更 (CarlifeModuleStatusList/CarlifeModuleStatus)
MSG_CMD_MD_MODULE_STATUS_LIST = 65574            # 兼容别名
MSG_CMD_MODULE_CONTROL = 98344                   # 0x00018028: 车端控制模块状态 (CarlifeModuleStatus)

# 10. 统计信息
MSG_CMD_STATISTIC_INFO = 98343                   # 0x00018027: 车机向手机发送统计数据 (CarlifeStatisticsInfo)
MSG_CMD_HU_STATISTICAL_INFO = 98343              # 兼容别名
MSG_CMD_HU_CONNECT_STATISTIC = 98400             # 0x00018060: 车机连接统计信息 (CarlifeConnectStatistic)

# 11. 导航与辅助诱导 (HUD & TBT)
MSG_CMD_NAVI_NEXT_TURN_INFO = 65584              # 0x00010030: 转向诱导信息 (CarlifeNaviNextTurnInfo)
MSG_CMD_MD_NAVI_NEXT_TURN_INFO = 65584           # 兼容别名
MSG_CMD_NAVI_INFO = 65595                         # 0x0001003B: 导航基础信息 (CarlifeNaviInfo)
MSG_CMD_NAVI_ASSITANTGUIDE_INFO = 65607          # 0x00010047: 电子狗与巡航辅助诱导信息 (CarlifeNaviAssitantGuideInfo)

# 12. 车身数据订阅机制 (Car Data Subscription)
MSG_CMD_CAR_DATA_SUBSCRIBE = 65585               # 0x00010031: 手机请求车端传感器支持列表 (CarlifeVehicleInfoList)
MSG_CMD_MD_REQ_VEHICLE_INFO = 65585              # 兼容别名
MSG_CMD_CAR_DATA_SUBSCRIBE_DONE = 98354          # 0x00018032: 车端响应传感器支持列表 (CarlifeVehicleInfoList)
MSG_CMD_CAR_DATA_SUBSCRIBE_START = 65587         # 0x00010033: 手机订阅具体传感器数据 (CarlifeVehicleInfoList)
MSG_CMD_MD_SUBSCRIBE_VEHICLE_INFO = 65587        # 兼容别名
MSG_CMD_CAR_DATA_SUBSCRIBE_STOP = 65588          # 0x00010034: 手机取消订阅传感器数据 (CarlifeVehicleInfoList)
MSG_CMD_MD_UNSUBSCRIBE_VEHICLE_INFO = 65588      # 兼容别名

# 13. 媒体展示信息
MSG_CMD_MEDIA_INFO = 65589                       # 0x00010035: 媒体曲目信息 (CarlifeMediaInfo)
MSG_CMD_MEDIA_PROGRESS_BAR = 65590               # 0x00010036: 媒体播放进度条 (CarlifeMediaProgressBar)

# 14. 系统提示与异常
MSG_CMD_CONNECT_EXCEPTION = 65591                # 0x00010037: 连接异常 (CarlifeConnectException)
MSG_CMD_UI_ACTION_SOUND = 65593                  # 0x00010039: UI 提示音

# 15. 蓝牙电话 (BT HFP Protocol)
MSG_CMD_BT_HFP_REQUEST = 65600                   # 0x00010040: 手机发起 HFP 请求 (CarlifeBTHfpRequest)
MSG_CMD_BT_HFP_INDICATION = 98369                # 0x00018041: 车机响应 HFP 状态指示 (CarlifeBTHfpIndication)
MSG_CMD_BT_HFP_CONNECTION = 98370                # 0x00018042: 车机通知 HFP 连接状态 (CarlifeBTHfpConnection)
MSG_CMD_BT_HFP_RESPONSE = 98382                  # 0x0001804E: 车机响应 HFP 命令 (CarlifeBTHfpResponse)
MSG_CMD_BT_HFP_STATUS_REQUEST = 65615            # 0x0001004F: 手机请求 HFP 状态
MSG_CMD_BT_HFP_STATUS_RESPONSE = 98384           # 0x00018050: 车机回复 HFP 状态
MSG_CMD_START_BT_AUTOPAIR_REQUEST = 65613        # 0x0001004D: 手机发起自动配对请求
MSG_CMD_BT_START_IDENTIFY_REQ = 98387            # 0x00018053: 车机发起蓝牙识别请求
MSG_CMD_BT_IDENTIFY_RESULT_IND = 65620           # 0x00010054: 手机回复蓝牙识别结果
MSG_CMD_BT_HFP_CALL_STATUS_COVER = 65624         # 0x00010058: 通话状态覆盖 (CarlifeBTHfpCallStatusCover)

# 16. 多屏互联与 CarLife 数据订阅 (CarLife Data Subscription)
MSG_CMD_CARLIFE_DATA_SUBSCRIBE = 98371           # 0x00018043: 车机向手机订阅 CarLife 诱导数据 (CarlifeSubscribeMobileCarLifeInfoList)
MSG_CMD_CARLIFE_DATA_SUBSCRIBE_DONE = 65604      # 0x00010044: 手机确认订阅 (CarlifeSubscribeMobileCarLifeInfoList)
MSG_CMD_MD_SUBSCRIBE_MOBILE_INFO_LIST = 65604    # 兼容别名
MSG_CMD_CARLIFE_DATA_SUBSCRIBE_START = 98373     # 0x00018045: 车机开始接收数据 (CarlifeSubscribeMobileCarLifeInfoList)
MSG_CMD_CARLIFE_DATA_SUBSCRIBE_STOP = 98374      # 0x00018046: 车机停止接收数据 (CarlifeSubscribeMobileCarLifeInfoList)

# 17. 鉴权与安全通道 (Authen & Encryption)
MSG_CMD_HU_AUTHEN_REQUEST = 98376                # 0x00018048: 车端发起鉴权请求 (CarlifeAuthenRequest)
MSG_CMD_MD_AUTHEN_RESPONSE = 65609               # 0x00010049: 手机回复鉴权响应 (CarlifeAuthenResponse)
MSG_CMD_HU_AUTHEN_RESULT = 98378                 # 0x0001804A: 车端确认鉴权结果 (CarlifeAuthenResult)
MSG_CMD_HU_AUTHEN_RESULT_98380 = 98380           # 0x0001804C: 历史兼容编号
MSG_CMD_MD_AUTHEN_RESULT = 65611                 # 0x0001004B: 手机发送鉴权结果 (CarlifeAuthenResult)
MSG_CMD_MD_RSA_PUBLIC_KEY_REQUEST = 65642        # 0x0001006A: 手机请求车机 RSA 公钥
MSG_CMD_MD_REQ_HU_RSA_PUBLIC_KEY = 65642         # 兼容别名
MSG_CMD_HU_RSA_PUBLIC_KEY_RESPONSE = 98411       # 0x0001806B: 车机回复 RSA 公钥
MSG_CMD_MD_AES_KEY_SEND_REQUEST = 65644          # 0x0001006C: 手机发送 AES 秘钥请求
MSG_CMD_MD_AES_KEY_REQUEST = 65644               # 兼容别名
MSG_CMD_HU_AES_REC_RESPONSE = 98413              # 0x0001806D: 车机回复 AES 接收完成
MSG_CMD_MD_ENCRYPT_READY = 65646                 # 0x0001006E: AES 秘钥协商完成
MSG_CMD_MD_AES_KEY_DONE = 65646                  # 兼容别名

# 18. 特征配置协商 (Feature Config)
MSG_CMD_MD_FEATURE_CONFIG_REQUEST = 65617        # 0x00010051: 手机请求配置列表 (CarlifeFeatureConfigList)
MSG_CMD_MD_FEATURE_CONFIG_LIST = 65617           # 兼容别名
MSG_CMD_HU_FEATURE_CONFIG_RESPONSE = 98386       # 0x00018052: 车端回复配置列表 (CarlifeFeatureConfigList)
MSG_CMD_HU_FEATURE_CONFIG_LIST = 98386           # 兼容别名

# 19. 退出、时间同步与错误码
MSG_CMD_MD_EXIT = 65625                          # 0x00010059: 手机请求退出 CarLife
MSG_CMD_ERROR_CODE = 98389                       # 0x00018055: 错误码 (CarlifeErrorCode)
MSG_CMD_TIME_SYNC = 65632                        # 0x00010060: 连接时间同步 (CarlifeConnectTimeSync)
MSG_CMD_MD_CONNECT_TIME_SYNC = 65632             # 兼容别名
MSG_CMD_FOCUS_CHANGE = 65630                     # 0x0001005E: 焦点切换通知
MSG_CMD_FOCUS_AREA_STATUS = 65648                # 0x00010070: 焦点区域状态
MSG_CMD_HU_VOICE_CONTROL = 65638                 # 0x00010066: 车机语音控制
MSG_CMD_DEVICE_VERSION_INFO = 65640              # 0x00010068: 设备版本信息
MSG_CMD_MD_STATE_CHANGE_INFO = 65653             # 0x00010075: 手机状态变更通知
MSG_CMD_HU_STATE_CHANGE_DONE = 98422             # 0x00018076: 车端状态变更确认
MSG_CMD_MD_VEHICLE_CONTROL = 65647               # 0x0001006F: 车辆控制指令 (CarlifeVehicleControl)

# ================= Channel 2: 视频通道 =================
MSG_VIDEO_DATA = 131073                          # 0x00020001: 视频帧数据 (H.264 NALU)
MSG_VIDEO_HEARTBEAT = 131074                     # 0x00020002: 视频心跳包 (HU -> MD)
MSG_CMD_HU_HEARTBEAT = 131074                    # 兼容别名

# ================= Channel 3: 媒体音频通道 =================
MSG_MEDIA_INIT = 196609                          # 0x00030001: 媒体音频初始化 (CarlifeMusicInit)
MSG_MEDIA_STOP = 196610                          # 0x00030002: 媒体音频停止
MSG_MEDIA_PAUSE = 196611                         # 0x00030003: 媒体音频暂停
MSG_MEDIA_RESUME_PLAY = 196612                   # 0x00030004: 媒体音频恢复播放
MSG_MEDIA_SEEK_TO = 196613                       # 0x00030005: 媒体音频快进
MSG_MEDIA_DATA = 196614                          # 0x00030006: 媒体音频裸流 (PCM)
MSG_MEDIA_DATA_ENCODE = 196615                   # 0x00030007: 编码后媒体音频流

# ================= Channel 4: 导航 TTS 通道 =================
MSG_NAVI_TTS_INIT = 262145                       # 0x00040001: 导航TTS初始化 (CarlifeTTSInit)
MSG_NAVI_TTS_END = 262146                        # 0x00040002: 导航TTS停止
MSG_NAVI_TTS_STOP = 262146                       # 兼容别名
MSG_NAVI_TTS_DATA = 262147                       # 0x00040003: 导航TTS裸流 (PCM)
MSG_NAV_TTS_INTERRUPT = 262149                   # 0x00040005: 导航TTS打断
MSG_NAV_TTS_FEED_END = 262150                    # 0x00040006: 导航TTS送流结束
MSG_NAV_TTS_DONE = 294919                        # 0x00048007: 车机确认TTS播报完成

# ================= Channel 5: 语音识别 VR 通道 =================
MSG_VR_DATA = 360449                             # 0x00058001: 麦克风录音 PCM 数据 (HU -> MD)
MSG_VR_AUDIO_INIT = 327682                       # 0x00050002: VR语音初始化 (CarlifeTTSInit)
MSG_VR_AUDIO_DATA = 327683                       # 0x00050003: VR语音裸流 (PCM)
MSG_VR_AUDIO_STOP = 327684                       # 0x00050004: VR语音停止
MSG_VR_MODULE_STATUS = 327685                    # 0x00050005: VR模块状态变更
MSG_VR_AUDIO_INTERRUPT = 327686                  # 0x00050006: VR语音打断
MSG_VR_AUDIO_FEED_END = 327688                   # 0x00050008: VR送流结束
MSG_VR_AUDIO_DONE = 360457                       # 0x00058009: 车机确认VR播报完成

# ================= Channel 6: 触控与按键通道 =================
MSG_TOUCH_ACTION = 425985                        # 0x00068001: 触控事件 (CarlifeTouchAction)
MSG_TOUCH_ACTION_DOWN = 425986                   # 0x00068002: 按下
MSG_TOUCH_ACTION_UP = 425987                     # 0x00068003: 抬起
MSG_TOUCH_ACTION_MOVE = 425988                   # 0x00068004: 移动
MSG_TOUCH_SINGLE_CLICK = 425989                  # 0x00068005: 单击
MSG_TOUCH_ACTION_CLICK = 425989                  # 兼容别名
MSG_TOUCH_DOUBLE_CLICK = 425990                  # 0x00068006: 双击
MSG_TOUCH_LONG_PRESS = 425991                    # 0x00068007: 长按
MSG_TOUCH_CAR_HARD_KEY_CODE = 425992             # 0x00068008: 实体按键 (CarlifeCarHardKeyCode)
MSG_HARD_KEY_CODE = 425992                       # 兼容别名
MSG_TOUCH_UI_ACTION_SOUND = 393225               # 0x00060009: 触控提示音
MSG_TOUCH_UI_ACTION_BEGIN = 425994               # 0x0006800A: UI动作开始
MSG_TOUCH_ACTION_POINTER_DOWN = 425995           # 0x0006800B: 次点按下
MSG_TOUCH_ACTION_POINTER_UP = 425996             # 0x0006800C: 次点抬起
MSG_TOUCH_ACTION_OTHERPOINTER_UP = 425997        # 0x0006800D: 其它点抬起
MSG_TOUCH_MULTI_POINT = 425998                   # 0x0006800E: 多点触控 (历史兼容)

# 触控板消息 (Touch Pad)
MSG_TOUCH_PAD_DOWN = 65626                       # 0x0001005A
MSG_TOUCH_PAD_MOVE = 65627                       # 0x0001005B
MSG_TOUCH_PAD_UP = 65628                         # 0x0001005C
MSG_TOUCH_PAD_PINCH = 65629                      # 0x0001005D

# ================= 消息名称反向映射表 (用于日志与分析器) =================
MSG_NAMES = {
    # 握手与基础控制
    MSG_CMD_HU_PROTOCOL_VERSION: "HU_PROTOCOL_VERSION",
    MSG_CMD_PROTOCOL_VERSION_MATCH_STATUS: "PROTOCOL_VERSION_MATCH_STATUS",
    MSG_CMD_HU_INFO: "HU_INFO",
    MSG_CMD_MD_INFO: "MD_INFO",
    MSG_CMD_HU_BT_OOB_INFO: "HU_BT_OOB_INFO",
    MSG_CMD_MD_BT_OOB_INFO: "MD_BT_OOB_INFO",

    # 视频推流协商
    MSG_CMD_HU_VIDEO_ENCODER_INIT: "HU_VIDEO_ENCODER_INIT",
    MSG_CMD_VIDEO_ENCODER_INIT: "VIDEO_ENCODER_INIT_DONE",
    MSG_CMD_VIDEO_ENCODER_START: "VIDEO_ENCODER_START",
    MSG_CMD_VIDEO_ENCODER_PAUSE: "VIDEO_ENCODER_PAUSE",
    MSG_CMD_VIDEO_ENCODER_RESET: "VIDEO_ENCODER_RESET",
    MSG_CMD_VIDEO_ENCODER_FRAME_RATE_CHANGE: "VIDEO_ENCODER_FRAME_RATE_CHANGE",
    MSG_CMD_VIDEO_ENCODER_FRAME_RATE_CHANGE_DONE: "VIDEO_ENCODER_FRAME_RATE_CHANGE_DONE",
    MSG_CMD_PAUSE_MEDIA: "PAUSE_MEDIA",
    MSG_CMD_VIDEO_ENCODER_JPEG: "VIDEO_ENCODER_JPEG",
    MSG_CMD_VIDEO_ENCODER_JPEG_ACK: "VIDEO_ENCODER_JPEG_ACK",

    # 车身数据
    MSG_CMD_CAR_VELOCITY: "CAR_VELOCITY",
    MSG_CMD_CAR_GPS: "CAR_GPS",
    MSG_CMD_CAR_GYROSCOPE: "CAR_GYROSCOPE",
    MSG_CMD_CAR_ACCELERATION: "CAR_ACCELERATION",
    MSG_CMD_CAR_OIL: "CAR_OIL",
    MSG_CMD_CAR_DATA_GEAR: "CAR_DATA_GEAR",

    # 电话状态
    MSG_CMD_TELE_STATE_CHANGE_INCOMING: "TELE_STATE_CHANGE_INCOMING",
    MSG_CMD_TELE_STATE_CHANGE_OUTGOING: "TELE_STATE_CHANGE_OUTGOING",
    MSG_CMD_TELE_STATE_CHANGE_IDLE: "TELE_STATE_CHANGE_IDLE",
    MSG_CMD_TELE_STATE_CHANGE_INCALLING: "TELE_STATE_CHANGE_INCALLING",

    # 屏幕与前后台
    MSG_CMD_SCREEN_ON: "SCREEN_ON",
    MSG_CMD_SCREEN_OFF: "SCREEN_OFF",
    MSG_CMD_SCREEN_USERPRESENT: "SCREEN_USERPRESENT",
    MSG_CMD_FOREGROUND: "FOREGROUND",
    MSG_CMD_BACKGROUND: "BACKGROUND",
    MSG_CMD_GO_TO_DESKTOP: "GO_TO_DESKTOP",
    MSG_CMD_GO_TO_FOREGROUND: "GO_TO_FOREGROUND",
    MSG_CMD_REQUEST_GO_TO_FOREGROUND: "REQUEST_GO_TO_FOREGROUND",

    # 启动模式
    MSG_CMD_LAUNCH_MODE_NORMAL: "LAUNCH_MODE_NORMAL",
    MSG_CMD_LAUNCH_MODE_PHONE: "LAUNCH_MODE_PHONE",
    MSG_CMD_LAUNCH_MODE_MAP: "LAUNCH_MODE_MAP",
    MSG_CMD_LAUNCH_MODE_MUSIC: "LAUNCH_MODE_MUSIC",

    # 语音录音
    MSG_CMD_MIC_RECORD_WAKEUP_START: "MIC_RECORD_WAKEUP_START",
    MSG_CMD_MIC_RECORD_END: "MIC_RECORD_END",
    MSG_CMD_MIC_RECORD_RECOG_START: "MIC_RECORD_RECOG_START",
    MSG_CMD_MIC_RECORD_PREPARE_START: "MIC_RECORD_PREPARE_START",
    MSG_CMD_MIC_RECORD_PREPARE_DONE: "MIC_RECORD_PREPARE_DONE",
    MSG_CMD_MIC_SOUND_EFFECT_START: "MIC_SOUND_EFFECT_START",
    MSG_CMD_MIC_SOUND_EFFECT_DONE: "MIC_SOUND_EFFECT_DONE",

    # 模块状态
    MSG_CMD_MODULE_STATUS: "MODULE_STATUS",
    MSG_CMD_MODULE_CONTROL: "MODULE_CONTROL",

    # 统计信息
    MSG_CMD_STATISTIC_INFO: "STATISTIC_INFO",
    MSG_CMD_HU_CONNECT_STATISTIC: "HU_CONNECT_STATISTIC",

    # 导航与辅助诱导
    MSG_CMD_NAVI_NEXT_TURN_INFO: "NAVI_NEXT_TURN_INFO",
    MSG_CMD_NAVI_INFO: "NAVI_INFO",
    MSG_CMD_NAVI_ASSITANTGUIDE_INFO: "NAVI_ASSITANTGUIDE_INFO",

    # 车身数据订阅
    MSG_CMD_CAR_DATA_SUBSCRIBE: "CAR_DATA_SUBSCRIBE",
    MSG_CMD_CAR_DATA_SUBSCRIBE_DONE: "CAR_DATA_SUBSCRIBE_DONE",
    MSG_CMD_CAR_DATA_SUBSCRIBE_START: "CAR_DATA_SUBSCRIBE_START",
    MSG_CMD_CAR_DATA_SUBSCRIBE_STOP: "CAR_DATA_SUBSCRIBE_STOP",

    # 媒体展示
    MSG_CMD_MEDIA_INFO: "MEDIA_INFO",
    MSG_CMD_MEDIA_PROGRESS_BAR: "MEDIA_PROGRESS_BAR",

    # 系统异常与提示
    MSG_CMD_CONNECT_EXCEPTION: "CONNECT_EXCEPTION",
    MSG_CMD_UI_ACTION_SOUND: "UI_ACTION_SOUND",

    # 蓝牙 HFP 电话族
    MSG_CMD_BT_HFP_REQUEST: "BT_HFP_REQUEST",
    MSG_CMD_BT_HFP_INDICATION: "BT_HFP_INDICATION",
    MSG_CMD_BT_HFP_CONNECTION: "BT_HFP_CONNECTION",
    MSG_CMD_BT_HFP_RESPONSE: "BT_HFP_RESPONSE",
    MSG_CMD_BT_HFP_STATUS_REQUEST: "BT_HFP_STATUS_REQUEST",
    MSG_CMD_BT_HFP_STATUS_RESPONSE: "BT_HFP_STATUS_RESPONSE",
    MSG_CMD_START_BT_AUTOPAIR_REQUEST: "START_BT_AUTOPAIR_REQUEST",
    MSG_CMD_BT_START_IDENTIFY_REQ: "BT_START_IDENTIFY_REQ",
    MSG_CMD_BT_IDENTIFY_RESULT_IND: "BT_IDENTIFY_RESULT_IND",
    MSG_CMD_BT_HFP_CALL_STATUS_COVER: "BT_HFP_CALL_STATUS_COVER",

    # 多屏互联与 CarLife 订阅
    MSG_CMD_CARLIFE_DATA_SUBSCRIBE: "CARLIFE_DATA_SUBSCRIBE",
    MSG_CMD_CARLIFE_DATA_SUBSCRIBE_DONE: "CARLIFE_DATA_SUBSCRIBE_DONE",
    MSG_CMD_CARLIFE_DATA_SUBSCRIBE_START: "CARLIFE_DATA_SUBSCRIBE_START",
    MSG_CMD_CARLIFE_DATA_SUBSCRIBE_STOP: "CARLIFE_DATA_SUBSCRIBE_STOP",

    # 鉴权与安全
    MSG_CMD_HU_AUTHEN_REQUEST: "HU_AUTHEN_REQUEST",
    MSG_CMD_MD_AUTHEN_RESPONSE: "MD_AUTHEN_RESPONSE",
    MSG_CMD_HU_AUTHEN_RESULT: "HU_AUTHEN_RESULT",
    MSG_CMD_HU_AUTHEN_RESULT_98380: "HU_AUTHEN_RESULT_98380",
    MSG_CMD_MD_AUTHEN_RESULT: "MD_AUTHEN_RESULT",
    MSG_CMD_MD_RSA_PUBLIC_KEY_REQUEST: "MD_RSA_PUBLIC_KEY_REQUEST",
    MSG_CMD_HU_RSA_PUBLIC_KEY_RESPONSE: "HU_RSA_PUBLIC_KEY_RESPONSE",
    MSG_CMD_MD_AES_KEY_SEND_REQUEST: "MD_AES_KEY_SEND_REQUEST",
    MSG_CMD_HU_AES_REC_RESPONSE: "HU_AES_REC_RESPONSE",
    MSG_CMD_MD_ENCRYPT_READY: "MD_ENCRYPT_READY",

    # 特征配置
    MSG_CMD_MD_FEATURE_CONFIG_REQUEST: "MD_FEATURE_CONFIG_REQUEST",
    MSG_CMD_HU_FEATURE_CONFIG_RESPONSE: "HU_FEATURE_CONFIG_RESPONSE",

    # 退出与系统
    MSG_CMD_MD_EXIT: "MD_EXIT",
    MSG_CMD_ERROR_CODE: "ERROR_CODE",
    MSG_CMD_TIME_SYNC: "TIME_SYNC",
    MSG_CMD_FOCUS_CHANGE: "FOCUS_CHANGE",
    MSG_CMD_FOCUS_AREA_STATUS: "FOCUS_AREA_STATUS",
    MSG_CMD_HU_VOICE_CONTROL: "HU_VOICE_CONTROL",
    MSG_CMD_DEVICE_VERSION_INFO: "DEVICE_VERSION_INFO",
    MSG_CMD_MD_STATE_CHANGE_INFO: "MD_STATE_CHANGE_INFO",
    MSG_CMD_HU_STATE_CHANGE_DONE: "HU_STATE_CHANGE_DONE",
    MSG_CMD_MD_VEHICLE_CONTROL: "MD_VEHICLE_CONTROL",

    # Channel 2: 视频通道
    MSG_VIDEO_DATA: "VIDEO_DATA",
    MSG_VIDEO_HEARTBEAT: "VIDEO_HEARTBEAT",

    # Channel 3: 媒体音频
    MSG_MEDIA_INIT: "MEDIA_INIT",
    MSG_MEDIA_STOP: "MEDIA_STOP",
    MSG_MEDIA_PAUSE: "MEDIA_PAUSE",
    MSG_MEDIA_RESUME_PLAY: "MEDIA_RESUME_PLAY",
    MSG_MEDIA_SEEK_TO: "MEDIA_SEEK_TO",
    MSG_MEDIA_DATA: "MEDIA_DATA",
    MSG_MEDIA_DATA_ENCODE: "MEDIA_DATA_ENCODE",

    # Channel 4: TTS 音频
    MSG_NAVI_TTS_INIT: "NAVI_TTS_INIT",
    MSG_NAVI_TTS_END: "NAVI_TTS_END",
    MSG_NAVI_TTS_DATA: "NAVI_TTS_DATA",
    MSG_NAV_TTS_INTERRUPT: "NAV_TTS_INTERRUPT",
    MSG_NAV_TTS_FEED_END: "NAV_TTS_FEED_END",
    MSG_NAV_TTS_DONE: "NAV_TTS_DONE",

    # Channel 5: VR 音频
    MSG_VR_DATA: "VR_DATA",
    MSG_VR_AUDIO_INIT: "VR_AUDIO_INIT",
    MSG_VR_AUDIO_DATA: "VR_AUDIO_DATA",
    MSG_VR_AUDIO_STOP: "VR_AUDIO_STOP",
    MSG_VR_MODULE_STATUS: "VR_MODULE_STATUS",
    MSG_VR_AUDIO_INTERRUPT: "VR_AUDIO_INTERRUPT",
    MSG_VR_AUDIO_FEED_END: "VR_AUDIO_FEED_END",
    MSG_VR_AUDIO_DONE: "VR_AUDIO_DONE",

    # Channel 6: 触控与按键
    MSG_TOUCH_ACTION: "TOUCH_ACTION",
    MSG_TOUCH_ACTION_DOWN: "TOUCH_ACTION_DOWN",
    MSG_TOUCH_ACTION_UP: "TOUCH_ACTION_UP",
    MSG_TOUCH_ACTION_MOVE: "TOUCH_ACTION_MOVE",
    MSG_TOUCH_SINGLE_CLICK: "TOUCH_SINGLE_CLICK",
    MSG_TOUCH_DOUBLE_CLICK: "TOUCH_DOUBLE_CLICK",
    MSG_TOUCH_LONG_PRESS: "TOUCH_LONG_PRESS",
    MSG_TOUCH_CAR_HARD_KEY_CODE: "TOUCH_CAR_HARD_KEY_CODE",
    MSG_TOUCH_UI_ACTION_SOUND: "TOUCH_UI_ACTION_SOUND",
    MSG_TOUCH_UI_ACTION_BEGIN: "TOUCH_UI_ACTION_BEGIN",
    MSG_TOUCH_ACTION_POINTER_DOWN: "TOUCH_ACTION_POINTER_DOWN",
    MSG_TOUCH_ACTION_POINTER_UP: "TOUCH_ACTION_POINTER_UP",
    MSG_TOUCH_ACTION_OTHERPOINTER_UP: "TOUCH_ACTION_OTHERPOINTER_UP",
    MSG_TOUCH_PAD_DOWN: "TOUCH_PAD_DOWN",
    MSG_TOUCH_PAD_MOVE: "TOUCH_PAD_MOVE",
    MSG_TOUCH_PAD_UP: "TOUCH_PAD_UP",
    MSG_TOUCH_PAD_PINCH: "TOUCH_PAD_PINCH",
}

# ================= 触控动作类型 =================
ACTION_DOWN = 0
ACTION_UP = 1
ACTION_MOVE = 2

# ================= 实体按键码 (CarlifeCarHardKeyCode.keycode) =================
KEYCODE_HOME = 1
KEYCODE_PHONE_CALL = 2
KEYCODE_PHONE_END = 3
KEYCODE_PHONE_END_MUTE = 4
KEYCODE_HFP = 5
KEYCODE_SELECTOR_NEXT = 6
KEYCODE_SELECTOR_PREVIOUS = 7
KEYCODE_SETTING = 8
KEYCODE_MEDIA = 9
KEYCODE_RADIO = 10
KEYCODE_NAVI = 11
KEYCODE_SRC = 12
KEYCODE_MODE = 13
KEYCODE_BACK = 14
KEYCODE_SEEK_SUB = 15
KEYCODE_SEEK_ADD = 16
KEYCODE_VOLUME_SUB = 17
KEYCODE_VOLUME_ADD = 18
KEYCODE_MUTE = 19
KEYCODE_OK = 20
KEYCODE_MOVE_LEFT = 21
KEYCODE_MOVE_RIGHT = 22
KEYCODE_MOVE_UP = 23
KEYCODE_MOVE_DOWN = 24
KEYCODE_MOVE_UP_LEFT = 25
KEYCODE_MOVE_UP_RIGHT = 26
KEYCODE_MOVE_DOWN_LEFT = 27
KEYCODE_MOVE_DOWN_RIGHT = 28
KEYCODE_TEL = 29
KEYCODE_MAIN = 30
KEYCODE_MEDIA_START = 31
KEYCODE_MEDIA_STOP = 32
KEYCODE_VR_START = 33
KEYCODE_VR_STOP = 34

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

# ================= 模块 ID 枚举 (CarlifeModuleStatus.moduleID) =================
# 依据 sources/com/baidu/carlife/core/base/model/ModuleStatusModel.java:6-13
MODULE_NAMES = {
    1: "电话(PHONE)",
    2: "导航(NAVI)",
    3: "音乐(MUSIC)",
    4: "语音(VR)",
    5: "连接(CONNECT)",
    6: "麦克风(MIC)",
    8: "巡航电子狗(CRUISE/EDOG)",
    9: "巡航伴随(CRUISE_FOLLOW)",
}

# ================= 各模块状态 ID 枚举 (CarlifeModuleStatus.statusID) =================
# 依据 sources/com/baidu/carlife/core/base/model/ModuleStatusModel.java:14-35
MODULE_STATUS_DESCS = {
    1: {  # PHONE
        0: "空闲(IDLE)",
        1: "来电(INCOMING)",
        2: "通话中/去电(OUTGOING)",
    },
    2: {  # NAVI
        0: "停止/未导航(IDLE)",
        1: "开始导航(START)",
        2: "停止导航(STOP)",
    },
    3: {  # MUSIC
        0: "停止/空闲(IDLE)",
        1: "播放中(RUNNING)",
    },
    4: {  # VR
        0: "空闲(IDLE)",
        1: "运行中(RUNNING)",
        2: "麦克风不支持",
        3: "阻塞空闲",
        4: "就绪(READY)",
    },
    6: {  # MIC
        0: "使用车机MIC",
        1: "使用手机MIC",
        2: "不支持",
        3: "支持左声道AES",
        4: "支持右声道AES",
    },
    8: {  # CRUISE / EDOG (巡航电子狗)
        0: "巡航停止(IDLE)",
        1: "巡航运行中(START)",
    },
    9: {  # CRUISE_FOLLOW
        0: "停止(IDLE)",
        1: "运行中(START)",
    },
}

def format_module_status_desc(module_id: int, status_id: int) -> str:
    """格式化单一模块状态为易读字符串"""
    mod_name = MODULE_NAMES.get(module_id, f"模块_{module_id}")
    status_desc = MODULE_STATUS_DESCS.get(module_id, {}).get(status_id, f"状态_{status_id}")
    return f"{mod_name}: {status_desc}"

