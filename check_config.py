"""
配置检查脚本

在运行主程序前，使用此脚本检查配置是否正确
"""

import sys
import os
import io

# 设置标准输出为UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import settings


def check_accounts():
    """检查账户配置"""
    print("=" * 60)
    print("1. 检查账户配置")
    print("=" * 60)
    
    if not settings.ACCOUNTS:
        print("❌ 错误：ACCOUNTS列表为空")
        print("   请在 src/config/settings.py 中配置至少一个账户")
        return False
    
    print(f"✅ 发现 {len(settings.ACCOUNTS)} 个账户配置")
    
    for i, account in enumerate(settings.ACCOUNTS, 1):
        print(f"\n账户 {i}: {account.get('account_name', 'Unknown')}")
        
        # 检查必填字段
        required_fields = ['username', 'password', 'account_name', 
                          'seat_numbers', 'profile_dir']
        all_ok = True
        
        for field in required_fields:
            if field not in account:
                print(f"  ❌ 缺少字段: {field}")
                all_ok = False
                continue
            
            value = account[field]
            
            # 检查是否为空
            if not value:
                print(f"  ❌ {field} 未填写")
                all_ok = False
            elif field == 'username' and not str(value).strip():
                print(f"  ❌ {field} 为空字符串")
                all_ok = False
            elif field == 'password' and not str(value).strip():
                print(f"  ❌ {field} 为空字符串")
                all_ok = False
            elif field == 'seat_numbers' and not isinstance(value, list):
                print(f"  ❌ {field} 必须是列表")
                all_ok = False
            elif field == 'seat_numbers' and len(value) == 0:
                print(f"  ❌ {field} 列表为空")
                all_ok = False
            else:
                # 显示配置信息（密码隐藏）
                if field == 'password':
                    display_value = '*' * len(str(value))
                elif field == 'seat_numbers':
                    display_value = f"{value} (共{len(value)}个座位)"
                else:
                    display_value = value
                print(f"  ✅ {field}: {display_value}")
        
        if not all_ok:
            return False
    
    # 检查profile_dir是否重复
    profile_dirs = [acc['profile_dir'] for acc in settings.ACCOUNTS 
                   if 'profile_dir' in acc]
    if len(profile_dirs) != len(set(profile_dirs)):
        print("\n❌ 错误：多个账户使用了相同的profile_dir")
        print("   每个账户必须使用不同的profile_dir")
        return False
    
    print("\n✅ 账户配置检查通过")
    return True


def check_target_room():
    """检查目标房间配置"""
    print("\n" + "=" * 60)
    print("2. 检查目标房间配置")
    print("=" * 60)
    
    if not settings.TARGET_ROOM:
        print("❌ 错误：TARGET_ROOM 未配置")
        return False
    
    print(f"✅ 目标房间: {settings.TARGET_ROOM}")
    return True


def check_wechat_config():
    """检查微信通知配置"""
    print("\n" + "=" * 60)
    print("3. 检查微信通知配置")
    print("=" * 60)
    
    if not settings.WECHAT_WORK_ENABLED:
        print("ℹ️  微信通知未启用")
        return True
    
    print("✅ 微信通知已启用")
    
    if not settings.WECHAT_WORK_WEBHOOK_URL:
        print("❌ 错误：WECHAT_WORK_WEBHOOK_URL 未配置")
        print("   请填写企业微信机器人的Webhook URL")
        return False
    
    if not settings.WECHAT_WORK_WEBHOOK_URL.startswith('https://'):
        print("❌ 错误：WECHAT_WORK_WEBHOOK_URL 格式不正确")
        print("   应该以 https:// 开头")
        return False
    
    print(f"✅ Webhook URL: {settings.WECHAT_WORK_WEBHOOK_URL[:50]}...")
    print(f"✅ @所有人: {settings.WECHAT_WORK_MENTION_ALL}")
    print(f"✅ 成功通知: {settings.NOTIFY_ON_SUCCESS}")
    print(f"✅ 失败通知: {settings.NOTIFY_ON_FAILURE}")
    
    return True


def check_directories():
    """检查必要的目录是否存在"""
    print("\n" + "=" * 60)
    print("4. 检查目录结构")
    print("=" * 60)
    
    dirs = [
        ('logs', settings.LOG_DIR),
        ('errors', settings.ERROR_DIR),
    ]
    
    all_ok = True
    for name, path in dirs:
        if os.path.exists(path):
            print(f"✅ {name} 目录存在: {path}")
        else:
            print(f"⚠️  {name} 目录不存在，将自动创建: {path}")
            try:
                os.makedirs(path, exist_ok=True)
                print(f"   ✅ 已创建目录")
            except Exception as e:
                print(f"   ❌ 创建失败: {e}")
                all_ok = False
    
    return all_ok


def check_python_version():
    """检查Python版本"""
    print("\n" + "=" * 60)
    print("5. 检查Python版本")
    print("=" * 60)
    
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要3.8或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True


def check_dependencies():
    """检查依赖包"""
    print("\n" + "=" * 60)
    print("6. 检查依赖包")
    print("=" * 60)
    
    required_packages = [
        'selenium',
        'webdriver_manager',
        'ddddocr',
        'aiohttp',
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            all_ok = False
    
    if not all_ok:
        print("\n💡 请运行以下命令安装依赖:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def main():
    """主函数"""
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "配置检查工具" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("账户配置", check_accounts),
        ("目标房间", check_target_room),
        ("微信通知", check_wechat_config),
        ("目录结构", check_directories),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 检查 {name} 时出错: {e}")
            results.append((name, False))
    
    # 显示总结
    print("\n" + "=" * 60)
    print("检查结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s} {status}")
    
    print("\n" + "=" * 60)
    
    if passed == total:
        print("🎉 所有检查通过！可以运行程序了")
        print("\n运行方式:")
        print("  1. 双击运行 run.bat")
        print("  2. 或在命令行运行: python main.py")
        return 0
    else:
        print(f"⚠️  {total - passed}/{total} 项检查失败，请修复后再运行")
        print("\n💡 查看详细配置说明:")
        print("  - QUICKSTART.md (快速开始)")
        print("  - CONFIG_EXAMPLE.md (配置示例)")
        print("  - README.md (完整文档)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

