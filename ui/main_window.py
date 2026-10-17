# -*- coding: utf-8 -*-
"""
CarLife PC 端车机调试控制台 UI (PyQt6)
包含：
1. 实时投屏渲染面板 (捕获鼠标交互转为 CarLife 触控事件)
2. USB / ADB 与 Wi-Fi 连接控制
3. 车机实体按键与车速模拟
4. 报文与握手状态机实时监控日志
"""

import sys
import os
import time
import html
import logging
from typing import Optional
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QImage, QPixmap, QColor, QFont, QPainter

from ..protocol import constants
from ..transport.connector import CarLifeConnector
from ..core.state_machine import CarLifeStateMachine, HandshakeState
from ..core.video_receiver import VideoReceiver
from ..core.touch_sender import TouchSender
from ..core.car_data_sender import CarDataSender
from .hud_widget import HudDisplayWidget, HudFloatingWindow

class VideoDisplayWidget(QtWidgets.QWidget):
    """视频渲染与触控映射控件 (高性能直接绘制与坐标映射)"""
    touch_event_signal = pyqtSignal(int, int, int) # action, x, y

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #0b0e14; border: 2px solid #21262d; border-radius: 8px;")
        self.setMinimumSize(640, 360)
        self.setMouseTracking(True)
        self.current_image: Optional[QImage] = None
        self.is_connected = False
        self.touch_sender: Optional[TouchSender] = None

    def set_touch_sender(self, sender: TouchSender):
        self.touch_sender = sender

    def update_frame(self, q_img: QImage):
        if q_img.isNull():
            return
        self.is_connected = True
        self.current_image = q_img
        # Qt 内部自动合并重绘请求，避免逐帧重复排队阻塞
        self.update()

    def show_disconnected(self):
        self.is_connected = False
        self.current_image = None
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#0b0e14"))

        if not self.is_connected or not self.current_image:
            # 绘制未连接提示文字
            painter.setPen(QColor("#8b949e"))
            font = painter.font()
            font.setPointSize(14)
            font.setBold(True)
            painter.setFont(font)
            text = "CarLife 车机模拟器就绪\n\n请使用 USB 数据线连接手机并打开 CarLife App\n或在上方点击【连接】"
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)
            return

        img_w = self.current_image.width()
        img_h = self.current_image.height()
        if img_w <= 0 or img_h <= 0:
            return

        # 计算在保持等比缩放时的有效渲染区域
        w_widget = self.width()
        h_widget = self.height()
        scale = min(w_widget / img_w, h_widget / img_h)
        disp_w = int(img_w * scale)
        disp_h = int(img_h * scale)
        offset_x = int((w_widget - disp_w) / 2.0)
        offset_y = int((h_widget - disp_h) / 2.0)

        target_rect = QtCore.QRect(offset_x, offset_y, disp_w, disp_h)
        # 高性能直接绘制：硬件/Qt 图形管线加速缩放，免除 CPU 逐像素重采样开销
        painter.drawImage(target_rect, self.current_image)

    def _handle_mouse(self, event: QtGui.QMouseEvent, action: int):
        if not self.is_connected or not self.touch_sender:
            return

        # 计算在保持等比缩放时的有效渲染区域
        w_widget = self.width()
        h_widget = self.height()
        target_w = self.touch_sender.target_width
        target_h = self.touch_sender.target_height

        scale = min(w_widget / target_w, h_widget / target_h)
        disp_w = target_w * scale
        disp_h = target_h * scale
        offset_x = (w_widget - disp_w) / 2.0
        offset_y = (h_widget - disp_h) / 2.0

        pos = event.position()
        rel_x = pos.x() - offset_x
        rel_y = pos.y() - offset_y

        if 0 <= rel_x <= disp_w and 0 <= rel_y <= disp_h:
            car_x = int((rel_x / disp_w) * target_w)
            car_y = int((rel_y / disp_h) * target_h)
            self.touch_sender.send_touch(action, car_x, car_y)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_mouse(event, constants.ACTION_DOWN)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._handle_mouse(event, constants.ACTION_MOVE)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_mouse(event, constants.ACTION_UP)


