# -*- coding: utf-8 -*-
"""
CarLife HUD (抬头显示/仪表盘) 导航信息测试显示器
依据协议与源码实现：
- 协议 ID: MSG_CMD_MD_NAVI_NEXT_TURN_INFO (65584 / 0x00010030)
- 数据结构: CarlifeNaviNextTurnInfo (action, nextTurn, roadName, totalDistance, remainDistance, turnIconData)
- 源码位置: sources/com/baidu/carlife/core/base/subscribe/RGEventHUDCollection.java
"""

from typing import Optional
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QPoint, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPixmap, QPainterPath, QPen, QBrush

# 转弯代码名称映射 (依据 sources/com/baidu/carlife/core/base/subscribe/RouteGuideParams.java)
TURN_NAMES = {
    1: "直行", 2: "右前方转弯", 3: "右转", 4: "右后方转弯", 5: "掉头",
    6: "左后方转弯", 7: "左转", 8: "左前方转弯", 9: "进入环岛", 10: "出环岛",
    11: "靠左行驶", 12: "靠右行驶", 13: "靠左进入主路", 14: "左分叉直行",
    15: "靠右进入主路", 16: "右分叉直行", 17: "分叉路走中间", 18: "靠左驶入辅路",
    19: "靠右驶入辅路", 20: "走左侧分叉", 21: "走右侧分叉", 22: "走中间分叉",
    23: "出发点", 24: "到达目的地", 29: "进入轮渡", 30: "离开轮渡", 31: "经过收费站"
}

ACTION_NAMES = {
    1: "开始显示",
    2: "诱导更新",
    3: "导航结束/已到达"
}

def format_distance(distance_m: int) -> str:
    """格式化距离显示 (米/公里)"""
    if distance_m <= 0:
        return "0 m"
    if distance_m < 1000:
        return f"{distance_m} m"
    km = distance_m / 1000.0
    if km >= 10:
        return f"{int(km)} km"
    return f"{km:.1f} km"


