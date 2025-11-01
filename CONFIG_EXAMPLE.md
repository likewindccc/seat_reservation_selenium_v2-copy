# 配置示例文档

本文档提供详细的配置示例，帮助你正确配置座位预约系统。

## 基础配置示例

### 单账户配置

```python
# src/config/settings.py

ACCOUNTS = [
    {
        'username': '2023XXXXXX',           # 你的学工号
        'password': 'mypassword123',        # 你的密码
        'account_name': 'Account1',         # 账户名称（用于日志）
        'seat_numbers': [158, 160, 162],    # 座位号（按优先级）
        'profile_dir': 'C:\\temp\\edge_profile_account1'
    }
]
```

### 双账户配置

```python
# src/config/settings.py

ACCOUNTS = [
    {
        'username': '2023XXXXXX',
        'password': 'password1',
        'account_name': 'Account1',
        'seat_numbers': [158, 160, 162],
        'profile_dir': 'C:\\temp\\edge_profile_account1'
    },
    {
        'username': '2023YYYYYY',
        'password': 'password2',
        'account_name': 'Account2',
        'seat_numbers': [159, 161, 163],
        'profile_dir': 'C:\\temp\\edge_profile_account2'  # 必须不同！
    }
]
```

---

## 目标房间配置

### 默认房间（研学中心）

```python
TARGET_ROOM = '研学中心学生工位'
```

### 其他房间示例

```python
# 根据实际情况修改
TARGET_ROOM = '图书馆阅览室'
```

---

## 座位号配置详解

### 单个座位

```python
'seat_numbers': [158]  # 只预约158号座位
```

### 多个备选座位（推荐）

```python
'seat_numbers': [158, 160, 162]  # 首选158，如果不可用则尝试160，再不可用则尝试162
```

### 大量备选座位

```python
'seat_numbers': [158, 160, 162, 164, 166, 168, 170]  # 提高预约成功率
```

---

## 微信通知配置

### 禁用微信通知（默认）

```python
WECHAT_WORK_ENABLED = False
WECHAT_WORK_WEBHOOK_URL = ""
```

### 启用微信通知

```python
WECHAT_WORK_ENABLED = True
WECHAT_WORK_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的机器人key"

# 通知选项
NOTIFY_ON_SUCCESS = True    # 成功时通知
NOTIFY_ON_FAILURE = True    # 失败时通知
WECHAT_WORK_MENTION_ALL = False  # 是否@所有人
```

---

## 高级配置

### 超时设置

```python
# 全局超时（秒）
GLOBAL_TIMEOUT = 300  # 5分钟

# 元素等待超时（秒）
ELEMENT_WAIT_TIMEOUT = 10

# 验证码识别超时（秒）
CAPTCHA_TIMEOUT = 120

# 最大验证码尝试次数
MAX_CAPTCHA_ATTEMPTS = 10
```

### 滑块验证码调优

```python
# 滑块距离微调（像素）
SLIDER_DISTANCE_OFFSET = 0  # 如果滑块总是偏左，设为正数（如+5）；偏右则设为负数（如-5）

# 滑块安全边距
SLIDER_SAFE_MARGIN = 0

# 最小有效滑动距离
SLIDER_MIN_VALID_DISTANCE = 10
```

### 浏览器窗口位置

```python
# 双账户窗口并排显示
WINDOW_POSITIONS = {
    'Account1': {'x': 0, 'y': 0, 'width': 700, 'height': 1000},      # 左侧
    'Account2': {'x': 700, 'y': 0, 'width': 700, 'height': 1000}     # 右侧
}
```

---

## 完整配置示例

### 示例1：单账户 + 无微信通知

```python
# 账户配置
ACCOUNTS = [
    {
        'username': '2023XXXXXX',
        'password': 'mypassword',
        'account_name': 'Account1',
        'seat_numbers': [158, 160, 162, 164],
        'profile_dir': 'C:\\temp\\edge_profile_account1'
    }
]

# 目标房间
TARGET_ROOM = '研学中心学生工位'

# 微信通知（禁用）
WECHAT_WORK_ENABLED = False
WECHAT_WORK_WEBHOOK_URL = ""
```

### 示例2：双账户 + 微信通知

```python
# 账户配置
ACCOUNTS = [
    {
        'username': '2023XXXXXX',
        'password': 'password1',
        'account_name': 'Account1',
        'seat_numbers': [158, 160, 162],
        'profile_dir': 'C:\\temp\\edge_profile_account1'
    },
    {
        'username': '2023YYYYYY',
        'password': 'password2',
        'account_name': 'Account2',
        'seat_numbers': [159, 161, 163],
        'profile_dir': 'C:\\temp\\edge_profile_account2'
    }
]

# 目标房间
TARGET_ROOM = '研学中心学生工位'

# 微信通知（启用）
WECHAT_WORK_ENABLED = True
WECHAT_WORK_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key"
NOTIFY_ON_SUCCESS = True
NOTIFY_ON_FAILURE = True
WECHAT_WORK_MENTION_ALL = False
```

---

## 配置文件位置

```
seat_reservation_selenium_v2/
└── src/
    └── config/
        └── settings.py  ← 在这里修改配置
```

---

## 配置检查清单

在运行程序前，请确认：

- [ ] `username` 已填写（学工号）
- [ ] `password` 已填写（密码）
- [ ] `seat_numbers` 已修改为实际座位号
- [ ] 如果使用双账户，每个 `profile_dir` 都不同
- [ ] `TARGET_ROOM` 与实际房间名称一致
- [ ] 如果启用微信通知，`WECHAT_WORK_WEBHOOK_URL` 已填写

---

## 常见配置错误

### ❌ 错误1：账户信息未填写

```python
'username': '',  # 错误：空字符串
'password': '',  # 错误：空字符串
```

**正确做法：**
```python
'username': '2023XXXXXX',  # 填写实际学工号
'password': 'mypassword',   # 填写实际密码
```

### ❌ 错误2：双账户使用相同的profile_dir

```python
ACCOUNTS = [
    {'profile_dir': 'C:\\temp\\edge_profile_account1'},
    {'profile_dir': 'C:\\temp\\edge_profile_account1'}  # 错误：重复了
]
```

**正确做法：**
```python
ACCOUNTS = [
    {'profile_dir': 'C:\\temp\\edge_profile_account1'},
    {'profile_dir': 'C:\\temp\\edge_profile_account2'}  # 正确：不同的路径
]
```

### ❌ 错误3：座位号格式错误

```python
'seat_numbers': 158  # 错误：不是列表
```

**正确做法：**
```python
'seat_numbers': [158]  # 正确：必须是列表
```

### ❌ 错误4：Webhook URL格式错误

```python
WECHAT_WORK_WEBHOOK_URL = "你的Webhook URL"  # 错误：未替换为实际URL
```

**正确做法：**
```python
WECHAT_WORK_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=实际的key"
```

---

## 需要帮助？

如果配置过程中遇到问题，请：
1. 仔细检查配置格式是否正确
2. 查看 `logs/` 文件夹中的错误日志
3. 参考 `README.md` 中的常见问题部分
4. 在GitHub上提交Issue

