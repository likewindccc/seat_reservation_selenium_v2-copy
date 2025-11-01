# 快速开始指南

这是一份简明的配置指南，帮助你快速上手座位预约系统。

## 1. 环境准备

### 必需软件
- ✅ Python 3.8 或更高版本
- ✅ Microsoft Edge 浏览器（最新版本）

### 检查Python版本
```bash
python --version
```

如果显示版本号，说明Python已安装。

---

## 2. 安装依赖

在项目目录下运行：

```bash
pip install -r requirements.txt
```

等待安装完成即可。

---

## 3. 配置账户信息

这是最重要的一步！

### 步骤1：打开配置文件

找到并打开文件：`src/config/settings.py`

### 步骤2：填写账户信息

找到 `ACCOUNTS` 配置部分，按以下示例填写：

```python
ACCOUNTS = [
    {
        'username': '2023XXXXXX',  # 改成你的学工号
        'password': 'yourpassword',  # 改成你的密码
        'account_name': 'Account1',  # 保持不变
        'seat_numbers': [158, 160, 162],  # 改成你想要的座位号
        'profile_dir': 'C:\\temp\\edge_profile_account1'  # 保持不变
    }
]
```

**重要提醒：**
- ⚠️ `username` 和 `password` 必须填写
- ⚠️ `seat_numbers` 是座位优先级列表，会按顺序尝试
- ⚠️ 确保座位号存在且可用

### 步骤3（可选）：配置第二个账户

如果你有第二个账户，取消注释并填写：

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
        'username': '第二个学工号',  # 取消注释并填写
        'password': '第二个密码',
        'account_name': 'Account2',
        'seat_numbers': [159, 161, 163],
        'profile_dir': 'C:\\temp\\edge_profile_account2'
    }
]
```

---

## 4. 运行程序

### 方式1：使用批处理文件（推荐）

双击运行 `run.bat` 文件即可。

### 方式2：命令行运行

```bash
python main.py
```

---

## 5. 验证运行

程序运行时会：
1. 自动打开Edge浏览器
2. 自动登录账户
3. 自动选择座位
4. 自动处理滑块验证码
5. 显示预约结果

如果出现错误：
- 检查 `logs/` 文件夹中的日志文件
- 检查 `errors/` 文件夹中的错误截图

---

## 6. 可选配置

### 微信通知（可选）

如果想要微信通知功能：

1. 在企业微信群中添加群机器人
2. 复制Webhook地址
3. 在 `settings.py` 中配置：

```python
WECHAT_WORK_ENABLED = True
WECHAT_WORK_WEBHOOK_URL = "你的Webhook地址"
```

### 修改目标房间（如需要）

在 `settings.py` 中修改：

```python
TARGET_ROOM = '研学中心学生工位'  # 改成你要预约的房间
```

---

## 常见问题

### Q: 程序报错找不到Python？
**A**: 修改 `run.bat` 文件，将 `set VENV_PYTHON=python` 改为你的Python完整路径。

### Q: Edge驱动下载失败？
**A**: 检查网络连接。首次运行时需要下载驱动，可能需要几分钟。

### Q: 滑块验证码识别失败？
**A**: 系统会自动重试10次。如果仍然失败，请检查网络连接和错误截图。

### Q: 如何知道座位号？
**A**: 需要先手动登录预约系统，查看可用的座位号。

---

## 下一步

配置完成后，建议：
1. 先测试运行一次，确保配置正确
2. 查看运行日志，了解运行情况
3. 阅读完整的 `README.md` 了解更多功能

---

## 需要帮助？

- 详细文档: 阅读 `README.md`
- 提交问题: [GitHub Issues](https://github.com/your-username/seat-reservation-system/issues)

祝你使用愉快！

