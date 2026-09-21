# -*- coding: utf-8 -*-
"""
CarLife 报文帧封包与拆包逻辑
依据源码位置：
- 报文头结构：sources/d/b/a/a/o/h/a.java:134-147, 204-228, 290-298
- 大端序整数处理：sources/c/b/k/m.java:663-666, 1188-1205
- Socket 流分块传输：sources/d/b/a/a/o/i/f/c.java:109-118, 130-135
"""

import struct
import socket
from typing import Tuple, Optional
from .constants import CHANNEL_CMD, CHANNEL_TOUCH

def get_header_size(channel: int) -> int:
    """
    依据 sources/d/b/a/a/o/h/a.java:134
    Channel 1 (控制) 和 Channel 6 (触控) 头部长度为 8 字节；
    其他通道 (音视频、数据) 头部长度为 12 字节。
    """
    return 8 if channel in (CHANNEL_CMD, CHANNEL_TOUCH) else 12

def pack_message(channel: int, service_type: int, payload: bytes = b'', seq_or_ts: int = 0) -> bytes:
    """
    依据 sources/d/b/a/a/o/h/a.java:212-218 及 y() 方法:
    打包为 CarLife 报文帧（全大端序 Big-Endian）：
    - Channel 1 / 6: [uint16 len][uint16 reserved][uint32 service_type] + payload
    - 其他通道:      [uint32 len][uint32 seq_or_ts][uint32 service_type] + payload
    """
    payload_len = len(payload)
    if channel in (CHANNEL_CMD, CHANNEL_TOUCH):
        header = struct.pack(">HHI", payload_len, 0, service_type)
    else:
        header = struct.pack(">III", payload_len, seq_or_ts, service_type)
    return header + payload

def unpack_header(channel: int, header_bytes: bytes) -> Tuple[int, int, int]:
    """
    依据 sources/d/b/a/a/o/h/a.java:140-147 及 m() 方法:
    解析包头字节：
    返回 (payload_len, extra_field, service_type)
    - Channel 1 / 6 (8 bytes): extra_field 为保留字段 0
    - 其他通道 (12 bytes): extra_field 为时间戳或序列号
    """
    if channel in (CHANNEL_CMD, CHANNEL_TOUCH):
        if len(header_bytes) < 8:
            raise ValueError(f"Header too short for channel {channel}: {len(header_bytes)} < 8")
        payload_len, reserved, service_type = struct.unpack(">HHI", header_bytes[:8])
        return payload_len, reserved, service_type
    else:
        if len(header_bytes) < 12:
            raise ValueError(f"Header too short for channel {channel}: {len(header_bytes)} < 12")
        payload_len, seq_ts, service_type = struct.unpack(">III", header_bytes[:12])
        return payload_len, seq_ts, service_type

def recv_exact(sock: socket.socket, num_bytes: int) -> Optional[bytes]:
    """
    确保从 TCP Socket 中完整读取指定字节数（防止 TCP 分包粘包）。
    返回 bytes，如果连接断开则返回 None。
    """
    buf = bytearray()
    while len(buf) < num_bytes:
        try:
            chunk = sock.recv(num_bytes - len(buf))
            if not chunk:
                return None
            buf.extend(chunk)
        except (socket.timeout, BlockingIOError):
            continue
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            return None
    return bytes(buf)

def read_message(sock: socket.socket, channel: int) -> Optional[Tuple[int, bytes]]:
    """
    从指定通道的 Socket 完整读取一个 CarLife 报文。
    返回 (service_type, payload)，若连接断开则返回 None。
    """
    hdr_size = get_header_size(channel)
    hdr_data = recv_exact(sock, hdr_size)
    if hdr_data is None:
        return None
    payload_len, _, service_type = unpack_header(channel, hdr_data)
    if payload_len > 0:
        payload = recv_exact(sock, payload_len)
        if payload is None:
            return None
    else:
        payload = b''
    return service_type, payload
