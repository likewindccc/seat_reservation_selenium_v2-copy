# 座位预约系统 Selenium V2

基于Selenium的自动化座位预约系统，支持滑块验证码自动识别。

## 项目特性

### ✨ 核心功能
- ✅ 双账户并行预约
- ✅ 自动识别滑块验证码（ddddocr，准确率95%+）
- ✅ 自动管理Edge驱动（无需手动更新驱动）
- ✅ 支持多个备选座位
- ✅ 微信通知推送（可选）
- ✅ 仅记录错误日志（减少IO开销）

### 🔧 技术亮点
- **webdriver-manager**: 自动下载并管理Edge驱动，解决驱动版本更新问题
- **ddddocr**: 滑块验证码识别，准确率高
- **模块化设计**: 代码结构清晰，易于维护和扩展
- **PEP8规范**: 严格遵守Python代码规范

---

## 快速开始

### 系统要求
- Windows 10/11
- Python 3.8+
- Microsoft Edge浏览器（最新版本）

### 安装步骤

1. **克隆或下载项目**
```bash
git clone https://github.com/your-username/seat-reservation-system.git
cd seat-reservation-system/seat_reservation_selenium_v2
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置账户信息**

编辑 `src/config/settings.py` 文件，填写你的账户信息：

```python
ACCOUNTS = [
    {
        'username': '你的学工号',  # 必填：你的学工号
        'password': '你的密码',     # 必填：你的密码
        'account_name': 'Account1',
        'seat_numbers': [158, 160, 162],  # 必填：座位号（按优先级）
        'profile_dir': 'C:\\temp\\edge_profile_account1'
    }
]
```

4. **运行程序**

**方式1：使用批处理文件（推荐）**
- 双击运行 `run.bat` 文件

**方式2：命令行运行**
```bash
python main.py
```

---

## 详细配置说明

### 必填配置项

#### 1. 账户配置

编辑 `src/config/settings.py` 中的 `ACCOUNTS` 列表：

```python
ACCOUNTS = [
    {
        'username': '',          # 必填：你的学工号
        'password': '',          # 必填：你的密码
        'account_name': 'Account1',  # 必填：账户名称（用于日志区分）
        'seat_numbers': [158, 160, 162],  # 必填：座位号列表（按优先级从高到低）
        'profile_dir': 'C:\\temp\\edge_profile_account1'  # 必填：Edge配置文件目录
    }
]
```

**配置说明：**

| 配置项 | 说明 | 示例 |
|--------|------|------|
| username | 学工号 | `2023XXXXXX` |
| password | 密码 | `yourpassword` |
| account_name | 账户名称（用于日志） | `Account1` |
| seat_numbers | 座位号列表（按优先级） | `[158, 159, 160]` |
| profile_dir | Edge配置文件目录（每个账户必须不同） | `C:\\temp\\edge_profile_account1` |

**多账户配置示例：**

如果你有多个账户，可以添加更多账户配置：

```python
ACCOUNTS = [
    {
        'username': '第一个学工号',
        'password': '第一个密码',
        'account_name': 'Account1',
        'seat_numbers': [158, 160, 162],
        'profile_dir': 'C:\\temp\\edge_profile_account1'
    },
    {
        'username': '第二个学工号',
        'password': '第二个密码',
        'account_name': 'Account2',
        'seat_numbers': [159, 161, 163],
        'profile_dir': 'C:\\temp\\edge_profile_account2'  # 注意：必须与第一个不同
    }
]
```

#### 2. 目标房间配置

在 `src/config/settings.py` 中修改目标房间名称：

```python
TARGET_ROOM = '研学中心学生工位'  # 修改为你要预约的房间名称
```

### 可选配置项

#### 3. 微信通知配置（可选）

如果需要微信通知功能，需要配置企业微信机器人：

1. **获取Webhook URL**
   - 在企业微信群中，点击群设置 → 群机器人 → 添加机器人
   - 复制Webhook地址

2. **配置到系统中**

编辑 `src/config/settings.py`：

```python
# 启用微信通知
WECHAT_WORK_ENABLED = True

# 填写你的Webhook URL
WECHAT_WORK_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key"

# 是否@所有人
WECHAT_WORK_MENTION_ALL = False

