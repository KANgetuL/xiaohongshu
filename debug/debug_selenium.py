#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Selenium和ChromeDriver问题
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crawler.selenium_handler import SeleniumHandler

def test_direct_chrome():
    """直接测试Chrome"""
    print("🧪 直接测试Chrome浏览器")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("1. 创建Chrome选项...")
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        print("2. 尝试初始化Chrome...")
        driver = webdriver.Chrome(options=options)
        
        print("✅ Chrome初始化成功!")
        
        print("3. 访问测试页面...")
        driver.get("https://www.baidu.com")
        
        print(f"✅ 页面标题: {driver.title}")
        print(f"✅ 当前URL: {driver.current_url}")
        
        driver.quit()
        print("✅ 浏览器已关闭")
        return True
        
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        print("\n📋 请尝试以下解决方案:")
        print("1. 检查Chrome是否已安装")
        print("2. 运行: pip install --upgrade selenium webdriver-manager")
        print("3. 手动下载ChromeDriver并添加到PATH")
        return False

def test_with_webdriver_manager():
    """测试webdriver-manager"""
    print("\n🧪 测试webdriver-manager")
    print("=" * 60)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("1. 配置环境变量...")
        import os
        os.environ['WDM_SSL_VERIFY'] = '0'
        os.environ['WDM_LOCAL'] = '1'
        
        print("2. 初始化webdriver-manager...")
        service = Service(ChromeDriverManager().install())
        
        print("3. 创建Chrome选项...")
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        print("4. 启动Chrome...")
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ webdriver-manager测试成功!")
        
        driver.get("https://www.baidu.com")
        print(f"✅ 页面标题: {driver.title}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ webdriver-manager测试失败: {e}")
        return False

def main():
    print("Selenium调试工具")
    print("=" * 60)
    
    print("1. 直接测试Chrome")
    print("2. 测试webdriver-manager")
    print("3. 测试自定义SeleniumHandler")
    print("4. 退出")
    
    choice = input("\n请选择操作 (1-4): ").strip()
    
    if choice == "1":
        test_direct_chrome()
    elif choice == "2":
        test_with_webdriver_manager()
    elif choice == "3":
        test_custom_handler()
    else:
        print("退出程序")

def test_custom_handler():
    """测试自定义的SeleniumHandler"""
    print("\n🧪 测试自定义SeleniumHandler")
    print("=" * 60)
    
    print("1. 创建SeleniumHandler实例...")
    handler = SeleniumHandler(browser='chrome', headless=False)
    
    print("2. 初始化浏览器...")
    if handler.initialize():
        print("✅ 初始化成功!")
        
        print("3. 访问测试页面...")
        handler.driver.get("https://www.baidu.com")
        print(f"✅ 页面标题: {handler.driver.title}")
        
        handler.close()
        print("✅ 浏览器已关闭")
    else:
        print("❌ 初始化失败")

if __name__ == "__main__":
    main()