class TurnIconRenderer(QtWidgets.QWidget):
    """转向图标绘制器：优先渲染手机传来的 PNG 图标，无图标时自绘矢量箭头"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(110, 110)
        self.pixmap: Optional[QPixmap] = None
        self.turn_code: int = 1
        self.is_active: bool = False

    def set_icon_data(self, icon_bytes: bytes, turn_code: int, is_active: bool):
        self.turn_code = turn_code
        self.is_active = is_active
        self.pixmap = None
        if icon_bytes and len(icon_bytes) > 0:
            pix = QPixmap()
            if pix.loadFromData(icon_bytes):
                self.pixmap = pix
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 背景圆环/发光底框
        rect = self.rect()
        center = rect.center()

        if not self.is_active:
            # 静止/未激活状态
            painter.setPen(QPen(QColor("#30363d"), 2))
            painter.setBrush(QBrush(QColor("#161b22")))
            painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), 16, 16)
            painter.setPen(QColor("#484f58"))
            font = painter.font()
            font.setPointSize(24)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "⤹")
            return

        # 激活状态底盘
        painter.setPen(QPen(QColor("#00f0ff"), 2))
        painter.setBrush(QBrush(QColor(10, 25, 40, 220)))
        painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), 16, 16)

        # 如果有手机端原生图标，直接绘制
        if self.pixmap and not self.pixmap.isNull():
            target_rect = rect.adjusted(12, 12, -12, -12)
            scaled = self.pixmap.scaled(
                target_rect.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            dx = int((self.width() - scaled.width()) / 2)
            dy = int((self.height() - scaled.height()) / 2)
            painter.drawPixmap(dx, dy, scaled)
            return

        # 备选：根据 turn_code 绘制精美矢量发光箭头
        self._draw_vector_arrow(painter)

    def _draw_vector_arrow(self, painter: QPainter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        pen = QPen(QColor("#00f0ff"), 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        code = self.turn_code
        path = QPainterPath()

        if code == 1:  # 直行
            path.moveTo(0, 28)
            path.lineTo(0, -26)
            path.moveTo(-16, -10)
            path.lineTo(0, -26)
            path.lineTo(16, -10)
        elif code in (2, 80):  # 右前方
            path.moveTo(-18, 24)
            path.lineTo(12, -12)
            path.moveTo(-4, -18)
            path.lineTo(18, -18)
            path.lineTo(18, -4)
        elif code == 3:  # 右转
            path.moveTo(-18, 26)
            path.lineTo(-18, -4)
            path.quadTo(-18, -18, -4, -18)
            path.lineTo(24, -18)
            path.moveTo(10, -32)
            path.lineTo(24, -18)
            path.lineTo(10, -4)
        elif code == 7:  # 左转
            path.moveTo(18, 26)
            path.lineTo(18, -4)
            path.quadTo(18, -18, 4, -18)
            path.lineTo(-24, -18)
            path.moveTo(-10, -32)
            path.lineTo(-24, -18)
            path.lineTo(-10, -4)
        elif code == 5:  # 掉头
            path.moveTo(14, 26)
            path.lineTo(14, -8)
            path.arcTo(-22, -26, 36, 36, 0, 180)
            path.lineTo(-22, 26)
            path.moveTo(-34, 12)
            path.lineTo(-22, 26)
            path.lineTo(-10, 12)
        elif code == 24:  # 到达目的地
            pen.setColor(QColor("#00e676"))
            painter.setPen(pen)
            painter.drawEllipse(-18, -18, 36, 36)
            painter.drawLine(0, -18, 0, 18)
            painter.drawLine(-18, 0, 18, 0)
            painter.restore()
            return
        else:
            # 默认直行
            path.moveTo(0, 26)
            path.lineTo(0, -24)
            path.moveTo(-14, -10)
            path.lineTo(0, -24)
            path.lineTo(14, -10)

        painter.drawPath(path)
        painter.restore()


class HudDisplayWidget(QtWidgets.QFrame):
    """
    HUD 显示器主卡片控件
    具备深空黑 HUD 界面、发光文字、剩余距离、转弯名称、目标道路等
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HudCardFrame")
        self.setStyleSheet("""
            QFrame#HudCardFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #080d14, stop:1 #0f172a);
                border: 2px solid #00f0ff;
                border-radius: 12px;
            }
        """)
        self.setMinimumHeight(150)

        # 数据状态
        self.is_active = False
        self.action = 0
        self.turn_code = 1
        self.road_name = "未在导航中"
        self.remain_distance = 0
        self.total_distance = 0

        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # 顶部栏：HUD 标识与动作状态标签
        top_box = QtWidgets.QHBoxLayout()
        self.lbl_hud_title = QtWidgets.QLabel("✦ HUD 抬头显示 ✦", self)
        self.lbl_hud_title.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 13px; letter-spacing: 2px;")

        self.lbl_action_badge = QtWidgets.QLabel("状态: 待机", self)
        self.lbl_action_badge.setStyleSheet("color: #8b949e; background-color: #161b22; border-radius: 4px; padding: 2px 8px; font-size: 11px;")

        top_box.addWidget(self.lbl_hud_title)
        top_box.addStretch()
        top_box.addWidget(self.lbl_action_badge)
        layout.addLayout(top_box)

        # 中部主体：左侧图标 + 右侧距离与路名
        content_box = QtWidgets.QHBoxLayout()
        content_box.setSpacing(18)

        # 1. 转向图标
        self.icon_renderer = TurnIconRenderer(self)
        content_box.addWidget(self.icon_renderer)

        # 2. 导航核心信息
        info_box = QtWidgets.QVBoxLayout()
        info_box.setSpacing(4)
        info_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # 距离大字 (如 350 m 或 1.2 km)
        dist_box = QtWidgets.QHBoxLayout()
        self.lbl_remain_dist = QtWidgets.QLabel("-- m", self)
        self.lbl_remain_dist.setStyleSheet("color: #00f0ff; font-size: 32px; font-weight: bold; font-family: Consolas, 'Segoe UI', monospace;")

        self.lbl_turn_action = QtWidgets.QLabel("直行", self)
        self.lbl_turn_action.setStyleSheet("color: #e6edf3; font-size: 16px; font-weight: bold; padding-left: 6px;")

        dist_box.addWidget(self.lbl_remain_dist)
        dist_box.addWidget(self.lbl_turn_action)
        dist_box.addStretch()
        info_box.addLayout(dist_box)

        # 下一个目标道路名 (大字醒目显示)
        self.lbl_road_name = QtWidgets.QLabel("等待手机开启导航...", self)
        self.lbl_road_name.setStyleSheet("color: #ffffff; font-size: 17px; font-weight: bold;")
        self.lbl_road_name.setWordWrap(True)
        info_box.addWidget(self.lbl_road_name)

        # 底部细节：路段总长与 turn 代码
        self.lbl_sub_info = QtWidgets.QLabel("路段总长: 0m | Turn: 1", self)
        self.lbl_sub_info.setStyleSheet("color: #6e7681; font-size: 11px;")
        info_box.addWidget(self.lbl_sub_info)

        content_box.addLayout(info_box, stretch=1)
        layout.addLayout(content_box)

    def update_hud_info(self, hud_info):
        """接收并刷新手机端推送的 CarlifeNaviNextTurnInfo 报文"""
        self.action = getattr(hud_info, "action", 2)
        self.turn_code = getattr(hud_info, "nextTurn", 1)
        self.road_name = getattr(hud_info, "roadName", "")
        self.remain_distance = getattr(hud_info, "remainDistance", 0)
        self.total_distance = getattr(hud_info, "totalDistance", 0)
        turn_icon_data = getattr(hud_info, "turnIconData", b"")

        # 状态判定
        if self.action == 3:
            # 导航结束或已到达
            self.is_active = False
            self.lbl_action_badge.setText("状态: 导航结束/已到达")
            self.lbl_action_badge.setStyleSheet("color: #ffab00; background-color: #2e1d08; border-radius: 4px; padding: 2px 8px; font-size: 11px;")
            self.lbl_remain_dist.setText("到达")
            self.lbl_turn_action.setText(TURN_NAMES.get(self.turn_code, "目的地"))
            self.lbl_road_name.setText(self.road_name or "已到达目的地周边")
        else:
            self.is_active = True
            act_text = ACTION_NAMES.get(self.action, "诱导中")
            self.lbl_action_badge.setText(f"状态: {act_text}")
            self.lbl_action_badge.setStyleSheet("color: #00e676; background-color: #082917; border-radius: 4px; padding: 2px 8px; font-size: 11px;")

            self.lbl_remain_dist.setText(format_distance(self.remain_distance))
            turn_name = TURN_NAMES.get(self.turn_code, f"动作码 {self.turn_code}")
            self.lbl_turn_action.setText(turn_name)
            self.lbl_road_name.setText(self.road_name or "进入当前道路")

        self.lbl_sub_info.setText(f"路段总长: {format_distance(self.total_distance)} | 动作码: {self.turn_code} | 图标: {len(turn_icon_data)}B")
        self.icon_renderer.set_icon_data(turn_icon_data, self.turn_code, self.is_active)

    update_hud = update_hud_info

    def reset_display(self):
        """断开连接时重置界面"""
        self.is_active = False
        self.lbl_action_badge.setText("状态: 待机")
        self.lbl_action_badge.setStyleSheet("color: #8b949e; background-color: #161b22; border-radius: 4px; padding: 2px 8px; font-size: 11px;")
        self.lbl_remain_dist.setText("-- m")
        self.lbl_turn_action.setText("直行")
        self.lbl_road_name.setText("等待手机开启导航...")
        self.lbl_sub_info.setText("路段总长: 0m | Turn: 1")
        self.icon_renderer.set_icon_data(b"", 1, False)


