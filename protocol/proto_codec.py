# -*- coding: utf-8 -*-
"""
CarLife 协议 Protobuf 消息编解码器
依据源码位置：
- sources/com/baidu/carlife/protobuf/*.java
通过 google.protobuf 动态构建 Descriptor，确保在不需要外部 protoc 编译器的前提下完美编解码。
"""

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

_pool = descriptor_pool.DescriptorPool()
_file_proto = descriptor_pb2.FileDescriptorProto()
_file_proto.name = "carlife_protocol.proto"
_file_proto.package = "com.baidu.carlife.protobuf"

def _add_field(msg, name, number, ftype, label=descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL, type_name=None):
    f = msg.field.add()
    f.name = name
    f.number = number
    f.type = ftype
    f.label = label
    if type_name:
        f.type_name = type_name

# 1. CarlifeProtocolVersion (sources/com/baidu/carlife/protobuf/CarlifeProtocolVersionProto.java)
_m_ver = _file_proto.message_type.add()
_m_ver.name = "CarlifeProtocolVersion"
_add_field(_m_ver, "majorVersion", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_ver, "minorVersion", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 2. CarlifeProtocolVersionMatchStatus (sources/com/baidu/carlife/protobuf/CarlifeProtocolVersionMatchStatusProto.java)
_m_ver_match = _file_proto.message_type.add()
_m_ver_match.name = "CarlifeProtocolVersionMatchStatus"
_add_field(_m_ver_match, "matchStatus", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_ver_match, "carlifeProtocolVersion", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 3. CarlifeDeviceInfo (sources/com/baidu/carlife/protobuf/CarlifeDeviceInfoProto.java)
_m_dev = _file_proto.message_type.add()
_m_dev.name = "CarlifeDeviceInfo"
_add_field(_m_dev, "os", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "board", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "bootloader", 3, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "brand", 4, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "cpuAbi", 5, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "cpuAbi2", 6, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "device", 7, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "display", 8, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "fingerprint", 9, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "hardware", 10, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "host", 11, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "cid", 12, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "manufacturer", 13, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "model", 14, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "product", 15, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "serial", 16, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "codename", 17, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "incremental", 18, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "release", 19, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "sdk", 20, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "sdkInt", 21, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_dev, "carlifeversion", 22, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_dev, "btaddress", 23, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

# 4. CarlifeStatisticsInfo (sources/com/baidu/carlife/protobuf/CarlifeStatisticsInfoProto.java)
_m_stat = _file_proto.message_type.add()
_m_stat.name = "CarlifeStatisticsInfo"
_add_field(_m_stat, "cuid", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_stat, "versionName", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_stat, "versionCode", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_stat, "channel", 4, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_stat, "connectCount", 5, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_stat, "connectSuccessCount", 6, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_stat, "connectTime", 7, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_stat, "crashCycle", 8, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

# 5. CarlifeAuthenResult (sources/com/baidu/carlife/protobuf/CarlifeAuthenResultProto.java)
_m_auth = _file_proto.message_type.add()
_m_auth.name = "CarlifeAuthenResult"
_add_field(_m_auth, "authenResult", 1, descriptor_pb2.FieldDescriptorProto.TYPE_BOOL)

# 6. CarlifeFeatureConfig & List (sources/com/baidu/carlife/protobuf/CarlifeFeatureConfigListProto.java)
_m_fc = _file_proto.message_type.add()
_m_fc.name = "CarlifeFeatureConfig"
_add_field(_m_fc, "key", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_fc, "value", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

_m_fcl = _file_proto.message_type.add()
_m_fcl.name = "CarlifeFeatureConfigList"
_add_field(_m_fcl, "cnt", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_fcl, "featureConfig", 2, descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE,
           label=descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED, type_name="CarlifeFeatureConfig")
_add_field(_m_fcl, "huBtAudioSupport", 3, descriptor_pb2.FieldDescriptorProto.TYPE_BOOL)
_add_field(_m_fcl, "huBtName", 4, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_fcl, "huBtMAC", 5, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

# 7. CarlifeVideoEncoderInfo (sources/com/baidu/carlife/protobuf/CarlifeVideoEncoderInfoProto.java)
_m_enc = _file_proto.message_type.add()
_m_enc.name = "CarlifeVideoEncoderInfo"
_add_field(_m_enc, "width", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_enc, "height", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_enc, "frameRate", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 8. CarlifeTouchAction (sources/com/baidu/carlife/protobuf/CarlifeTouchActionProto.java)
_m_touch = _file_proto.message_type.add()
_m_touch.name = "CarlifeTouchAction"
_add_field(_m_touch, "action", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_touch, "x", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_touch, "y", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_touch, "pointerx", 4, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_touch, "pointery", 5, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 9. CarlifeCarSpeed (sources/com/baidu/carlife/protobuf/CarlifeCarSpeedProto.java)
_m_spd = _file_proto.message_type.add()
_m_spd.name = "CarlifeCarSpeed"
_add_field(_m_spd, "speed", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_spd, "timeStamp", 2, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64)

# 10. CarlifeCarHardKeyCode (sources/com/baidu/carlife/protobuf/CarlifeCarHardKeyCodeProto.java)
_m_key = _file_proto.message_type.add()
_m_key.name = "CarlifeCarHardKeyCode"
_add_field(_m_key, "keycode", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 11. CarlifeMusicInit (sources/com/baidu/carlife/protobuf/CarlifeMusicInitProto.java)
_m_mus = _file_proto.message_type.add()
_m_mus.name = "CarlifeMusicInit"
_add_field(_m_mus, "sampleRate", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_mus, "channelConfig", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_mus, "sampleFormat", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 12. CarlifeNaviNextTurnInfo (sources/com/baidu/carlife/protobuf/CarlifeNaviNextTurnInfoProto.java)
_m_hud = _file_proto.message_type.add()
_m_hud.name = "CarlifeNaviNextTurnInfo"
_add_field(_m_hud, "action", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_hud, "nextTurn", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_hud, "roadName", 3, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_hud, "totalDistance", 4, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_hud, "remainDistance", 5, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_hud, "turnIconData", 6, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES)

# 注册文件描述符并导出 Message 类
_file_desc = _pool.Add(_file_proto)

CarlifeProtocolVersion = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeProtocolVersion"])
CarlifeProtocolVersionMatchStatus = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeProtocolVersionMatchStatus"])
CarlifeDeviceInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeDeviceInfo"])
CarlifeStatisticsInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeStatisticsInfo"])
CarlifeAuthenResult = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeAuthenResult"])
CarlifeFeatureConfig = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeFeatureConfig"])
CarlifeFeatureConfigList = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeFeatureConfigList"])
CarlifeVideoEncoderInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeVideoEncoderInfo"])
CarlifeTouchAction = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeTouchAction"])
CarlifeCarSpeed = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeCarSpeed"])
CarlifeCarHardKeyCode = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeCarHardKeyCode"])
CarlifeMusicInit = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeMusicInit"])
CarlifeNaviNextTurnInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeNaviNextTurnInfo"])

