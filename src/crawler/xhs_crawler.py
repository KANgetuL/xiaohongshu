import time
import logging
import os
from selenium_handler import SeleniumHandler
from parser import XHSParser
from request_handler import RequestHandler

logger = logging.getLogger(__name__)

class SimpleXHSCrawler:
    def __init__(self):
        self.selenium_handler = None
        self.parser = XHSParser()
        self.request_handler = RequestHandler()
        self.collected_notes = []
        
    def run_crawler(self, max_items=3, headless=False):
        """
        运行爬虫主程序（修改版）
        """
        try:
            # 检查cookie文件是否存在
            cookies_file = "xiaohongshu_cookies.json"
            if os.path.exists(cookies_file):
                logger.info(f"📁 发现cookie文件: {cookies_file}")
            else:
                logger.info("📁 未找到cookie文件，需要首次登录")
            
            # 初始化浏览器
            self.selenium_handler = SeleniumHandler(
                browser='chrome',
                headless=headless,
                user_data_dir=None  # 可以设置为你的Chrome用户数据目录
            )
            
            if not self.selenium_handler.initialize():
                logger.error("浏览器初始化失败")
                return
            
            # 步骤1: 先登录
            logger.info("🔐 开始登录小红书...")
            print("\n" + "="*50)
            print("小红书登录提示：")
            print("1. 浏览器将打开小红书页面")
            print("2. 请扫描页面上的二维码登录")
            print("3. 登录成功后，程序会自动保存cookies")
            print("4. 下次运行将自动使用保存的cookies")
            print("="*50 + "\n")
            
            login_success = self.selenium_handler.login_with_cookies()
            
            if not login_success:
                logger.warning("⚠️ 登录失败或未完成登录")
                print("\n⚠️ 注意：未登录状态下，小红书可能限制搜索功能")
                print("建议：")
                print("1. 手动访问: https://www.xiaohongshu.com")
                print("2. 扫码登录")
                print("3. 关闭浏览器")
                print("4. 重新运行程序")
                print("\n是否继续尝试？(y/n): ", end="")
                choice = input().strip().lower()
                
                if choice != 'y':
                    self.selenium_handler.close()
                    return
            
            # 步骤2: 开始爬取
            logger.info("🚀 开始爬取小红书内容...")
            
            # 搜索关键词列表
            keywords = ["外卖翻车", "点餐翻车", "外卖漫画", "点餐漫画"]
            
            for keyword in keywords:
                if len(self.collected_notes) >= max_items:
                    break
                    
                logger.info(f"处理关键词: {keyword}")
                
                # 构建搜索URL
                import urllib.parse
                encoded_keyword = urllib.parse.quote(keyword)
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}"
                
                # 访问搜索页面
                logger.info(f"搜索关键词: {keyword}")
                if self.selenium_handler.get_page(search_url, wait_selector=".feeds-container"):
                    # 等待页面加载
                    time.sleep(3)
                    
                    # 检查是否登录状态
                    if not self.selenium_handler.is_logged_in():
                        logger.warning(f"⚠️ 搜索'{keyword}'时可能受限，尝试重新登录")
                        self.selenium_handler.login_with_cookies(search_url)
                    
                    # 获取页面源码
                    page_source = self.selenium_handler.driver.page_source
                    
                    # 解析笔记列表
                    notes = self.parser.parse_search_results(page_source)
                    
                    if not notes:
                        logger.warning(f"未找到关键词'{keyword}'的笔记")
                        continue
                    
                    logger.info(f"解析到 {len(notes)} 个笔记")
                    
                    for note in notes:
                        if len(self.collected_notes) >= max_items:
                            break
                            
                        note_id = note.get('note_id')
                        if not note_id:
                            continue
                            
                        logger.info(f"处理笔记: {note_id}")
                        
                        # 访问笔记详情页
                        note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
                        if self.selenium_handler.get_page(note_url, wait_selector=".note-container"):
                            # 等待页面加载
                            time.sleep(2)
                            
                            # 解析笔记详情
                            note_detail = self.parser.parse_note_page(
                                self.selenium_handler.driver.page_source
                            )
                            
                            # 验证笔记是否符合要求
                            if self.validate_note(note_detail):
                                # 下载图片
                                success = self.download_note_images(note_detail)
                                if success:
                                    self.collected_notes.append(note_detail)
                                    logger.info(f"成功收集连环画 {len(self.collected_notes)}/{max_items}: {note_detail.get('title', '无标题')}")
                            else:
                                logger.warning(f"笔记验证失败: {note_id}")
            
            logger.info(f"🎉 爬取完成，共收集 {len(self.collected_notes)} 个笔记")
            
            # 显示收集结果
            if self.collected_notes:
                print("\n" + "="*50)
                print("📊 收集结果：")
                for i, note in enumerate(self.collected_notes, 1):
                    print(f"{i}. {note.get('title', '无标题')} (图片数: {len(note.get('images', []))})")
                print("="*50)
            
        except Exception as e:
            logger.error(f"爬虫运行失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.selenium_handler:
                self.selenium_handler.close()
    
    def validate_note(self, note):
        """验证笔记是否符合要求"""
        try:
            # 检查标题长度（至少6个字符）
            title = note.get('title', '')
            if len(title) < 6:
                logger.debug(f"标题太短: {title}")
                return False
            
            # 检查图片数量（至少3张）
            images = note.get('images', [])
            if len(images) < 3:
                logger.debug(f"图片数量不足: {len(images)}")
                return False
            
            # 检查是否有有效内容
            content = note.get('content', '')
            if not content or len(content.strip()) < 10:
                logger.debug("内容太少或为空")
                return False
            
            return True
        except:
            return False
    
    def download_note_images(self, note):
        """下载笔记中的图片"""
        try:
            images = note.get('images', [])
            note_id = note.get('note_id', 'unknown')
            
            if not images:
                return False
            
            # 创建保存目录
            import os
            import time
            timestamp = int(time.time() * 1000)
            save_dir = f"data/processed/comics/comic_{timestamp}_{note_id}"
            os.makedirs(save_dir, exist_ok=True)
            os.makedirs(f"{save_dir}/images", exist_ok=True)
            
            # 下载图片
            downloaded_count = 0
            for i, img_url in enumerate(images[:10]):  # 最多下载10张
                if downloaded_count >= 3:  # 至少需要3张
                    break
                    
                try:
                    # 使用request_handler下载图片
                    filename = f"image_{i+1:02d}.jpg"
                    save_path = f"{save_dir}/images/{filename}"
                    
                    success = self.request_handler.download_image(img_url, save_path)
                    if success:
                        downloaded_count += 1
                        logger.info(f"下载图片 {i+1}/{len(images)}: {filename}")
                    else:
                        logger.warning(f"图片下载失败: {img_url}")
                except Exception as e:
                    logger.error(f"下载图片时出错: {e}")
            
            # 保存笔记信息
            note_info = {
                'note_id': note_id,
                'title': note.get('title', ''),
                'content': note.get('content', ''),
                'images_count': len(images),
                'downloaded_count': downloaded_count,
                'url': f"https://www.xiaohongshu.com/explore/{note_id}",
                'collected_time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'save_dir': save_dir
            }
            
            import json
            with open(f"{save_dir}/note_info.json", 'w', encoding='utf-8') as f:
                json.dump(note_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"连环画数据保存成功: {save_dir}")
            return downloaded_count >= 3
            
        except Exception as e:
            logger.error(f"下载笔记图片失败: {e}")
            return False