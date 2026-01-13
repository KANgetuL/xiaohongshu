import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logger = logging.getLogger(__name__)

class SeleniumHandler:
    def __init__(self, browser='chrome', headless=False, user_data_dir=None):
        self.browser = browser
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.driver = None
        self.wait = None
        self.cookies_file = "xiaohongshu_cookies.json"  # cookie文件路径
    
    def initialize(self):
        """初始化浏览器"""
        try:
            if self.browser.lower() == 'chrome':
                # 配置webdriver-manager使用国内镜像
                import os
                os.environ['WDM_SSL_VERIFY'] = '0'  # 跳过SSL验证
                os.environ['WDM_LOCAL'] = '1'  # 优先使用本地缓存
                
                # 设置国内镜像源
                # os.environ['WDM_CDNURL'] = 'https://npmmirror.com/mirrors/chromedriver/'
                
                options = webdriver.ChromeOptions()
                
                # 如果指定了用户数据目录，则使用
                if self.user_data_dir:
                    options.add_argument(f"user-data-dir={self.user_data_dir}")
                
                # 无头模式
                if self.headless:
                    options.add_argument('--headless')
                
                # 其他选项
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # 添加更多选项以提高稳定性
                options.add_argument('--window-size=1920,1080')
                options.add_argument('--start-maximized')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-notifications')
                options.add_argument('--disable-popup-blocking')
                
                try:
                    # 尝试使用webdriver-manager自动管理驱动
                    from selenium.webdriver.chrome.service import Service
                    from webdriver_manager.chrome import ChromeDriverManager
                    
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                except Exception as e:
                    logger.warning(f"webdriver-manager初始化失败，尝试直接使用Chrome: {e}")
                    # 如果webdriver-manager失败，尝试直接使用系统Chrome
                    self.driver = webdriver.Chrome(options=options)
                
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
            elif self.browser.lower() == 'firefox':
                # 类似地，可以添加Firefox支持
                pass
            else:
                raise ValueError(f"不支持的浏览器: {self.browser}")
            
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info(f"Selenium浏览器初始化成功: {self.browser}")
            return True
            
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            
            # 提供具体的错误解决建议
            print(f"\n❌ 浏览器初始化失败: {e}")
            print("\n📋 可能的解决方案:")
            print("1. 确保已安装 Chrome 浏览器")
            print("2. 检查网络连接")
            print("3. 尝试手动下载 ChromeDriver:")
            print("   - 查看 Chrome 版本: chrome://settings/help")
            print("   - 下载对应版本的 ChromeDriver: https://chromedriver.chromium.org/")
            print("   - 将 chromedriver.exe 放在 Python 脚本目录或添加到 PATH")
            print("4. 使用已有的 Chrome 用户数据目录:")
            print("   - 添加参数: user_data_dir='C:/Users/你的用户名/AppData/Local/Google/Chrome/User Data'")
            
            return False
    
    def login_with_cookies(self, url="https://www.xiaohongshu.com"):
        """
        使用cookie登录小红书
        """
        try:
            # 首先访问小红书主页
            self.driver.get(url)
            time.sleep(2)
            
            # 检查是否已经有cookie文件
            if os.path.exists(self.cookies_file):
                logger.info(f"找到cookie文件: {self.cookies_file}")
                self.load_cookies()
                self.driver.refresh()
                time.sleep(3)
                
                # 检查登录状态
                if self.is_logged_in():
                    logger.info("✅ 已通过cookie自动登录")
                    return True
                else:
                    logger.info("❌ Cookie已失效，需要重新登录")
            
            # 如果没有cookie或cookie失效，手动登录
            logger.info("📱 请扫描页面上的二维码登录小红书...")
            logger.info("等待30秒供您扫码登录...")
            
            # 等待用户扫码登录
            for i in range(30):
                time.sleep(1)
                if self.is_logged_in():
                    logger.info("✅ 登录成功！")
                    self.save_cookies()
                    return True
                # 每5秒打印一次等待信息
                if i % 5 == 0:
                    logger.info(f"等待中... ({i+1}/30秒)")
            
            logger.warning("⚠️ 登录超时，继续尝试无登录状态访问")
            return False
            
        except Exception as e:
            logger.error(f"登录过程中发生错误: {e}")
            return False
    
    def is_logged_in(self):
        """
        检查是否已登录
        """
        try:
            # 检查是否有登录弹窗
            login_popup_selectors = [
                ".login-container",
                ".login-dialog", 
                ".login-box",
                ".login-modal",
                ".qrcode-login-container",
                "[class*='login']",
                "[class*='Login']"
            ]
            
            for selector in login_popup_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            logger.debug(f"发现登录弹窗: {selector}")
                            return False
                except:
                    continue
            
            # 检查是否有用户头像或登录入口
            user_avatar_selectors = [
                ".avatar",
                ".user-avatar",
                ".header-avatar",
                ".nav-avatar",
                "[class*='avatar']",
                "[class*='Avatar']"
            ]
            
            for selector in user_avatar_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements:
                            if element.is_displayed():
                                logger.debug(f"发现用户头像: {selector}")
                                return True
                except:
                    continue
            
            # 检查页面是否有"登录"字样
            page_text = self.driver.page_source
            login_keywords = ["立即登录", "登录后查看", "登录解锁", "请先登录", "登录小红书"]
            for keyword in login_keywords:
                if keyword in page_text:
                    logger.debug(f"发现登录提示: {keyword}")
                    return False
                    
            # 检查是否有搜索框（已登录状态通常显示搜索框）
            search_box_selectors = [
                ".search-input",
                ".search-box",
                "input[placeholder*='搜索']",
                "[class*='search']"
            ]
            
            for selector in search_box_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements:
                            if element.is_displayed():
                                logger.debug(f"发现搜索框: {selector}")
                                return True
                except:
                    continue
            
            logger.debug("无法确定登录状态，默认返回False")
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态时出错: {e}")
            return False
    
    def save_cookies(self):
        """
        保存cookies到文件
        """
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Cookies已保存到: {self.cookies_file} ({len(cookies)}个)")
            return True
        except Exception as e:
            logger.error(f"保存cookies失败: {e}")
            return False
    
    def load_cookies(self):
        """
        从文件加载cookies
        """
        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            logger.info(f"正在加载 {len(cookies)} 个cookies...")
            
            # 清除现有cookies
            self.driver.delete_all_cookies()
            
            # 添加新的cookies
            loaded_count = 0
            for cookie in cookies:
                try:
                    # 修复domain，确保包含.xiaohongshu.com
                    if 'domain' in cookie and 'xiaohongshu.com' not in cookie['domain']:
                        cookie['domain'] = '.xiaohongshu.com'
                    
                    self.driver.add_cookie(cookie)
                    loaded_count += 1
                except Exception as e:
                    logger.debug(f"无法添加cookie: {cookie.get('name', 'unknown')}, 错误: {e}")
                    continue
            
            logger.info(f"✅ 已成功加载 {loaded_count}/{len(cookies)} 个cookies")
            return True
        except Exception as e:
            logger.error(f"加载cookies失败: {e}")
            return False
    
    def force_login_required(self, url):
        """
        强制要求登录的页面处理
        """
        try:
            current_url = self.driver.current_url
            page_text = self.driver.page_source
            
            # 检查是否是登录页面
            if "passport.xiaohongshu.com" in current_url or "login" in current_url:
                logger.warning("检测到登录页面，需要重新登录")
                return True
                
            # 检查页面内容是否有登录提示
            login_keywords = ["登录后查看", "立即登录", "登录解锁", "登录后继续", "请先登录"]
            for keyword in login_keywords:
                if keyword in page_text:
                    logger.warning(f"页面提示需要登录: {keyword}")
                    return True
            
            return False
        except:
            return False

    def get_page(self, url, wait_selector=None, timeout=10):
        """
        访问页面，并处理可能的登录弹窗
        """
        try:
            logger.info(f"访问页面: {url}")
            self.driver.get(url)
            
            # 等待页面加载
            if wait_selector:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
                except TimeoutException:
                    logger.warning(f"等待元素超时: {wait_selector}")
            else:
                time.sleep(3)  # 默认等待3秒
            
            # 尝试关闭登录弹窗
            self.close_login_popup()
            
            return True
            
        except TimeoutException:
            logger.warning(f"页面加载超时: {url}")
            return False
        except Exception as e:
            logger.error(f"访问页面时发生错误: {e}")
            return False
    
    def close_login_popup(self):
        """
        关闭登录弹窗
        """
        try:
            # 等待弹窗出现
            time.sleep(2)
            
            # 尝试多种关闭方式
            close_selectors = [
                "div[class*='close']",
                "i[class*='close']",
                "svg[class*='close']",
                "button[class*='close']",
                ".close-btn",
                ".cancel-btn",
                ".icon-close",
                "[aria-label='关闭']",
                "[class*='close-icon']"
            ]
            
            for selector in close_selectors:
                try:
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in close_buttons:
                        if btn.is_displayed():
                            try:
                                btn.click()
                                logger.info(f"找到登录弹窗关闭按钮: {selector}")
                                time.sleep(1)
                                return True
                            except:
                                # 如果点击失败，尝试使用JavaScript点击
                                self.driver.execute_script("arguments[0].click();", btn)
                                logger.info(f"使用JS点击关闭按钮: {selector}")
                                time.sleep(1)
                                return True
                except:
                    continue
            
            # 如果没有找到关闭按钮，尝试按ESC键
            try:
                from selenium.webdriver.common.keys import Keys
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                logger.info("尝试按ESC键关闭弹窗")
                time.sleep(1)
            except:
                pass
            
            return False
            
        except Exception as e:
            logger.debug(f"关闭登录弹窗时出错: {e}")
            return False
    
    def extract_images(self, selector="img"):
        """
        提取页面中的图片
        """
        try:
            images = self.driver.find_elements(By.CSS_SELECTOR, selector)
            img_urls = []
            
            for img in images:
                src = img.get_attribute('src')
                if src and src.startswith('http'):
                    img_urls.append(src)
            
            logger.info(f"提取到 {len(img_urls)} 张图片")
            return img_urls
            
        except Exception as e:
            logger.error(f"提取图片时出错: {e}")
            return []
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except:
                pass