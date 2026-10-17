# -*- coding: utf-8 -*-
"""
CarLife USB AOA (Android Open Accessory) 传输与多路复用模块
依据源码与官方规范：
- 规范文档：《百度CarLife车机手机互联方案接入详细指南V2.1.1.pdf》第 6.1.1 节
- 手机端过滤参数：carlife.xiaomi_8.8.5/resources/res/xml/accessory_filter.xml
- 手机端 AOA 连接管理：com.baidu.carlife.core.connect.AOAConnectManager
- 手机端多路复用读写：AoaReadTransport.java / AoaWriteTransport.java
- 车机端 AOA 实现：d.b.a.a.p.o.c.a.java
"""

import os
import sys
import time
import struct
import socket
import select
import logging
import threading
from typing import Dict, Tuple, Optional, Callable, List

logger = logging.getLogger("CarLife_AOA")

# Google AOA 厂商 ID 与配件模式产品 ID 列表
AOA_VID = 0x18D1
AOA_PIDS = (0x2D00, 0x2D01, 0x2D02, 0x2D03, 0x2D04, 0x2D05)

# AOA 协议控制传输指令编号
AOA_GET_PROTOCOL = 51
AOA_SEND_STRING = 52
AOA_START_ACCESSORY = 53

# USB Vendor 控制传输请求类型
REQ_VENDOR_IN = 0xC0   # Device-to-Host, Vendor, Device
REQ_VENDOR_OUT = 0x40  # Host-to-Device, Vendor, Device

# 依据 accessory_filter.xml 定义的配件认证字符串 (精准匹配)
# <usb-accessory manufacturer="Baidu" model="CarLife" version="1.0.0"/>
ACCESSORY_STRINGS = [
    "Baidu",                       # 0: Manufacturer
    "CarLife",                     # 1: Model Name
    "Baidu CarLife",               # 2: Description (车机原生反编译: "Baidu CarLife")
    "1.0.0",                       # 3: Version
    "http://carlife.baidu.com/",   # 4: URI (车机原生反编译: "http://carlife.baidu.com/")
    "0720SerialNo.",               # 5: Serial Number (车机原生反编译: "0720SerialNo.")
]

def get_pyusb_backend():
    """获取可用的 PyUSB 后端 (优先使用系统 libusb-1.0，自动适配 Windows 环境)"""
    try:
        import usb.core
        import usb.backend.libusb1

        # 1. 尝试默认 libusb1
        be = usb.backend.libusb1.get_backend()
        if be is not None:
            return be

        # 2. 尝试从 Python 安装的 libusb 运行时包中加载 dll
        try:
            import libusb
            libusb_dir = os.path.dirname(libusb.__file__)
            candidates = [
                os.path.join(libusb_dir, "_platform", "windows", "x86_64", "libusb-1.0.dll"),
                os.path.join(libusb_dir, "_platform", "windows", "x86", "libusb-1.0.dll"),
                os.path.join(libusb_dir, "libusb-1.0.dll"),
            ]
            for p in candidates:
                if os.path.exists(p):
                    be = usb.backend.libusb1.get_backend(find_library=lambda x, p=p: p)
                    if be is not None:
                        logger.info(f"成功加载 libusb 运行时: {p}")
                        return be
        except Exception as e:
            logger.debug(f"从 libusb 包加载 dll 失败: {e}")

        # 3. 降级尝试 libusb0
        import usb.backend.libusb0
        be0 = usb.backend.libusb0.get_backend()
        if be0 is not None:
            return be0
    except Exception as e:
        logger.error(f"初始化 PyUSB 后端异常: {e}")

    return None


