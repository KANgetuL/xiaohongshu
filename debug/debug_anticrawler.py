# 创建测试脚本 test_anti_crawler.py
from src.crawler.selenium_handler import SeleniumHandler

def test_anti_crawler():
    handler = SeleniumHandler(headless=False)
    
    if handler.initialize():
        print("1. 访问小红书首页...")
        handler.get_page("https://www.xiaohongshu.com")
        
        print("2. 测试登录...")
        handler.login_with_cookies()
        
        print("3. 测试搜索...")
        handler.get_page("https://www.xiaohongshu.com/search_result?keyword=外卖翻车", 
                        wait_selector=".feeds-container", max_retries=3)
        
        print("4. 检查页面状态...")
        if handler.check_page_redirected():
            print("页面被重定向，尝试恢复...")
            handler.handle_page_redirect("https://www.xiaohongshu.com/search_result?keyword=外卖翻车")
        
        handler.close()

if __name__ == "__main__":
    test_anti_crawler()