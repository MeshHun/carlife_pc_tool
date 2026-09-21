# -*- coding: utf-8 -*-
"""
CarLife 网络连接管理模块
依据源码位置：
- 端口定义：sources/d/b/a/a/p/o/e/c.java:16
- UDP 7999 广播发现：sources/d/b/a/a/p/o/e/d.java:146-160
- Socket 通信读写：sources/d/b/a/a/o/i/f/c.java:79-100
"""

import socket
import subprocess
import threading
import time
import logging
from typing import Dict, Optional, Callable
from ..protocol import constants
from ..protocol.constants import ALL_CHANNELS, UDP_DISCOVERY_PORT, CHANNEL_VIDEO

logger = logging.getLogger("CarLife_Connector")

class CarLifeConnector:
    """管理与手机端的 7 个 TCP 通道连接及 ADB 端口转发/Wi-Fi 发现"""

    def __init__(self):
        self.sockets: Dict[int, socket.socket] = {}
        self.is_connected = False
        self.target_host = "127.0.0.1"
        self._udp_listener_thread: Optional[threading.Thread] = None
        self._udp_running = False

    @staticmethod
    def check_adb_devices() -> list:
        """检查通过 USB 连接并开启了调试的 Android 设备"""
        try:
            res = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
            lines = res.stdout.strip().splitlines()[1:]
            devices = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
            return devices
        except Exception as e:
            logger.warning(f"检测 ADB 设备失败: {e}")
            return []

    @staticmethod
    def setup_adb_forward() -> bool:
        """为 CarLife 的 7 个通道自动建立 ADB 端口映射"""
        devices = CarLifeConnector.check_adb_devices()
        if not devices:
            logger.warning("未检测到通过 USB 连接的 Android 设备，请确保已开启 USB 调试")
            return False

        logger.info(f"检测到设备: {devices[0]}，正在设置端口映射...")
        try:
            for ch_id, port, desc in ALL_CHANNELS:
                cmd = ["adb", "forward", f"tcp:{port}", f"tcp:{port}"]
                subprocess.run(cmd, check=True, capture_output=True, timeout=3)
                logger.info(f"  [ADB forward] {port} -> {port} ({desc})")
            return True
        except Exception as e:
            logger.error(f"设置 ADB 端口转发失败: {e}")
            return False

    def start_wifi_discovery(self, on_found_callback: Callable[[str], None]):
        """
        依据 sources/d/b/a/a/p/o/e/d.java:146
        启动后台 UDP 7999 监听，等待手机端发起广播发现
        """
        if self._udp_running:
            return

        def _listen():
            self._udp_running = True
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                udp_sock.bind(("0.0.0.0", UDP_DISCOVERY_PORT))
                udp_sock.settimeout(2.0)
                logger.info(f"[*] UDP 广播监听已在端口 {UDP_DISCOVERY_PORT} 启动，等待手机端连接...")
                while self._udp_running:
                    try:
                        data, addr = udp_sock.recvfrom(1024)
                        phone_ip = addr[0]
                        logger.info(f"[+] 捕获到手机 CarLife Wi-Fi 广播，来自 IP: {phone_ip}")
                        on_found_callback(phone_ip)
                        break
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self._udp_running:
                            logger.error(f"UDP 接收异常: {e}")
                        break
            except Exception as e:
                logger.error(f"绑定 UDP 7999 端口失败: {e}")
            finally:
                udp_sock.close()
                self._udp_running = False

        self._udp_listener_thread = threading.Thread(target=_listen, daemon=True, name="CarLife_UDP_Discovery")
        self._udp_listener_thread.start()

    def stop_wifi_discovery(self):
        self._udp_running = False

    def connect_all_channels(self, host: str, timeout: float = 3.0) -> bool:
        """
        连接全部 7 个 TCP 端口。
        依据 sources/d/b/a/a/p/o/e/c.java:67-71 循环建立每个通道的 Socket 连接
        """
        self.disconnect_all()
        self.target_host = host
        logger.info(f"[*] 正在连接 CarLife 手机端通道 (目标: {host})...")

        # 优先连接关键通道：Channel 1 (控制)、Channel 2 (视频)、Channel 6 (触控)
        for ch_id, port, desc in ALL_CHANNELS:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # 开启 TCP_NODELAY，禁用 Nagle 算法，降低数据包传输排队延迟
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                # 针对视频通道扩容 TCP 接收缓冲区至 2MB，防止高分辨率/高码率大 I 帧瞬间打满缓冲区
                if ch_id == constants.CHANNEL_VIDEO:
                    try:
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 * 1024 * 1024)
                    except Exception as e:
                        logger.warning(f"设置视频通道接收缓冲区失败: {e}")

                s.settimeout(timeout)
                s.connect((host, port))
                s.settimeout(None)  # 连接成功后设为阻塞或长超时
                self.sockets[ch_id] = s
                logger.info(f"  [+] 通道 {ch_id} ({desc}) 连接成功: {host}:{port}")
            except Exception as e:
                logger.warning(f"  [-] 通道 {ch_id} ({desc}, port {port}) 连接失败: {e}")
                # Channel 1 是生命线，必须成功
                if ch_id == 1:
                    logger.error("控制通道 (Channel 1) 连接失败，连接终止")
                    self.disconnect_all()
                    return False

        self.is_connected = True
        return True

    def get_socket(self, channel: int) -> Optional[socket.socket]:
        return self.sockets.get(channel)

    def disconnect_all(self):
        """关闭所有通道 Socket"""
        self.is_connected = False
        for ch_id, sock in list(self.sockets.items()):
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                sock.close()
            except Exception:
                pass
        self.sockets.clear()
        logger.info("[*] 所有通道已断开")
