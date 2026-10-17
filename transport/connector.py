# -*- coding: utf-8 -*-
"""
CarLife 传输连接管理模块 (局域网监听与 USB AOA 双原生模式)
依据源码与官方规范：
- 局域网端口定义：sources/d/b/a/a/p/o/e/c.java:16
- 局域网 UDP 7999 广播发现：sources/d/b/a/a/p/o/e/d.java:146-160
- 手机端广播源：carlife.xiaomi_8.8.5/sources/com/baidu/carlife/core/connect/ConnectManager.java:978-989
- 手机端 AOA 管理：carlife.xiaomi_8.8.5/sources/com/baidu/carlife/core/connect/AOAConnectManager.java
- 车机端 AOA 传输：sources/d/b/a/a/p/o/c/a.java
"""

import socket
import threading
import time
import logging
from typing import Dict, Optional, Callable
from ..protocol import constants
from ..protocol.constants import ALL_CHANNELS, UDP_DISCOVERY_PORT, CHANNEL_VIDEO
from .aoa_transport import AoaManager

logger = logging.getLogger("CarLife_Connector")

class CarLifeConnector:
    """管理车机端与手机端的通信连接 (仅保留 局域网监听 与 USB AOA 两种车机原生模式)"""

    def __init__(self, on_disconnect: Optional[Callable[[str], None]] = None):
        self.sockets: Dict[int, socket.socket] = {}
        self.is_connected = False
        self.target_host = "127.0.0.1"
        self.connect_mode = "LAN"  # "LAN" 或 "AOA"
        self._udp_listener_thread: Optional[threading.Thread] = None
        self._udp_running = False
        self.aoa_manager = AoaManager()
        self.on_disconnect = on_disconnect

    # ================= 模式一：局域网监听与多通道连接 =================

    def start_lan_discovery(self, on_found_callback: Callable[[str], None]):
        """
        依据车机端 sources/d/b/a/a/p/o/e/d.java:146
        启动后台 UDP 7999 监听，等待手机端发起广播 (手机端每秒广播 'CarlifeHost')
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
                logger.info(f"[*] 局域网 UDP 广播监听已在端口 {UDP_DISCOVERY_PORT} 启动，等待手机端广播接入...")
                while self._udp_running:
                    try:
                        data, addr = udp_sock.recvfrom(1024)
                        phone_ip = addr[0]
                        logger.info(f"[+] 捕获到手机 CarLife 局域网广播 ({data[:32]!r})，来自 IP: {phone_ip}")
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

        self._udp_listener_thread = threading.Thread(target=_listen, daemon=True, name="CarLife_LAN_Discovery")
        self._udp_listener_thread.start()

    def stop_lan_discovery(self):
        """停止局域网广播监听"""
        self._udp_running = False

    def connect_all_channels(self, host: str, timeout: float = 3.0) -> bool:
        """
        连接全部 7 个 TCP 端口 (局域网直连)。
        依据 sources/d/b/a/a/p/o/e/c.java:67-71 循环建立每个通道的 Socket 连接
        """
        self.disconnect_all()
        self.target_host = host
        self.connect_mode = "LAN"
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
        self._start_aux_drainers()
        return True

    def _start_aux_drainers(self):
        """
        依据官方车机 sources/d/b/a/a/p/o/e/c.java:70 与 SocketReader 逻辑
        对非控制/非渲染辅助通道 (Channel 3: 媒体音频, Channel 4: TTS, Channel 5: VR) 启动后台静默消费守护线程
        防止手机端因向 Socket 写入 PCM/状态包无响应或 TCP 接收缓冲区堆积导致连接异常
        """
        for ch_id in (constants.CHANNEL_AUDIO, constants.CHANNEL_TTS, constants.CHANNEL_VR):
            sock = self.sockets.get(ch_id)
            if not sock:
                continue
            def _drain_loop(s=sock, cid=ch_id):
                while self.is_connected:
                    try:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                    except Exception:
                        break
            threading.Thread(target=_drain_loop, daemon=True, name=f"CarLife_Drain_{ch_id}").start()

    # ================= 模式二：USB AOA 模式 =================

    def connect_aoa(self, log_callback: Optional[Callable[[str, str], None]] = None) -> bool:
        """
        通过 USB AOA 模式与手机建立连接
        依据官方规范 6.1.1 节与 AOAConnectManager 逻辑
        """
        self.disconnect_all()
        self.connect_mode = "AOA"
        channel_ids = [ch_id for ch_id, _, _ in ALL_CHANNELS]
        client_sockets = self.aoa_manager.connect(
            channel_ids,
            log_cb=log_callback,
            on_fatal_error=self._on_aoa_fatal_error
        )
        if not client_sockets:
            self.disconnect_all()
            return False

        self.sockets = client_sockets
        self.is_connected = True
        self._start_aux_drainers()
        logger.info("[*] USB AOA 虚拟通道多路复用已就绪")
        return True

    def _on_aoa_fatal_error(self, reason: str):
        logger.warning(f"[-] AOA 底层链路异常中断 ({reason})，联动清理连接状态")
        self.disconnect_all()
        if self.on_disconnect:
            try:
                self.on_disconnect(reason)
            except Exception as e:
                logger.error(f"执行断开回调异常: {e}")

    # ================= 公共通道管理 =================

    def get_socket(self, channel: int) -> Optional[socket.socket]:
        """获取指定通道的数据 Socket (无论是 LAN TCP 还是 AOA 虚拟通道，接口完全透明一致)"""
        return self.sockets.get(channel)

    def disconnect_all(self):
        """关闭所有通道连接 (无论 LAN 还是 AOA)"""
        self.is_connected = False
        self.stop_lan_discovery()

        if self.connect_mode == "AOA":
            self.aoa_manager.disconnect()

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
