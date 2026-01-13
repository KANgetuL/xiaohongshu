#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书登录测试脚本
用于测试cookie登录功能
"""

import os
import sys
import time
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入模块
try:
    from src.crawler.selenium_handler import SeleniumHandler
    print("✅ 成功导入 SeleniumHandler")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("尝试使用相对导入...")
    sys.path.insert(0, os.path.join(project_root, 'src'))
    try:
        from crawler.selenium_handler import SeleniumHandler
        print("✅ 成功导入 SeleniumHandler (相对路径)")
    except ImportError as e2:
        print(f"❌ 相对导入也失败: {e2}")
        print("当前sys.path:")
        for p in sys.path:
            print(f"  - {p}")
        sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_login():
    """测试登录功能"""
    print("🧪 小红书登录功能测试")
    print("=" * 60)
    
    # 检查cookie文件
    cookies_file = "xiaohongshu_cookies.json"
    if os.path.exists(cookies_file):
        print(f"📁 找到cookie文件: {cookies_file}")
        try:
            import json
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            print(f"  包含 {len(cookies)} 个cookies")
        except:
            print("  无法读取cookie文件")
    else:
        print("📁 未找到cookie文件，需要首次登录")
    
    print("\n1. 初始化浏览器...")
    handler = SeleniumHandler(browser='chrome', headless=False)
    
    if not handler.initialize():
        print("❌ 浏览器初始化失败")
        return
    
    try:
        print("\n2. 尝试登录...")
        print("   浏览器窗口将打开，请扫码登录小红书")
        print("   登录成功后，cookies将自动保存")
        print("   等待30秒...\n")
        
        if handler.login_with_cookies():
            print("✅ 登录测试成功！")
            
            # 测试搜索功能
            print("\n3. 测试搜索功能...")
            search_url = "https://www.xiaohongshu.com/search_result?keyword=外卖翻车"
            handler.get_page(search_url)
            time.sleep(5)
            
            # 检查登录状态
            if handler.is_logged_in():
                print("✅ 登录状态正常")
            else:
                print("❌ 登录状态异常")
            
            # 检查页面内容
            page_source = handler.driver.page_source
            if "立即登录" not in page_source and "登录后查看" not in page_source:
                print("✅ 搜索功能正常，已登录状态访问成功")
                
                # 提取一些图片测试
                images = handler.extract_images()
                print(f"✅ 提取到 {len(images)} 张图片")
                
                if images:
                    print(f"   第一张图片: {images[0][:80]}...")
            else:
                print("❌ 搜索功能受限，仍需要登录")
            
            # 保存截图
            screenshot_file = "test_login_success.png"
            handler.driver.save_screenshot(screenshot_file)
            print(f"📸 已保存截图: {screenshot_file}")
            
            # 保存页面源码
            with open("test_login_page.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("💾 已保存页面源码: test_login_page.html")
            
        else:
            print("❌ 登录测试失败")
            
        print("\n" + "=" * 60)
        print("📋 测试完成")
        print(f"Cookie文件: {cookies_file}")
        print("下次运行程序将自动使用保存的cookies")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        handler.close()
        print("✅ 浏览器已关闭")

def manual_login():
    """手动登录并保存cookies"""
    print("🔧 手动登录模式")
    print("=" * 60)
    
    print("1. 初始化浏览器...")
    handler = SeleniumHandler(browser='chrome', headless=False)
    
    if not handler.initialize():
        print("❌ 浏览器初始化失败")
        return
    
    try:
        print("\n2. 请手动登录小红书")
        print("   浏览器窗口已打开，请按以下步骤操作：")
        print("   a. 访问 https://www.xiaohongshu.com")
        print("   b. 扫描二维码登录")
        print("   c. 登录成功后，按回车键继续...")
        
        # 打开小红书
        handler.driver.get("https://www.xiaohongshu.com")
        
        # 等待用户手动登录
        input("\n按回车键继续（登录完成后）...")
        
        # 检查登录状态
        if handler.is_logged_in():
            print("✅ 检测到已登录状态")
            
            # 保存cookies
            if handler.save_cookies():
                print("✅ Cookies保存成功")
            else:
                print("❌ Cookies保存失败")
        else:
            print("❌ 未检测到登录状态，请重新运行")
            
    except Exception as e:
        print(f"❌ 手动登录过程中发生错误: {e}")
    finally:
        handler.close()
        print("✅ 浏览器已关闭")

if __name__ == "__main__":
    print("小红书登录测试工具")
    print("=" * 60)
    print("1. 自动登录测试")
    print("2. 手动登录并保存cookies")
    print("3. 退出")
    
    choice = input("\n请选择操作 (1-3): ").strip()
    
    if choice == "1":
        test_login()
    elif choice == "2":
        manual_login()
    else:
        print("退出程序")