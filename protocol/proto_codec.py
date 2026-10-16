# -*- coding: utf-8 -*-
"""
CarLife 协议 Protobuf 消息编解码器
依据源码位置：
- sources/com/baidu/carlife/protobuf/*.java
- 通信协议规范：《百度CarLife车机手机互联方案接入详细指南V2.1.1.pdf》

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

# 8. CarlifeVideoFrameRate (sources/com/baidu/carlife/protobuf/CarlifeVideoFrameRateProto.java)
_m_vfr = _file_proto.message_type.add()
_m_vfr.name = "CarlifeVideoFrameRate"
_add_field(_m_vfr, "frameRate", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 9. CarlifeTouchAction (sources/com/baidu/carlife/protobuf/CarlifeTouchActionProto.java)
_m_touch = _file_proto.message_type.add()
_m_touch.name = "CarlifeTouchAction"
_add_field(_m_touch, "action", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_touch, "x", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_touch, "y", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_touch, "pointerx", 4, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_touch, "pointery", 5, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 10. CarlifeCarSpeed (sources/com/baidu/carlife/protobuf/CarlifeCarSpeedProto.java)
_m_spd = _file_proto.message_type.add()
_m_spd.name = "CarlifeCarSpeed"
_add_field(_m_spd, "speed", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_spd, "timeStamp", 2, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64)

# 11. CarlifeCarHardKeyCode (sources/com/baidu/carlife/protobuf/CarlifeCarHardKeyCodeProto.java)
_m_key = _file_proto.message_type.add()
_m_key.name = "CarlifeCarHardKeyCode"
_add_field(_m_key, "keycode", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 12. CarlifeCarGps (sources/com/baidu/carlife/protobuf/CarlifeCarGpsProto.java)
_m_gps = _file_proto.message_type.add()
_m_gps.name = "CarlifeCarGps"
_add_field(_m_gps, "antennaState", 1, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "signalQuality", 2, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "latitude", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_gps, "longitude", 4, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_gps, "height", 5, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_gps, "speed", 6, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "heading", 7, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "year", 8, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "month", 9, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "day", 10, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "hrs", 11, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "min", 12, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "sec", 13, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "fix", 14, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "hdop", 15, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "pdop", 16, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "vdop", 17, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "satsUsed", 18, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "satsVisible", 19, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "horPosError", 20, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "vertPosError", 21, descriptor_pb2.FieldDescriptorProto.TYPE_UINT32)
_add_field(_m_gps, "northSpeed", 22, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_gps, "eastSpeed", 23, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_gps, "vertSpeed", 24, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_gps, "timeStamp", 25, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64)

# 13. CarlifeGyroscope (sources/com/baidu/carlife/protobuf/CarlifeGyroscopeProto.java)
_m_gyro = _file_proto.message_type.add()
_m_gyro.name = "CarlifeGyroscope"
_add_field(_m_gyro, "gyroType", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_gyro, "gyroX", 2, descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_m_gyro, "gyroy", 3, descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_m_gyro, "gyroZ", 4, descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_m_gyro, "timeStamp", 5, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64)

# 14. CarlifeAcceleration (sources/com/baidu/carlife/protobuf/CarlifeAccelerationProto.java)
_m_acc = _file_proto.message_type.add()
_m_acc.name = "CarlifeAcceleration"
_add_field(_m_acc, "accX", 1, descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_m_acc, "accY", 2, descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_m_acc, "accZ", 3, descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE)
_add_field(_m_acc, "timeStamp", 4, descriptor_pb2.FieldDescriptorProto.TYPE_UINT64)

# 15. CarlifeOil (sources/com/baidu/carlife/protobuf/CarlifeOilProto.java)
_m_oil = _file_proto.message_type.add()
_m_oil.name = "CarlifeOil"
_add_field(_m_oil, "level", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_oil, "range", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_oil, "lowFuleWarning", 3, descriptor_pb2.FieldDescriptorProto.TYPE_BOOL)

# 16. CarlifeGearInfo (sources/com/baidu/carlife/protobuf/CarlifeGearInfoProto.java)
_m_gear = _file_proto.message_type.add()
_m_gear.name = "CarlifeGearInfo"
_add_field(_m_gear, "gear", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 17. CarlifeModuleStatus & List (sources/com/baidu/carlife/protobuf/CarlifeModuleStatusListProto.java)
_m_ms = _file_proto.message_type.add()
_m_ms.name = "CarlifeModuleStatus"
_add_field(_m_ms, "moduleID", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_ms, "statusID", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

_m_msl = _file_proto.message_type.add()
_m_msl.name = "CarlifeModuleStatusList"
_add_field(_m_msl, "cnt", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_msl, "moduleStatus", 2, descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE,
           label=descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED, type_name="CarlifeModuleStatus")

# 18. CarlifeVehicleInfo & List (sources/com/baidu/carlife/protobuf/CarlifeVehicleInfoListProto.java)
_m_vi = _file_proto.message_type.add()
_m_vi.name = "CarlifeVehicleInfo"
_add_field(_m_vi, "moduleID", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_vi, "flag", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_vi, "frequency", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_vi, "supportFlag", 4, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

_m_vil = _file_proto.message_type.add()
_m_vil.name = "CarlifeVehicleInfoList"
_add_field(_m_vil, "cnt", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_vil, "vehicleInfo", 2, descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE,
           label=descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED, type_name="CarlifeVehicleInfo")

# 19. CarlifeSubscribeMobileCarLifeInfo & List (sources/com/baidu/carlife/protobuf/CarlifeSubscribeMobileCarLifeInfoListProto.java)
_m_smi = _file_proto.message_type.add()
_m_smi.name = "CarlifeSubscribeMobileCarLifeInfo"
_add_field(_m_smi, "moduleID", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_smi, "supportFlag", 2, descriptor_pb2.FieldDescriptorProto.TYPE_BOOL)
_add_field(_m_smi, "frequency", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

_m_smil = _file_proto.message_type.add()
_m_smil.name = "CarlifeSubscribeMobileCarLifeInfoList"
_add_field(_m_smil, "cnt", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_smil, "subscribemobileCarLifeInfo", 2, descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE,
           label=descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED, type_name="CarlifeSubscribeMobileCarLifeInfo")

# 20. CarlifeNaviNextTurnInfo (sources/com/baidu/carlife/protobuf/CarlifeNaviNextTurnInfoProto.java)
_m_hud = _file_proto.message_type.add()
_m_hud.name = "CarlifeNaviNextTurnInfo"
_add_field(_m_hud, "action", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_hud, "nextTurn", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_hud, "roadName", 3, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_hud, "totalDistance", 4, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_hud, "remainDistance", 5, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_hud, "turnIconData", 6, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES)

# 21. CarlifeNaviAssitantGuideInfo (sources/com/baidu/carlife/protobuf/CarlifeNaviAssitantGuideInfoProto.java)
_m_assist = _file_proto.message_type.add()
_m_assist.name = "CarlifeNaviAssitantGuideInfo"
_add_field(_m_assist, "action", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_assist, "assistantType", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_assist, "trafficSignType", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_assist, "totalDistance", 4, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_assist, "remainDistance", 5, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_assist, "cameraSpeed", 6, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 22. CarlifeMediaInfo (sources/com/baidu/carlife/protobuf/CarlifeMediaInfoProto.java)
_m_media = _file_proto.message_type.add()
_m_media.name = "CarlifeMediaInfo"
_add_field(_m_media, "source", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_media, "song", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_media, "artist", 3, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_media, "album", 4, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_media, "albumArt", 5, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES)
_add_field(_m_media, "duration", 6, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_media, "playlistNum", 7, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_media, "songId", 8, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_media, "mode", 9, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 23. CarlifeMediaProgressBar (sources/com/baidu/carlife/protobuf/CarlifeMediaProgressBarProto.java)
_m_mpb = _file_proto.message_type.add()
_m_mpb.name = "CarlifeMediaProgressBar"
_add_field(_m_mpb, "progressBar", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_mpb, "mediaLyric", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

# 24. CarlifeMusicInit (sources/com/baidu/carlife/protobuf/CarlifeMusicInitProto.java)
_m_mus = _file_proto.message_type.add()
_m_mus.name = "CarlifeMusicInit"
_add_field(_m_mus, "sampleRate", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_mus, "channelConfig", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_mus, "sampleFormat", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 25. CarlifeTTSInit (sources/com/baidu/carlife/protobuf/CarlifeTTSInitProto.java)
_m_tts = _file_proto.message_type.add()
_m_tts.name = "CarlifeTTSInit"
_add_field(_m_tts, "sampleRate", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_tts, "channelConfig", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_tts, "sampleFormat", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 26. CarlifeBTHfpRequest (sources/com/baidu/carlife/protobuf/CarlifeBTHfpRequestProto.java)
_m_bt_req = _file_proto.message_type.add()
_m_bt_req.name = "CarlifeBTHfpRequest"
_add_field(_m_bt_req, "command", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_bt_req, "phoneNum", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_bt_req, "dtmfCode", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 27. CarlifeBTHfpIndication (sources/com/baidu/carlife/protobuf/CarlifeBTHfpIndicationProto.java)
_m_bt_ind = _file_proto.message_type.add()
_m_bt_ind.name = "CarlifeBTHfpIndication"
_add_field(_m_bt_ind, "state", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_bt_ind, "phoneNum", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_bt_ind, "phoneName", 3, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_bt_ind, "address", 4, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

# 28. CarlifeBTHfpConnection (sources/com/baidu/carlife/protobuf/CarlifeBTHfpConnectionProto.java)
_m_bt_conn = _file_proto.message_type.add()
_m_bt_conn.name = "CarlifeBTHfpConnection"
_add_field(_m_bt_conn, "state", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_bt_conn, "address", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_bt_conn, "name", 3, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

# 29. CarlifeBTHfpResponse (sources/com/baidu/carlife/protobuf/CarlifeBTHfpResponseProto.java)
_m_bt_resp = _file_proto.message_type.add()
_m_bt_resp.name = "CarlifeBTHfpResponse"
_add_field(_m_bt_resp, "status", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_bt_resp, "cmd", 2, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_bt_resp, "dtmfCode", 3, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 30. CarlifeAuthenRequest & Response (sources/com/baidu/carlife/protobuf/CarlifeAuthenRequestProto.java)
_m_auth_req = _file_proto.message_type.add()
_m_auth_req.name = "CarlifeAuthenRequest"
_add_field(_m_auth_req, "randomValue", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

_m_auth_resp = _file_proto.message_type.add()
_m_auth_resp.name = "CarlifeAuthenResponse"
_add_field(_m_auth_resp, "encryptValue", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

# 31. CarlifeBTPairInfo (sources/com/baidu/carlife/protobuf/CarlifeBTPairInfoProto.java)
_m_bt_pair = _file_proto.message_type.add()
_m_bt_pair.name = "CarlifeBTPairInfo"
_add_field(_m_bt_pair, "address", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_bt_pair, "passKey", 2, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_bt_pair, "name", 3, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)
_add_field(_m_bt_pair, "status", 4, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)
_add_field(_m_bt_pair, "uuid", 5, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

# 32. CarlifeConnectTimeSync (sources/com/baidu/carlife/protobuf/CarlifeConnectTimeSyncProto.java)
_m_time_sync = _file_proto.message_type.add()
_m_time_sync.name = "CarlifeConnectTimeSync"
_add_field(_m_time_sync, "timeStamp", 1, descriptor_pb2.FieldDescriptorProto.TYPE_INT32)

# 33. CarlifeErrorCode (sources/com/baidu/carlife/protobuf/CarlifeErrorCodeProto.java)
_m_err = _file_proto.message_type.add()
_m_err.name = "CarlifeErrorCode"
_add_field(_m_err, "errorCode", 1, descriptor_pb2.FieldDescriptorProto.TYPE_STRING)

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
CarlifeVideoFrameRate = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeVideoFrameRate"])
CarlifeTouchAction = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeTouchAction"])
CarlifeCarSpeed = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeCarSpeed"])
CarlifeCarHardKeyCode = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeCarHardKeyCode"])
CarlifeCarGps = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeCarGps"])
CarlifeGyroscope = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeGyroscope"])
CarlifeAcceleration = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeAcceleration"])
CarlifeOil = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeOil"])
CarlifeGearInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeGearInfo"])
CarlifeModuleStatus = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeModuleStatus"])
CarlifeModuleStatusList = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeModuleStatusList"])
CarlifeVehicleInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeVehicleInfo"])
CarlifeVehicleInfoList = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeVehicleInfoList"])
CarlifeSubscribeMobileCarLifeInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeSubscribeMobileCarLifeInfo"])
CarlifeSubscribeMobileCarLifeInfoList = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeSubscribeMobileCarLifeInfoList"])
CarlifeNaviNextTurnInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeNaviNextTurnInfo"])
CarlifeNaviAssitantGuideInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeNaviAssitantGuideInfo"])
CarlifeMediaInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeMediaInfo"])
CarlifeMediaProgressBar = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeMediaProgressBar"])
CarlifeMusicInit = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeMusicInit"])
CarlifeTTSInit = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeTTSInit"])
CarlifeBTHfpRequest = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeBTHfpRequest"])
CarlifeBTHfpIndication = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeBTHfpIndication"])
CarlifeBTHfpConnection = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeBTHfpConnection"])
CarlifeBTHfpResponse = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeBTHfpResponse"])
CarlifeAuthenRequest = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeAuthenRequest"])
CarlifeAuthenResponse = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeAuthenResponse"])
CarlifeBTPairInfo = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeBTPairInfo"])
CarlifeConnectTimeSync = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeConnectTimeSync"])
CarlifeErrorCode = message_factory.GetMessageClass(_file_desc.message_types_by_name["CarlifeErrorCode"])