class HudFloatingWindow(QtWidgets.QWidget):
    """
    独立 HUD 悬浮窗口
    可拖动到屏幕任意位置（或外接副屏/扩展屏），模拟真车前挡风玻璃透明 HUD
    """
    def __init__(self, parent=None):
        super().__init__(None) # 顶层独立窗口
        self.setWindowTitle("CarLife HUD 抬头显示仿真器")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(380, 180)

        self._drag_pos: Optional[QPoint] = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # 嵌套 HUD 显示卡片
        self.hud_card = HudDisplayWidget(self)
        layout.addWidget(self.hud_card)

        # 顶部操作工具栏浮动按钮（关闭/提示）
        btn_close = QtWidgets.QPushButton("✕", self)
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet("""
            QPushButton {
                color: #8b949e; background: rgba(30, 35, 45, 180);
                border: 1px solid #30363d; border-radius: 12px; font-weight: bold;
            }
            QPushButton:hover { color: #ffffff; background: #da3633; }
        """)
        btn_close.clicked.connect(self.hide)
        btn_close.move(348, 10)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self._drag_pos = None

    def update_hud_info(self, hud_info):
        self.hud_card.update_hud_info(hud_info)

    update_hud = update_hud_info

    def reset_display(self):
        self.hud_card.reset_display()