# 通知开关
NOTIFY_ON_SUCCESS = True   # 预约成功时通知
NOTIFY_ON_FAILURE = True   # 预约失败时通知
```

#### 4. 其他可选配置

```python
# 全局超时时间（秒）
GLOBAL_TIMEOUT = 300  # 5分钟

# 验证码识别最大尝试次数
MAX_CAPTCHA_ATTEMPTS = 10

# 滑块距离微调（像素）
SLIDER_DISTANCE_OFFSET = 0  # 如果滑块总是偏左，设置为正数；偏右则设置为负数
```

---

## 使用方法

### 方式1：使用批处理文件（推荐Windows用户）

1. 修改 `run.bat` 文件中的Python路径（如果需要）：
```batch
REM 默认使用系统Python
set VENV_PYTHON=python

REM 如果使用虚拟环境，请取消注释并修改路径
REM set VENV_PYTHON=D:\Python\.venv\Scripts\python.exe
```

2. 双击运行 `run.bat` 文件

### 方式2：命令行运行

```bash
# 切换到项目目录
cd seat_reservation_selenium_v2

# 运行程序
python main.py
```

---

## 项目结构

```
seat_reservation_selenium_v2/
├── src/
│   ├── config/
│   │   └── settings.py           # 配置管理（账户、URL、XPath等）
│   ├── core/
│   │   ├── browser_manager.py    # 浏览器管理（自动驱动更新）
│   │   ├── login_handler.py      # 登录流程
│   │   ├── reservation_handler.py # 预约流程编排
│   │   ├── slider_captcha.py     # 滑块验证码处理⭐核心
│   │   └── seat_query.py         # HTTP座位查询
│   └── utils/
│       ├── logger.py              # 日志工具
│       ├── element_helper.py     # 元素操作助手
│       └── date_helper.py        # 日期处理工具
├── logs/                          # 日志文件夹
├── errors/                        # 错误截图文件夹
├── main.py                        # 主入口⭐
├── requirements.txt               # 依赖清单
├── DEVELOPMENT_PLAN.md           # 开发计划
└── README.md                      # 本文件
```

---

## 运行流程

系统执行的完整流程：

1. **初始化阶段**
   - 加载配置
   - 初始化日志系统
   - 创建浏览器管理器（自动下载最新驱动）

2. **登录阶段**
   - 访问登录页面
   - 输入用户名密码
   - 点击登录按钮
   - 进入应用

3. **预约阶段**
   - 进入预约选座页面
   - 选择目标房间
   - 选择明天的日期
   - 选择座位（按优先级尝试）
   - 点击确定按钮

4. **验证码阶段**⭐核心
   - 获取滑块验证码图片
   - 使用ddddocr识别滑动距离
   - 生成模拟人工的滑动轨迹
   - 执行滑块拖动
   - 验证结果

5. **完成阶段**
   - 确认预约成功
   - 保存日志
   - 关闭浏览器

---

## 常见问题

### Q1: 如何配置账户信息？
**A**: 
1. 打开 `src/config/settings.py` 文件
2. 找到 `ACCOUNTS` 列表
3. 填写你的学工号和密码
4. 修改座位号列表 `seat_numbers`

### Q2: 如何解决Edge驱动版本不匹配？
**A**: 本系统使用 `webdriver-manager` 自动管理驱动，会自动下载匹配的驱动版本。无需手动操作！

### Q3: 滑块验证码识别失败怎么办？
**A**: 系统会自动重试最多10次。如果仍然失败：
- 检查网络连接是否正常
- 查看 `errors/` 文件夹中的错误截图
- 尝试调整 `settings.py` 中的 `SLIDER_DISTANCE_OFFSET` 参数

### Q4: 如何查看运行日志？
**A**: 
- 错误日志：`logs/error_{账户名}_{日期}.log`
- 错误截图：`errors/error_{错误类型}_{账户名}_{时间戳}.png`

### Q5: 可以同时运行多个账户吗？
**A**: 可以！在 `settings.py` 的 `ACCOUNTS` 列表中添加多个账户配置即可。每个账户会独立运行。

### Q6: 如何修改目标座位？
**A**: 编辑 `src/config/settings.py` 中的 `seat_numbers` 字段，按优先级从高到低排列。

### Q7: 为什么每个账户需要不同的profile_dir？
**A**: 每个账户使用独立的Edge配置文件，避免登录状态冲突。确保每个账户的 `profile_dir` 都不同。

### Q8: 微信通知功能是必须的吗？
**A**: 不是必须的。如果不需要，在 `settings.py` 中设置 `WECHAT_WORK_ENABLED = False` 即可。

### Q9: 如何修改目标房间？
**A**: 在 `settings.py` 中修改 `TARGET_ROOM` 变量为你要预约的房间名称。

### Q10: Python环境如何配置？
**A**: 
- **方式1（推荐新手）**: 直接使用系统Python，在 `run.bat` 中保持 `set VENV_PYTHON=python`
- **方式2（推荐进阶）**: 创建虚拟环境，在 `run.bat` 中修改为你的虚拟环境路径

---

## 技术说明

### 滑块验证码识别原理

1. **图片获取**: 通过JavaScript从页面获取背景图和滑块图
2. **距离识别**: 使用ddddocr的slide_match方法识别滑动距离
3. **轨迹生成**: 使用ease-out算法生成模拟人工的滑动轨迹
   - 前80%距离：加速阶段
   - 后20%距离：减速阶段
4. **滑块拖动**: 使用ActionChains按轨迹拖动滑块
5. **结果验证**: 检查验证码弹窗是否消失

### Edge驱动自动管理原理

使用 `webdriver-manager` 库：
```python
from webdriver_manager.microsoft import EdgeChromiumDriverManager

service = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service)
```

**特点**：
- 首次运行自动下载最新驱动
- 后续运行使用缓存驱动
- 浏览器更新时自动检测并下载新驱动
- 无需手动管理驱动文件

---

## 更新日志

### V2.0.0 (2025-10-31)
- ✅ 重构代码，采用模块化设计
- ✅ 集成滑块验证码自动识别（ddddocr）
- ✅ 使用webdriver-manager自动管理驱动
- ✅ 支持双账户并行预约
- ✅ 集成微信通知功能
- ✅ 仅记录错误日志
- ✅ 严格遵守PEP8规范

---

## 注意事项

1. **账户安全**：请妥善保管你的账户密码，不要将配置文件上传到公开仓库
2. **合理使用**：本系统仅供学习交流使用，请遵守学校相关规定
3. **网络环境**：建议在稳定的网络环境下运行
4. **浏览器版本**：建议使用最新版本的Microsoft Edge浏览器

---

## 许可证

MIT License

本项目仅供学习交流使用，请勿用于商业用途。

---

## 贡献指南

欢迎提交Issue和Pull Request！

如果你发现了bug或有功能建议：
1. 在GitHub上提交Issue
2. Fork本项目并创建新分支
3. 提交你的改动
4. 创建Pull Request

---

## 联系方式

- 提交Issue: [GitHub Issues](https://github.com/your-username/seat-reservation-system/issues)
- 项目主页: [GitHub](https://github.com/your-username/seat-reservation-system)

---

## 上传到GitHub前的准备

如果你想将此项目fork或上传到自己的GitHub仓库，**请务必先完成以下步骤**：

### 安全检查清单

1. **清空敏感配置**
   - 打开 `src/config/settings.py`
   - 确保所有 `username` 和 `password` 为空
   - 确保 `WECHAT_WORK_WEBHOOK_URL` 为空

2. **清空日志和错误文件**
   ```bash
   Remove-Item "logs/*.log" -Force
   Remove-Item "errors/*.*" -Force -Exclude .gitkeep
   ```

3. **运行安全检查脚本**
   ```bash
   python check_config.py
   ```

4. **查看完整检查清单**
   - 参考 `GITHUB_UPLOAD_CHECKLIST.md`
   - 逐项完成所有检查

**重要提醒：上传到GitHub的内容是公开的，请确保不包含任何个人隐私信息！**

---

## 致谢

感谢以下开源项目：
- [Selenium](https://www.selenium.dev/) - 浏览器自动化框架
- [ddddocr](https://github.com/sml2h3/ddddocr) - 验证码识别库
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) - 驱动管理工具