def reset_aoa_device_pnp() -> bool:
    """
    通过 Windows 原生 pnputil 工具快速重启 Android AOA 复合设备 (VID 0x18D1, PID 0x2D01 / 0x2D00)，
    促使 Android 手机在免拔插 USB 数据线的前提下，硬件脱离 Accessory 模式并重枚举回普通模式 (0x4ee7)。
    """
    import subprocess
    try:
        out = subprocess.check_output(
            "pnputil /enum-devices /connected /class USB",
            shell=True,
            timeout=3
        ).decode("gbk", errors="ignore")
        for line in out.splitlines():
            line = line.strip()
            if "USB\\VID_18D1&PID_2D01" in line.upper() or "USB\\VID_18D1&PID_2D00" in line.upper():
                parts = line.split(":")
                if len(parts) >= 2:
                    inst_id = parts[-1].strip()
                    logger.info(f"[*] 发现 AOA USB 复合设备 ({inst_id})，正在通过 Windows PnP 触发端口电源复位...")
                    subprocess.run(
                        f'pnputil /restart-device "{inst_id}"',
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    )
                    return True
    except Exception as e:
        logger.debug(f"PnP 重置 AOA 设备异常: {e}")
    return False


class AoaTransportSession:
    """
    管理单个 AOA 物理链路及其 7 个虚拟 Socket 通道。
    依据规范 6.1.1.5 节：
    通过 socketpair 创建 7 组虚拟通道，上层与底层完全解耦；
    后台线程在 USB Bulk 端点与 7 个 Socket 之间进行 8 字节 AOA 协议包的封包与解包转发。
    """

    def __init__(self, dev, ep_in, ep_out, on_fatal_error: Optional[Callable[[str], None]] = None):
        self.dev = dev
        self.ep_in = ep_in
        self.ep_out = ep_out
        self.on_fatal_error = on_fatal_error
        self.is_running = False

        # 通道 ID -> (client_socket, engine_socket)
        # client_socket 返回给上层模块 (StateMachine/VideoReceiver/TouchSender 等)
        # engine_socket 由内部 Mux/Demux 线程监听和读写
        self.channel_pairs: Dict[int, Tuple[socket.socket, socket.socket]] = {}
        self.engine_to_channel: Dict[socket.socket, int] = {}

        self._rx_thread: Optional[threading.Thread] = None
        self._tx_thread: Optional[threading.Thread] = None
        self._write_lock = threading.RLock()

    def start(self, channel_ids: List[int]) -> Dict[int, socket.socket]:
        """为指定的通道建立 SocketPair 并启动数据转发"""
        client_sockets = {}
        for ch_id in channel_ids:
            s_client, s_engine = socket.socketpair()
            # 开启低延迟配置
            try:
                s_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s_engine.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except Exception:
                pass
            s_engine.setblocking(False)

            self.channel_pairs[ch_id] = (s_client, s_engine)
            self.engine_to_channel[s_engine] = ch_id
            client_sockets[ch_id] = s_client

        self.is_running = True

        # 启动接收线程 (Bulk IN -> Demux -> 剥除 8B AOA 头 -> engine_socket)
        self._rx_thread = threading.Thread(target=self._rx_worker, daemon=True, name="CarLife_AOA_Rx")
        self._rx_thread.start()

        # 启动发送线程 (engine_socket -> 添加 8B AOA 头 -> Mux -> Bulk OUT)
        self._tx_thread = threading.Thread(target=self._tx_worker, daemon=True, name="CarLife_AOA_Tx")
        self._tx_thread.start()

        logger.info(f"[AOA] 通道多路复用引擎已就绪，已分配 {len(channel_ids)} 个虚拟通道")
        return client_sockets

    def _handle_fatal_error(self, reason: str):
        """底层 USB 传输发生致命异常（对端断开/写入超时），立刻终止会话并关闭所有通道，阻止无脑重发"""
        with self._write_lock:
            if not self.is_running:
                return
            self.is_running = False

        logger.warning(f"[AOA] 底层链路致命中断: {reason}，立即销毁所有虚拟通道")

        # 强制关闭所有 SocketPair，使上层的读写线程（如 state_machine、video_receiver 等）立刻收到 EOF 或 OSError 并终止
        for ch_id, (s_c, s_e) in list(self.channel_pairs.items()):
            try:
                s_c.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s_c.close()
            except Exception:
                pass
            try:
                s_e.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s_e.close()
            except Exception:
                pass
        self.channel_pairs.clear()
        self.engine_to_channel.clear()

        # 触发上层致命断开回调
        if self.on_fatal_error:
            try:
                self.on_fatal_error(reason)
            except Exception as ex:
                logger.error(f"[AOA] 调用断开回调异常: {ex}")

    def _rx_worker(self):
        """
        后台循环从 USB Bulk IN 读取，按 8 字节 AOA 协议头解复用：
        [Channel ID: 4B 大端][Msg Len: 4B 大端] + [CarLife Msg: Msg Len 字节]
        剥离 AOA 头后将原始 CarLife 报文送入对应通道的 engine_socket
        """
        rx_buf = bytearray()
        logger.info("[AOA Rx] 接收解复用线程启动")

        while self.is_running:
            try:
                # 尝试从 USB Bulk 端点拉取数据块 (最大 16KB，超时 500ms)
                chunk = self.ep_in.read(16384, timeout=500)
                if chunk:
                    rx_buf.extend(chunk)
            except Exception as e:
                # 超时无数据属于正常心跳间歇
                err_str = str(e)
                if "timeout" in err_str.lower() or "timed out" in err_str.lower():
                    continue
                if self.is_running:
                    logger.error(f"[AOA Rx] USB Bulk IN 读取致命异常: {e}")
                    self._handle_fatal_error(f"Bulk IN 读异常: {e}")
                break

            # 循环解析缓冲区中的完整 AOA 包
            while len(rx_buf) >= 8:
                ch_id, msg_len = struct.unpack(">II", rx_buf[:8])

                # 校验通道有效性 (1~7)
                if ch_id < 1 or ch_id > 7 or msg_len < 0 or msg_len > 67108864:
                    logger.error(f"[AOA Rx] 非法 AOA 报文: channel={ch_id}, msg_len={msg_len}，清空缓冲区重同步")
                    rx_buf.clear()
                    break

                if len(rx_buf) < 8 + msg_len:
                    # 数据尚未完整，等待下次继续接收
                    break

                # 提取完整的 CarLife 消息载荷 (剥离 8 字节 AOA 头)
                payload = bytes(rx_buf[8 : 8 + msg_len])
                del rx_buf[: 8 + msg_len]

                # 分发给对应通道的虚拟 Socket
                if ch_id in self.channel_pairs:
                    _, s_engine = self.channel_pairs[ch_id]
                    try:
                        s_engine.sendall(payload)
                    except (BlockingIOError, OSError) as e:
                        err_no = getattr(e, "winerror", None) or getattr(e, "errno", None)
                        # 10035 (WSAEWOULDBLOCK), 11 (EAGAIN), 35 (EWOULDBLOCK) 表示上层未读取该通道导致本地缓冲区已满
                        if err_no in (10035, 11, 35) or isinstance(e, BlockingIOError):
                            # 上层暂未消费该通道（如当前未实现音频播放的通道 3 媒体音频），静默丢弃多余帧，避免刷屏
                            pass
                        else:
                            logger.warning(f"[AOA Rx] 向通道 {ch_id} 虚拟 Socket 写入失败: {e}")
                    except Exception as e:
                        logger.warning(f"[AOA Rx] 向通道 {ch_id} 虚拟 Socket 写入失败: {e}")
                else:
                    logger.debug(f"[AOA Rx] 忽略未监听通道 {ch_id} 的数据，长度: {msg_len}")

        logger.info("[AOA Rx] 接收解复用线程退出")

    def _tx_worker(self):
        """
        后台监听 7 个通道的虚拟 Socket 发送请求，添加 8 字节 AOA 头后合并写入 USB Bulk OUT：
        [Channel ID: 4B 大端][Msg Len: 4B 大端] + [CarLife Msg]
        """
        engine_socks = list(self.engine_to_channel.keys())
        logger.info("[AOA Tx] 发送多路复用线程启动")

        while self.is_running:
            try:
                readable, _, _ = select.select(engine_socks, [], [], 0.05)
                for s in readable:
                    if not self.is_running:
                        break
                    ch_id = self.engine_to_channel.get(s)
                    if not ch_id:
                        continue
                    try:
                        data = s.recv(16384)
                        if not data:
                            continue
                        self.send_packet(ch_id, data)
                    except BlockingIOError:
                        continue
                    except Exception as e:
                        if self.is_running:
                            logger.warning(f"[AOA Tx] 从通道 {ch_id} 读取发送数据异常: {e}")
            except Exception as e:
                if self.is_running:
                    logger.error(f"[AOA Tx] Select 异常: {e}")
                break

        logger.info("[AOA Tx] 发送多路复用线程退出")

    def send_packet(self, channel_id: int, payload: bytes):
        """线程安全地向 USB Bulk OUT 写入一个完整的 AOA 包"""
        with self._write_lock:
            if not self.is_running:
                return
            header = struct.pack(">II", channel_id, len(payload))
            try:
                # 依据百度官方接入指南 6.1.1.3 节要求：
                # “车机端在发送AOA数据时需要注意将8个字节的AOA Head和CarLife Msg单独分开发送。”
                # 手机端使用两次独立的 read() 获取 AOA 头和消息载荷，此处必须分两次 USB Bulk 传输写入
                self.ep_out.write(header, timeout=1000)
                if payload:
                    self.ep_out.write(payload, timeout=1000)
            except Exception as e:
                logger.error(f"[AOA Tx] USB Bulk OUT 写入通道 {channel_id} 失败: {e}，判定连接已断开！")
                self._handle_fatal_error(f"Bulk OUT 写入通道 {channel_id} 失败: {e}")

    def close(self):
        """关闭 AOA 会话，释放所有资源"""
        if not self.is_running and not self.channel_pairs:
            return
        self.is_running = False
        # 关闭所有 SocketPair
        for ch_id, (s_c, s_e) in list(self.channel_pairs.items()):
            try:
                s_c.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s_c.close()
            except Exception:
                pass
            try:
                s_e.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s_e.close()
            except Exception:
                pass
        self.channel_pairs.clear()
        self.engine_to_channel.clear()

        # 1. 主动断开时向手机发送 AOA 退出指令帧 (非法的 channel ID = 0xFFFFFFFF)
        # 依据手机端源码 AoaReadTransport.java:56-58 与 Carwith r9/d.java:110：
        # 手机端读到非法 channelId 后会立即抛出 IOException 异常并退出 AOAReadThread，主动切断连接并 uninit！
        try:
            exit_frame = struct.pack(">II", 0xFFFFFFFF, 0)
            self.ep_out.write(exit_frame, timeout=500)
        except Exception as e:
            logger.debug(f"[AOA] 发送断开退出帧异常 (可能链路已断): {e}")

        # 2. 对 USB 设备执行 Bus Reset，促使 Android 硬件脱离 Accessory 模式重新枚举，广播 USB_ACCESSORY_DETACHED
        try:
            self.dev.reset()
            logger.info("[AOA] 已向 Android 设备发送 USB Bus Reset 信号")
        except Exception as e:
            logger.debug(f"[AOA] USB 设备 reset 异常: {e}")

        # 3. 释放 USB 接口
        try:
            import usb.util
            usb.util.dispose_resources(self.dev)
        except Exception:
            pass

        # 4. 触发 Windows PnP 重启 USB 复合设备，迫使 Android 手机脱离 2D01 恢复普通模式 (4EE7)，免拔线！
        reset_aoa_device_pnp()

        logger.info("[AOA] 会话已安全关闭并复位 USB 端口")


