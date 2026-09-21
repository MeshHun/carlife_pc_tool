# CarLife 电脑端车机调试工具 (Vehicle HeadUnit Simulator)

基于反编译自百度 CarLife 车机端 App (`carlife-vehicle`) 的底层通信协议构建的电脑端车机模拟工具。
用于在 PC 上**连接、调试、测试真实的手机端 CarLife App**（支持 Android 和 iOS）。

---

## 主要功能

1. **7 通道完整仿真**：
   - 依据 [`sources/d/b/a/a/p/o/e/c.java`](file:///d:/CodeWORK/Prj/carlife-vehicle/sources/d/b/a/a/p/o/e/c.java#L16)，模拟车机端在端口 `7240`、`8240`、`9240`、`9241`、`9242`、`9340`、`9440` 上建立全部 TCP 连接。
2. **自动化握手与心跳状态机**：
   - 依据 [`sources/d/b/a/a/p/m/a/c.java`](file:///d:/CodeWORK/Prj/carlife-vehicle/sources/d/b/a/a/p/m/a/c.java#L58-L133)，自动与手机端协商版本 (`98305`/`65538`)、交换设备信息 (`98307`/`65540`)、确认鉴权 (`98380`/`65611`) 与特征配置，并启动 1000ms 心跳守护 (`131074`)。
3. **低延迟 H.264 投屏渲染**：
   - 依据 [`sources/d/b/a/a/p/k/a.java`](file:///d:/CodeWORK/Prj/carlife-vehicle/sources/d/b/a/a/p/k/a.java#L47)，实时解码 Channel 2 传输的 H.264/AVC 裸流并在 PC 窗口流畅渲染。
4. **鼠标交互转触控事件**：
   - 依据 [`sources/com/baidu/carlife/sdk/receiver/view/RemoteDisplayGLView.java`](file:///d:/CodeWORK/Prj/carlife-vehicle/sources/com/baidu/carlife/sdk/receiver/view/RemoteDisplayGLView.java#L220)，在投屏窗口上点击、拖拽鼠标，实时换算为手机坐标并封装为 `CarlifeTouchAction` (`425985`) 发送给手机。
5. **车机物理按键与传感器注入**：
   - 支持 Home 键、Back 键、接听/挂断电话等车机实体按键 (`425992`)。
   - 支持滑块实时模拟车速 (`98322`)，测试手机端导航的巡航与车速自适应功能。
6. **报文监控与日志窗口**：
   - 实时彩色日志显示当前收发的协议命令、ID 与数据包详情。

---

## 启动与使用方式

### 1. 运行环境要求
- Python 3.10+
- 已安装依赖：`PyQt6`, `av (PyAV)`, `protobuf`

### 2. 快速启动
在项目根目录下或 `tools/carlife_pc_hu/` 目录下执行：
```powershell
python tools/carlife_pc_hu/main.py
```

### 3. 连接手机端 CarLife

#### 方式 A：USB 模式 (Android 推荐，最稳定)
1. 手机开启 **开发者选项** 与 **USB 调试**；
2. 用 USB 数据线将手机连接到电脑；
3. 打开手机端 **CarLife App**；
4. 在本工具界面中，模式选择 **【USB (ADB 自动端口穿透)】**；
5. 点击 **【连接车机】**，工具将自动执行 `adb forward` 并完成握手投屏。

#### 方式 B：Wi-Fi 局域网模式 (Android / iOS)
1. 确保电脑与手机连接在同一个 Wi-Fi 路由器局域网下；
2. 打开手机端 CarLife App；
3. 工具模式选择 **【Wi-Fi 局域网连接】**，在目标 IP 中输入手机在 Wi-Fi 下的 IP 地址（如 `192.168.1.105`）；
4. 点击 **【连接车机】**。

---

## 运行单元测试
```powershell
python -m unittest discover -s tools/carlife_pc_hu/tests
```
