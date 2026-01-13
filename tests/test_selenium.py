#!/usr/bin/env python3
"""
测试Selenium功能脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.crawler.selenium_handler import SeleniumHandler
from src.utils.logger import setup_logger


def test_selenium_basic():
    """测试Selenium基础功能"""
    print("测试Selenium基础功能...")
    
    # 初始化日志
    logger = setup_logger("test_selenium", log_level="DEBUG")
    
    # 创建Selenium处理器（显示浏览器界面，方便调试）
    handler = SeleniumHandler(headless=False)
    
    try:
        # 测试访问页面
        print("1. 测试页面访问...")
        url = "https://www.baidu.com"
        source = handler.get_page_source(url)
        
        if source:
            print(f"✓ 页面访问成功: {url}")
            print(f"  页面标题: {handler.driver.title}")
        else:
            print(f"✗ 页面访问失败: {url}")
        
        # 测试滚动
        print("\n2. 测试页面滚动...")
        handler.scroll_down(500, 1)
        print("✓ 页面滚动成功")
        
        # 测试提取图片
        print("\n3. 测试提取图片URL...")
        image_urls = handler.extract_image_urls()
        print(f"✓ 提取到 {len(image_urls)} 张图片")
        
        if image_urls:
            print(f"  示例图片URL: {image_urls[0][:50]}...")
        
        # 测试小红书搜索（简单测试）
        print("\n4. 测试小红书搜索（简单测试）...")
        try:
            # 先访问小红书主页
            handler.driver.get("https://www.xiaohongshu.com")
            print("✓ 小红书主页访问成功")
            
            # 获取页面标题
            print(f"  页面标题: {handler.driver.title}")
            
            # 保存截图
            handler.driver.save_screenshot("test_xiaohongshu.png")
            print("✓ 截图保存成功: test_xiaohongshu.png")
            
        except Exception as e:
            print(f"✗ 小红书测试失败: {str(e)}")
        
        print("\n✓ 所有测试完成!")
        
    except Exception as e:
        print(f"✗ 测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭浏览器
        input("\n按Enter键关闭浏览器...")
        handler.close()
        print("✓ 浏览器已关闭")


def main():
    """主测试函数"""
    print("小红书Selenium功能测试")
    print("=" * 50)
    
    try:
        test_selenium_basic()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试失败: {str(e)}")


if __name__ == "__main__":
    main()