class AoaManager:
    """AOA 设备检测、握手切换与连接生命周期管理器"""

    def __init__(self):
        self.backend = get_pyusb_backend()
        self.active_session: Optional[AoaTransportSession] = None

    def is_backend_available(self) -> bool:
        return self.backend is not None

    def find_all_usb_devices(self) -> list:
        """枚举所有连接到本机的 USB 设备"""
        if not self.backend:
            return []
        try:
            import usb.core
            return list(usb.core.find(find_all=True, backend=self.backend))
        except Exception as e:
            logger.error(f"枚举 USB 设备失败: {e}")
            return []

    def find_aoa_device(self):
        """查找当前已处于 Google AOA 模式的设备 (VID 0x18D1, PID 0x2D00~0x2D05)"""
        for dev in self.find_all_usb_devices():
            if dev.idVendor == AOA_VID and dev.idProduct in AOA_PIDS:
                return dev
        return None

    def trigger_aoa_handshake(self, log_cb: Optional[Callable[[str, str], None]] = None) -> bool:
        """
        对已插入的 Android 设备执行 AOA 握手协商 (51/52/53 号控制指令)
        促使手机切换到 Accessory 模式并自动拉起百度 CarLife App
        """
        def _log(msg: str, color: str = "#58a6ff"):
            logger.info(msg)
            if log_cb:
                log_cb(msg, color)

        if not self.backend:
            _log("[-] 未找到可用的 libusb 驱动后端，无法操作 USB 接口", "#f85149")
            return False

        # 0. 尝试释放可能霸占 USB 端口的后台 ADB 服务
        try:
            import subprocess
            subprocess.run(["adb", "kill-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass

        # 1. 检查是否残留处于 AOA 模式 (0x2D00 / 0x2D01)
        # 核心机制：若设备直接处于 0x2D01，说明此前会话断开后手机尚未重枚举，
        # 此时手机端无活跃进程监听 /dev/usb_accessory，直接写入端点必然 10060 超时。
        # 自动触发 Windows PnP 端口复位让手机切回普通模式 (0x4EE7)，再通过 52/53 指令唤醒拉起 CarLife！
        aoa_dev = self.find_aoa_device()
        if aoa_dev:
            _log(f"[*] 检测到 Android 设备处于残留 AOA 模式 (PID: {hex(aoa_dev.idProduct)})，正在触发端口电源复位以唤醒手机...", "#d29922")
            reset_aoa_device_pnp()
            time.sleep(1.5)

        # 2. 扫描待切换的 USB 设备
        devices = self.find_all_usb_devices()
        _log(f"[*] 正在扫描 USB 总线，共检测到 {len(devices)} 个 USB 设备...")

        target_dev = None
        access_denied_count = 0
        for d in devices:
            # 过滤标准集线器与纯根端口
            if d.bDeviceClass == 9:  # HUB
                continue
            try:
                # 尝试发送 51 号指令探测是否支持 AOA
                # bmRequestType: 0xC0 (Vendor In), bRequest: 51
                proto = d.ctrl_transfer(REQ_VENDOR_IN, AOA_GET_PROTOCOL, 0, 0, 2, timeout=500)
                if len(proto) == 2:
                    ver = proto[0] | (proto[1] << 8)
                    if ver >= 1:
                        target_dev = d
                        _log(f"[+] 发现支持 AOA 协议的 Android 设备 (VID={hex(d.idVendor)} PID={hex(d.idProduct)} AOA_Version={ver})", "#3fb950")
                        break
            except Exception as e:
                err_str = str(e).lower()
                if "access denied" in err_str or "errno 13" in err_str:
                    access_denied_count += 1
                continue

        if not target_dev:
            if access_denied_count > 0:
                _log("[-] 未能通过 AOA 探测到设备：检测到 USB 端口被其他进程独占（请关闭正在运行的手机助手或 ADB 工具）", "#f85149")
            else:
                _log("[-] 未能通过 AOA 协议探测到 Android 设备，请确认手机已使用 USB 数据线直连电脑", "#f85149")
            return False

        # 3. 发送 52 号指令：写入认证参数 (匹配 accessory_filter.xml)
        _log("[*] 正在发送 52 号指令 (Accessory Identification: Baidu CarLife)...")
        try:
            for idx, text in enumerate(ACCESSORY_STRINGS):
                data = text.encode("utf-8")
                target_dev.ctrl_transfer(REQ_VENDOR_OUT, AOA_SEND_STRING, 0, idx, data, timeout=1000)
                logger.debug(f"  String[{idx}]: {text}")
        except Exception as e:
            _log(f"[-] 发送 AOA 认证字符串失败: {e}", "#f85149")
            return False

        # 4. 发送 53 号指令：请求启动 Accessory 模式
        _log("[*] 正在发送 53 号指令 (Start Accessory)，触发手机端拉起 CarLife...")
        try:
            target_dev.ctrl_transfer(REQ_VENDOR_OUT, AOA_START_ACCESSORY, 0, 0, None, timeout=1000)
        except Exception as e:
            logger.debug(f"发送 53 指令返回值 (重枚举引发总线断开属于正常现象): {e}")

        # 5. 等待设备重新枚举 (VID 变为 0x18D1)
        _log("[*] 等待 Android 手机 USB 重枚举 (最长 6 秒)...")
        start_t = time.time()
        while time.time() - start_t < 6.0:
            time.sleep(0.5)
            aoa_dev = self.find_aoa_device()
            if aoa_dev:
                _log(f"[+] 手机已成功切换至 AOA 配件模式！(VID=0x18D1 PID={hex(aoa_dev.idProduct)})", "#3fb950")
                return True

        _log("[-] 超时：未在总线上检测到重枚举后的 AOA 设备 (0x18D1)", "#f85149")
        return False

    def connect(self, channel_ids: List[int], log_cb: Optional[Callable[[str, str], None]] = None,
                on_fatal_error: Optional[Callable[[str], None]] = None) -> Optional[Dict[int, socket.socket]]:
        """执行完整 AOA 握手并连接，返回 7 个虚拟 Socket 通道映射字典"""
        def _log(msg: str, color: str = "#58a6ff"):
            logger.info(msg)
            if log_cb:
                log_cb(msg, color)

        # 1. 确保设备进入 AOA 模式
        if not self.trigger_aoa_handshake(log_cb):
            return None

        # 2. 找到处于 AOA 模式的设备并打开端点
        dev = self.find_aoa_device()
        if not dev:
            _log("[-] 无法定位已进入 AOA 模式的 USB 设备", "#f85149")
            return None

        try:
            import usb.util
            # 如果有内核驱动已占领，尝试卸载
            try:
                if dev.is_kernel_driver_active(0):
                    dev.detach_kernel_driver(0)
            except Exception:
                pass

            dev.set_configuration()
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]

            ep_in = None
            ep_out = None
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    ep_in = ep
                else:
                    ep_out = ep

            if not ep_in or not ep_out:
                _log("[-] 未能在 AOA 接口中找到成对的 Bulk IN/OUT 端点", "#f85149")
                return None

            _log(f"[+] 成功捕获 AOA 端点 (Bulk IN={hex(ep_in.bEndpointAddress)}, Bulk OUT={hex(ep_out.bEndpointAddress)})", "#3fb950")

            # 驱动就绪度检测 (Windows 下 libusb 需 WinUSB 驱动)
            try:
                usb.util.claim_interface(dev, intf.bInterfaceNumber)
            except (NotImplementedError, Exception) as claim_err:
                err_text = str(claim_err).lower()
                if "not implemented" in err_text or "not supported" in err_text or isinstance(claim_err, NotImplementedError):
                    _log("=" * 60, "#f85149")
                    _log("[-] 【Windows 驱动提示】Android Accessory 接口尚未绑定 WinUSB 驱动！", "#f85149")
                    _log("    说明：Windows 默认未给 AOA 接口分配驱动（设备管理器中显示为黄色感叹号）。", "#d29922")
                    _log("    请进行一次性驱动指定（无需下载额外软件，Windows 官方自带）：", "#d29922")
                    _log("    1. 按 Win+X 键打开【设备管理器】；", "#e6edf3")
                    _log("    2. 展开【其他设备】，找到带有黄色感叹号的【Android Accessory Interface】；", "#e6edf3")
                    _log("    3. 鼠标右键 ->【更新驱动程序】->【浏览我的电脑以查找驱动程序】；", "#e6edf3")
                    _log("    4. 点击【让我从计算机上的可用驱动程序列表中选取】；", "#e6edf3")
                    _log("    5. 类别选择【通用串行总线设备】，型号选择【WinUSB Device】安装即可！", "#e6edf3")
                    _log("=" * 60, "#f85149")
                    return None
                else:
                    _log(f"[-] 声明 AOA 接口失败: {claim_err}", "#f85149")
                    return None

            # 3. 建立传输会话与虚拟多路复用
            session = AoaTransportSession(dev, ep_in, ep_out, on_fatal_error=on_fatal_error)
            client_sockets = session.start(channel_ids)
            self.active_session = session
            return client_sockets

        except Exception as e:
            _log(f"[-] 打开 AOA 设备端点异常: {e}", "#f85149")
            logger.exception("打开 AOA 设备端点异常")
            return None

    def disconnect(self):
        """断开当前 AOA 会话"""
        if self.active_session:
            self.active_session.close()
            
            self.active_session = None