class MainWindow(QtWidgets.QMainWindow):
    sig_log = pyqtSignal(str, str)             # text, color
    sig_state = pyqtSignal(str)
    sig_render_trigger = pyqtSignal()          # 轻量无参渲染触发信号 (避免跨线程队列大对象积压)
    sig_video_ready = pyqtSignal(int, int, int)
    sig_hud_info = pyqtSignal(object)          # HUD 导航转向指引数据 (CarlifeNaviNextTurnInfo)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CarLife 车机模拟调试器 (HeadUnit Simulator for Mobile Debug)")
        self.resize(1200, 780)
        self._setup_theme()

        self.connector = CarLifeConnector(on_disconnect=self._on_fatal_disconnect)
        self.state_machine: Optional[CarLifeStateMachine] = None
        self.video_receiver: Optional[VideoReceiver] = None
        self.touch_sender: Optional[TouchSender] = None
        self.car_data_sender: Optional[CarDataSender] = None
        self.floating_hud = HudFloatingWindow(self)
        self.is_connected = False

        # 核心防卡顿机制：单缓冲覆写式渲染 (Latest Frame Only)
        import threading
        self._frame_lock = threading.Lock()
        self._latest_frame: Optional[QImage] = None
        self._frame_pending = False

        self._init_ui()
        self._connect_signals()

    def _setup_theme(self):
        # 现代暗色高级车控主题
        self.setStyleSheet("""
            QMainWindow { background-color: #0d1117; }
            QWidget { color: #c9d1d9; font-family: "Segoe UI", "Microsoft YaHei", sans-serif; font-size: 13px; }
            QGroupBox { border: 1px solid #30363d; border-radius: 6px; margin-top: 10px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #58a6ff; }
            QPushButton {
                background-color: #21262d; border: 1px solid #363b42; border-radius: 6px;
                padding: 6px 14px; font-weight: bold; min-height: 20px;
            }
            QPushButton:hover { background-color: #30363d; border-color: #8b949e; }
            QPushButton:pressed { background-color: #161b22; }
            QPushButton#btn_connect { background-color: #238636; color: #ffffff; border: none; }
            QPushButton#btn_connect:hover { background-color: #2ea043; }
            QPushButton#btn_disconnect { background-color: #da3633; color: #ffffff; border: none; }
            QPushButton#btn_disconnect:hover { background-color: #f85149; }
            QLineEdit, QComboBox {
                background-color: #161b22; border: 1px solid #30363d; border-radius: 6px;
                padding: 5px; color: #c9d1d9;
            }
            QTextEdit {
                background-color: #0d1117; border: 1px solid #30363d; border-radius: 6px;
                font-family: "Consolas", "Courier New", monospace; font-size: 12px;
            }
            QSlider::groove:horizontal { height: 6px; background: #21262d; border-radius: 3px; }
            QSlider::sub-page:horizontal { background: #58a6ff; border-radius: 3px; }
            QSlider::handle:horizontal { background: #ffffff; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
        """)

    def _init_ui(self):
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ========== 左侧：投屏显示与车机中控交互 ==========
        left_box = QtWidgets.QVBoxLayout()

        # 1. 顶部连接设置栏
        conn_group = QtWidgets.QGroupBox("连接与传输设置", self)
        conn_layout = QtWidgets.QHBoxLayout(conn_group)

        self.combo_mode = QtWidgets.QComboBox(self)
        self.combo_mode.addItems([
            "USB AOA 模式 (标准有线互联)",
            "局域网监听模式 (自动发现手机接入)",
            "局域网指定 IP 直连 (备用)"
        ])
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)

        self.edit_ip = QtWidgets.QLineEdit("USB AOA 即插即用", self)
        self.edit_ip.setPlaceholderText("无需 IP (USB 原生传输)")
        self.edit_ip.setEnabled(False)

        self.btn_connect = QtWidgets.QPushButton("连接车机", self)
        self.btn_connect.setObjectName("btn_connect")
        self.btn_connect.clicked.connect(self.start_connection)

        self.btn_disconnect = QtWidgets.QPushButton("断开", self)
        self.btn_disconnect.setObjectName("btn_disconnect")
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.clicked.connect(self.stop_connection)

        self.lbl_status_badge = QtWidgets.QLabel("状态: 未连接", self)
        self.lbl_status_badge.setStyleSheet("color: #8b949e; font-weight: bold;")

        conn_layout.addWidget(QtWidgets.QLabel("模式:"))
        conn_layout.addWidget(self.combo_mode)
        conn_layout.addWidget(QtWidgets.QLabel("手机 IP:"))
        conn_layout.addWidget(self.edit_ip)
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addWidget(self.btn_disconnect)
        conn_layout.addStretch()
        conn_layout.addWidget(self.lbl_status_badge)

        left_box.addWidget(conn_group)

        # 2. 视频投屏与鼠标触控区
        self.video_widget = VideoDisplayWidget(self)
        self.video_widget.show_disconnected()
        left_box.addWidget(self.video_widget, stretch=1)

        # 3. 车机实体控制按键面板
        ctrl_group = QtWidgets.QGroupBox("车机控制台与实体按键模拟", self)
        ctrl_layout = QtWidgets.QHBoxLayout(ctrl_group)

        btn_home = QtWidgets.QPushButton("⌂ 主页 (HOME)", self)
        btn_home.clicked.connect(lambda: self._send_key(constants.KEYCODE_HOME))

        btn_back = QtWidgets.QPushButton("↩ 返回 (BACK)", self)
        btn_back.clicked.connect(lambda: self._send_key(constants.KEYCODE_BACK))

        btn_call = QtWidgets.QPushButton("✆ 接听 (CALL)", self)
        btn_call.clicked.connect(lambda: self._send_key(constants.KEYCODE_PHONE_CALL))

        btn_hangup = QtWidgets.QPushButton("✕ 挂断 (END)", self)
        btn_hangup.clicked.connect(lambda: self._send_key(constants.KEYCODE_PHONE_END))

        btn_media = QtWidgets.QPushButton("▶ 媒体 (MEDIA)", self)
        btn_media.clicked.connect(lambda: self._send_key(constants.KEYCODE_MEDIA))

        ctrl_layout.addWidget(btn_home)
        ctrl_layout.addWidget(btn_back)
        ctrl_layout.addWidget(btn_call)
        ctrl_layout.addWidget(btn_hangup)
        ctrl_layout.addWidget(btn_media)
        ctrl_layout.addStretch()

        left_box.addWidget(ctrl_group)
        main_layout.addLayout(left_box, stretch=3)

        # ========== 右侧：车况注入与报文监视面板 ==========
        right_box = QtWidgets.QVBoxLayout()

        # 4. 车况传感器数据注入
        car_group = QtWidgets.QGroupBox("车况与传感器数据注入 (Channel 7)", self)
        car_layout = QtWidgets.QVBoxLayout(car_group)

        speed_box = QtWidgets.QHBoxLayout()
        self.lbl_speed = QtWidgets.QLabel("车速: 0 km/h", self)
        self.slider_speed = QtWidgets.QSlider(Qt.Orientation.Horizontal, self)
        self.slider_speed.setRange(0, 180)
        self.slider_speed.setValue(0)
        self.slider_speed.valueChanged.connect(self._on_speed_changed)
        speed_box.addWidget(self.lbl_speed)
        speed_box.addWidget(self.slider_speed)
        car_layout.addLayout(speed_box)

        right_box.addWidget(car_group)

        # 5. HUD 导航指引测试监视器 (Channel 1 - 0x00010030)
        hud_group = QtWidgets.QGroupBox("HUD 导航指引监视器 (Channel 1 - 0x00010030)", self)
        hud_layout = QtWidgets.QVBoxLayout(hud_group)

        self.hud_widget = HudDisplayWidget(self)
        hud_layout.addWidget(self.hud_widget)

        hud_btn_box = QtWidgets.QHBoxLayout()
        self.btn_float_hud = QtWidgets.QPushButton("⧉ 弹出独立 HUD 浮窗", self)
        self.btn_float_hud.clicked.connect(self._toggle_floating_hud)

        self.btn_test_hud = QtWidgets.QPushButton("⚡ 模拟测试数据", self)
        self.btn_test_hud.clicked.connect(self._simulate_test_hud)

        hud_btn_box.addWidget(self.btn_float_hud)
        hud_btn_box.addWidget(self.btn_test_hud)
        hud_layout.addLayout(hud_btn_box)

        right_box.addWidget(hud_group)

        # 6. 协议实时日志监控
        log_group = QtWidgets.QGroupBox("协议通信与报文监视器", self)
        log_layout = QtWidgets.QVBoxLayout(log_group)

        self.text_log = QtWidgets.QTextEdit(self)
        self.text_log.setReadOnly(True)

        log_ctrl_box = QtWidgets.QHBoxLayout()
        self.chk_filter_frequent = QtWidgets.QCheckBox("过滤高频消息 (心跳/进度条)", self)
        self.chk_filter_frequent.setChecked(True)
        btn_clear_log = QtWidgets.QPushButton("清空日志", self)
        btn_clear_log.clicked.connect(self.text_log.clear)

        log_ctrl_box.addWidget(self.chk_filter_frequent)
        log_ctrl_box.addStretch()
        log_ctrl_box.addWidget(btn_clear_log)

        log_layout.addWidget(self.text_log)
        log_layout.addLayout(log_ctrl_box)

        right_box.addWidget(log_group, stretch=1)
        main_layout.addLayout(right_box, stretch=2)

    def _connect_signals(self):
        self.sig_log.connect(self._append_log)
        self.sig_state.connect(self._update_state)
        self.sig_render_trigger.connect(self._on_render_trigger)
        self.sig_video_ready.connect(self._on_video_ready)
        self.sig_hud_info.connect(self._on_hud_info_received)

    def _on_render_trigger(self):
        """主线程槽函数：仅消费最新一帧图像，彻底消除帧排队堆积与卡顿"""
        with self._frame_lock:
            qimg = self._latest_frame
            self._frame_pending = False

        # 核心防残留守卫：若当前车机未处于已连接状态，坚决丢弃帧并跳过绘制
        if not self.is_connected:
            return

        if qimg and not self.isMinimized():
            self.video_widget.update_frame(qimg)

    def changeEvent(self, event):
        """窗口状态变化处理：从后台/最小化还原时，立刻渲染最新画面"""
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            if not self.isMinimized() and self.is_connected:
                with self._frame_lock:
                    qimg = self._latest_frame
                if qimg:
                    self.video_widget.update_frame(qimg)
        super().changeEvent(event)

    def _on_mode_changed(self, index: int):
        if index == 0:  # USB AOA 模式
            self.edit_ip.setText("USB AOA 即插即用")
            self.edit_ip.setPlaceholderText("无需 IP (USB 原生传输)")
            self.edit_ip.setEnabled(False)
        elif index == 1:  # 局域网监听模式 (车机原生行为)
            self.edit_ip.clear()
            self.edit_ip.setPlaceholderText("等待手机端 UDP 7999 广播自动捕获...")
            self.edit_ip.setEnabled(False)
        else:  # 局域网指定 IP 直连 (备用)
            self.edit_ip.setText("192.168.")
            self.edit_ip.setPlaceholderText("手动输入手机 IP 地址")
            self.edit_ip.setEnabled(True)
 
    def _append_log(self, text: str, color: str):
        # 过滤高频日志：仅过滤视频心跳保活与媒体进度条高频推送
        if hasattr(self, 'chk_filter_frequent') and self.chk_filter_frequent.isChecked():
            frequent_keywords = [
                "VIDEO_HEARTBEAT",             # ID: 131074 车端/通道2心跳
                "131074",
                "MEDIA_PROGRESS_BAR",          # ID: 65590 音乐播放进度条高频推送
                "65590",
            ]
            if any(kw in text for kw in frequent_keywords):
                return

        timestamp = time.strftime("%H:%M:%S")
        escaped_text = html.escape(text)
        html_str = f"<div style='color: {color};'>[{timestamp}] {escaped_text}</div>"
        self.text_log.append(html_str)

    def _on_fatal_disconnect(self, reason: str):
        self.sig_log.emit(f"[-] 底层传输链路中断 ({reason})，已彻底释放所有通道并重置连接", "#f85149")
        self.sig_state.emit(HandshakeState.DISCONNECTED)

    def _update_state(self, state_str: str):
        self.lbl_status_badge.setText(f"状态: {state_str}")
        if state_str == HandshakeState.CONNECTED:
            self.is_connected = True
            self.lbl_status_badge.setStyleSheet("color: #3fb950; font-weight: bold;")
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
        elif state_str == HandshakeState.DISCONNECTED:
            self.is_connected = False
            self.lbl_status_badge.setStyleSheet("color: #f85149; font-weight: bold;")
            self.btn_connect.setEnabled(True)
            self.btn_disconnect.setEnabled(False)

            if self.video_receiver:
                try:
                    self.video_receiver.stop()
                except Exception:
                    pass
                self.video_receiver = None

            if self.state_machine:
                try:
                    self.state_machine.stop()
                except Exception:
                    pass
                self.state_machine = None

            try:
                self.connector.disconnect_all()
            except Exception:
                pass

            # 无论主动还是被动断开，彻底清空缓存与画布残留
            with self._frame_lock:
                self._latest_frame = None
                self._frame_pending = False
            self.video_widget.show_disconnected()
            self.hud_widget.reset_display()
            self.floating_hud.reset_display()
        else:
            self.lbl_status_badge.setStyleSheet("color: #d29922; font-weight: bold;")

    def _send_key(self, keycode: int):
        if self.touch_sender:
            self.touch_sender.send_hardkey(keycode)

    def _on_speed_changed(self, val: int):
        self.lbl_speed.setText(f"车速: {val} km/h")
        if self.car_data_sender:
            self.car_data_sender.send_speed(val)

    def start_connection(self):
        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)

        mode = self.combo_mode.currentIndex()

        def _setup_session():
            """通道就绪后，启动触控发送、车况注入及握手协议状态机"""
            self.sig_log.emit("[+] 通道已就绪，启动协议握手状态机...", "#3fb950")

            # 1. 初始化触控与车况发送器
            cmd_sock = self.connector.get_socket(constants.CHANNEL_CMD)
            touch_sock = self.connector.get_socket(constants.CHANNEL_TOUCH)
            data_sock = self.connector.get_socket(constants.CHANNEL_DATA)

            if touch_sock:
                self.touch_sender = TouchSender(touch_sock)
                self.video_widget.set_touch_sender(self.touch_sender)

            if data_sock:
                self.car_data_sender = CarDataSender(data_sock)

            # 2. 启动状态机
            def _format_ui_log(txt: str, sid: int):
                if "[模块状态]" in txt or "[巡航电子狗" in txt:
                    color = "#7ee787"  # 醒目亮绿高亮业务状态
                elif "->" in txt:
                    color = "#58a6ff"  # 车端发出
                else:
                    color = "#79c0ff"  # 手机端收到
                self.sig_log.emit(f"{txt} (ID: {sid})", color)

            self.state_machine = CarLifeStateMachine(
                cmd_socket=cmd_sock,
                on_state_change=lambda st: self.sig_state.emit(st),
                on_log=lambda txt, sid, pld: _format_ui_log(txt, sid),
                on_video_ready=lambda w, h, fps: self.sig_video_ready.emit(w, h, fps),
                on_navi_hud_info=lambda hud: self.sig_hud_info.emit(hud)
            )
            self.state_machine.start()

        def _connect_task():
            import threading
            if mode == 0:  # USB AOA 模式 (标准有线互联)
                self.sig_log.emit("[*] 正在启动 USB AOA 模式，正在与 Android 设备协商握手...", "#58a6ff")
                self.sig_state.emit("AOA 协商中...")

                def _aoa_log_bridge(txt: str, clr: str):
                    self.sig_log.emit(txt, clr)

                if not self.connector.connect_aoa(log_callback=_aoa_log_bridge):
                    self.sig_log.emit("[-] USB AOA 连接建立失败，请确认数据线连接正常且驱动已安装", "#f85149")
                    self.sig_state.emit(HandshakeState.DISCONNECTED)
                    return

                _setup_session()

            elif mode == 1:  # 局域网监听模式 (依据 sources/d/b/a/a/p/o/e/d.java:146)
                self.sig_log.emit("[*] 局域网监听模式：正在后台监听 UDP 7999 端口，请在手机上打开 CarLife App...", "#58a6ff")
                self.sig_state.emit("监听局域网广播...")

                def _on_ip_found(phone_ip: str):
                    self.sig_log.emit(f"[+] 捕获到手机广播！手机 IP: {phone_ip}", "#3fb950")
                    self.sig_state.emit(f"发现手机 {phone_ip}")
                    # 使用 QTimer.singleShot 保证在主线程更新 UI 文本
                    QtCore.QTimer.singleShot(0, lambda: self.edit_ip.setText(phone_ip))

                    self.sig_log.emit(f"[*] 正在向手机 {phone_ip} 建立 7 个 TCP 通道...", "#58a6ff")
                    if not self.connector.connect_all_channels(phone_ip):
                        self.sig_log.emit("[-] 无法连接手机端 CarLife，请确认手机端已启动 CarLife App", "#f85149")
                        self.sig_state.emit(HandshakeState.DISCONNECTED)
                        return
                    _setup_session()

                self.connector.start_lan_discovery(_on_ip_found)

            else:  # 局域网指定 IP 直连 (备用)
                target_ip = self.edit_ip.text().strip()
                if not target_ip or target_ip == "192.168.":
                    self.sig_log.emit("[-] 请输入有效的手机 IP 地址", "#f85149")
                    self.sig_state.emit(HandshakeState.DISCONNECTED)
                    return
                self.sig_log.emit(f"[*] 正在向手机 {target_ip} 建立 7 个 TCP 通道...", "#58a6ff")
                if not self.connector.connect_all_channels(target_ip):
                    self.sig_log.emit("[-] 无法连接手机端 CarLife，请确认手机端已启动 CarLife App", "#f85149")
                    self.sig_state.emit(HandshakeState.DISCONNECTED)
                    return
                _setup_session()

        import threading
        threading.Thread(target=_connect_task, daemon=True, name="CarLife_Connect_Task").start()

    def _on_video_ready(self, width: int, height: int, fps: int):
        self.sig_log.emit(f"[+] 启动视频解码接收 (分辨率: {width}x{height} @ {fps}fps)", "#3fb950")
        if self.touch_sender:
            self.touch_sender.set_target_resolution(width, height)

        if self.video_receiver and self.video_receiver.is_running:
            return  # 避免同一连接中因信令触发多次而重复创建接收器

        video_sock = self.connector.get_socket(constants.CHANNEL_VIDEO)
        if video_sock:
            def _frame_callback(qimg: QImage):
                try:
                    # 1. 窗口断开、最小化/后台或图像无效时，跳过渲染，降低 CPU 负载
                    if not self.is_connected or self.isMinimized() or qimg.isNull():
                        return

                    # 2. 单缓冲覆写式通知：若上一帧尚在渲染中，仅更新最新帧，绝不在 Qt 队列中堆积事件
                    with self._frame_lock:
                        if not self.is_connected:
                            return
                        self._latest_frame = qimg
                        if not self._frame_pending:
                            self._frame_pending = True
                            self.sig_render_trigger.emit()
                except Exception as e:
                    logging.getLogger("CarLife_MainWindow").error(f"处理视频帧异常: {e}")

            self.video_receiver = VideoReceiver(video_sock, on_frame=_frame_callback)
            self.video_receiver.start()

    def _on_hud_info_received(self, hud_info):
        """处理来自手机端的 HUD 导航转向指引数据 (CarlifeNaviNextTurnInfo)"""
        try:
            self.hud_widget.update_hud(hud_info)
            if self.floating_hud.isVisible():
                self.floating_hud.update_hud(hud_info)

            turn_code = getattr(hud_info, "nextTurn", 1)
            turn_desc = constants.HUD_TURN_ACTIONS.get(turn_code, f"动作({turn_code})")
            road = getattr(hud_info, "roadName", "") or "前方道路"
            dist = getattr(hud_info, "remainDistance", 0)
            total = getattr(hud_info, "totalDistance", 0)
            self.sig_log.emit(
                f"[HUD 导航转向] {dist}m 后 {turn_desc} ➔ {road} (总长: {total}m)",
                "#00ffff"
            )
        except Exception as e:
            logging.getLogger("CarLife_MainWindow").error(f"处理 HUD 指引异常: {e}")

    def _toggle_floating_hud(self):
        """显隐独立半透明无边框 HUD 浮窗 (可自由拖拽到副屏模拟前挡风玻璃 HUD 投影)"""
        if self.floating_hud.isVisible():
            self.floating_hud.hide()
            self.btn_float_hud.setText("⧉ 弹出独立 HUD 浮窗")
        else:
            geo = self.geometry()
            self.floating_hud.move(geo.x() + geo.width() - 430, geo.y() + 60)
            self.floating_hud.show()
            self.floating_hud.raise_()
            self.btn_float_hud.setText("✕ 关闭独立 HUD 浮窗")

    def _simulate_test_hud(self):
        """离线轮播测试数据，验证 HUD 仪表盘与转向图标渲染效果"""
        if not hasattr(self, '_test_hud_idx'):
            self._test_hud_idx = 0

        test_cases = [
            {"action": 1, "nextTurn": 1, "remainDistance": 850, "totalDistance": 12500, "roadName": "京港澳高速"},
            {"action": 2, "nextTurn": 3, "remainDistance": 300, "totalDistance": 11650, "roadName": "深南大道 (辅道)"},
            {"action": 2, "nextTurn": 2, "remainDistance": 150, "totalDistance": 11350, "roadName": "科技南一路"},
            {"action": 2, "nextTurn": 16, "remainDistance": 50, "totalDistance": 11200, "roadName": "掉头进入小米园区"},
            {"action": 3, "nextTurn": 10, "remainDistance": 0, "totalDistance": 11150, "roadName": "小米科技园 - 目的地到达"},
        ]
        sample = test_cases[self._test_hud_idx % len(test_cases)]
        self._test_hud_idx += 1

        from ..protocol.proto_codec import CarlifeNaviNextTurnInfo
        dummy = CarlifeNaviNextTurnInfo()
        dummy.action = sample["action"]
        dummy.nextTurn = sample["nextTurn"]
        dummy.remainDistance = sample["remainDistance"]
        dummy.totalDistance = sample["totalDistance"]
        dummy.roadName = sample["roadName"]
        self.sig_hud_info.emit(dummy)

    def stop_connection(self):
        self.is_connected = False
        self.connector.stop_lan_discovery()
        if self.video_receiver:
            self.video_receiver.stop()
            self.video_receiver = None
        if self.state_machine:
            try:
                # 依据协议暂停手机端视频录制推流 (98314) 并通知返回桌面 (65569)
                self.state_machine.send_cmd(constants.MSG_CMD_VIDEO_ENCODER_PAUSE)
                self.state_machine.send_cmd(constants.MSG_CMD_GO_TO_DESKTOP)
            except Exception:
                pass
            self.state_machine.stop()
            self.state_machine = None
        self.connector.disconnect_all()

        # 锁内清空最后一帧缓存，彻底消除残留
        with self._frame_lock:
            self._latest_frame = None
            self._frame_pending = False

        self.video_widget.show_disconnected()
        self.hud_widget.reset_display()
        self.floating_hud.reset_display()
        self.sig_state.emit(HandshakeState.DISCONNECTED)
        self.sig_log.emit("[*] 已断开所有通道连接并清空画布", "#8b949e")

    def closeEvent(self, event):
        self.floating_hud.close()
        self.stop_connection()
        event.accept()
