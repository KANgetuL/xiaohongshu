import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from config.settings import (
    CRAWLER_SETTINGS, FILTER_RULES, COMICS_DIR,
    SELENIUM_SETTINGS, TAGS
)
from config.constants import DATA_TEMPLATE
from src.crawler.selenium_handler import SeleniumHandler
from src.crawler.parser import XHSParser
from src.crawler.request_handler import RequestHandler
from src.utils.helper import generate_id, safe_json_dump, format_timestamp
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)


class SimpleXHSCrawler:
    def __init__(self, max_comics: int = 3, headless: bool = False):
        """
        初始化爬虫
        
        Args:
            max_comics: 最大收集数量
            headless: 是否无头模式
        """
        self.max_comics = max_comics
        self.headless = headless
        
        # 组件实例
        self.selenium_handler = None
        self.parser = None
        self.request_handler = None
        
        # 数据存储
        self.collected_comics = []
        self.stats = {
            'total_found': 0,
            'total_collected': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 初始化日志
        self.logger = setup_logger("xhs_crawler")
    
    def initialize(self) -> bool:
        """初始化各个组件"""
        try:
            # 初始化Selenium处理器
            self.selenium_handler = SeleniumHandler(
                browser='chrome',
                headless=self.headless,
                user_data_dir=None
            )
            
            if not self.selenium_handler.initialize():
                self.logger.error("Selenium浏览器初始化失败")
                return False
            
            # 初始化解析器
            self.parser = XHSParser()
            
            # 初始化请求处理器
            self.request_handler = RequestHandler()
            
            self.logger.info("所有组件初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False
    
    def crawl(self) -> Optional[Dict[str, Any]]:
        """
        主爬取流程
        
        Returns:
            爬取报告，失败返回None
        """
        self.stats['start_time'] = format_timestamp()
        self.logger.info("开始爬取流程")
        
        # 初始化组件
        if not self.initialize():
            return None
        
        try:
            # 登录小红书
            if not self.login_xiaohongshu():
                self.logger.warning("登录失败或未完全登录，继续尝试爬取")
            
            # 搜索关键词并爬取
            keywords = CRAWLER_SETTINGS["search_keywords"]
            self.logger.info(f"搜索关键词: {keywords}")
            
            for keyword in keywords:
                if len(self.collected_comics) >= self.max_comics:
                    break
                
                self.logger.info(f"处理关键词: {keyword}")
                self.search_and_crawl(keyword)
            
            # 更新统计信息
            self.stats['end_time'] = format_timestamp()
            self.stats['total_collected'] = len(self.collected_comics)
            
            # 生成报告
            report = self.generate_report()
            
            self.logger.info(f"爬取完成，共收集 {len(self.collected_comics)} 个连环画")
            return report
            
        except Exception as e:
            self.logger.error(f"爬取过程中出错: {e}", exc_info=True)
            return None
        
        finally:
            self.close()
    
    def login_xiaohongshu(self) -> bool:
        """登录小红书"""
        try:
            self.logger.info("开始登录小红书...")
            
            # 先访问小红书主页
            login_success = self.selenium_handler.login_with_cookies()
            
            if login_success:
                self.logger.info("✅ 登录成功")
                return True
            else:
                self.logger.warning("登录失败或未完成登录")
                return False
                
        except Exception as e:
            self.logger.error(f"登录过程中出错: {e}")
            return False
    
    def search_and_crawl(self, keyword: str):
        """搜索关键词并爬取内容"""
        try:
            # 构建搜索URL
            import urllib.parse
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}"
            
            # 访问搜索页面
            self.logger.info(f"访问搜索页面: {search_url}")
            if not self.selenium_handler.get_page(search_url, wait_selector=".feeds-container"):
                self.logger.warning(f"搜索页面访问失败: {keyword}")
                return
            
            # 等待页面加载
            time.sleep(CRAWLER_SETTINGS.get("scroll_pause_time", 3))
            
            # 检查登录状态
            if not self.selenium_handler.is_logged_in():
                self.logger.warning(f"搜索'{keyword}'时可能受限，尝试重新登录")
                self.selenium_handler.login_with_cookies(search_url)
            
            # 获取页面源码
            page_source = self.selenium_handler.driver.page_source
            
            # 解析搜索结果 - 使用新的方法名
            notes = self.parser.parse_search_results_direct(page_source, keyword)
            self.logger.info(f"解析到 {len(notes)} 个笔记")
            
            if not notes:
                self.logger.warning(f"未找到关键词'{keyword}'的笔记")
                return
            
            # 处理每个笔记
            for note in notes:
                if len(self.collected_comics) >= self.max_comics:
                    break
                
                self.process_note(note)
                
        except Exception as e:
            self.logger.error(f"搜索爬取失败: {e}", exc_info=True)
    
    def process_note(self, note_info: Dict[str, Any]):
        """处理单个笔记"""
        try:
            note_id = note_info.get('note_id')
            if not note_id:
                return
            
            self.logger.info(f"处理笔记: {note_id}")
            
            # 访问笔记详情页
            note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
            if not self.selenium_handler.get_page(note_url, wait_selector=".note-container"):
                self.logger.warning(f"笔记页面访问失败: {note_id}")
                return
            
            # 等待页面加载
            time.sleep(2)
            
            # 解析笔记详情
            note_detail = self.parser.parse_note_detail_direct(
                self.selenium_handler.driver.page_source,
                note_url
            )
            
            # 验证笔记是否符合要求
            if self.validate_note(note_detail):
                # 处理为连环画格式
                comic_data = self.process_to_comic(note_detail)
                
                if comic_data and self.save_comic(comic_data):
                    self.collected_comics.append(comic_data)
                    self.logger.info(f"成功收集连环画 {len(self.collected_comics)}/{self.max_comics}: {comic_data['title']}")
            else:
                self.logger.debug(f"笔记验证失败: {note_id}")
                
        except Exception as e:
            self.logger.error(f"处理笔记失败: {e}", exc_info=True)
    
    def validate_note(self, note: Dict[str, Any]) -> bool:
        """验证笔记是否符合要求"""
        try:
            # 检查图片数量
            images = note.get('images', [])
            if len(images) < 3:  # 至少3张图片
                self.logger.debug(f"图片数量不足: {len(images)}")
                return False
            
            # 检查内容长度
            content = note.get('content', '')
            if not content or len(content.strip()) < 10:
                self.logger.debug("内容太少或为空")
                return False
            
            # 主题过滤 - 确保是"外卖/点餐翻车"相关
            title = note.get('title', '').lower()
            content_lower = content.lower()
            
            # 检查是否包含主题关键词
            theme_keywords = ['外卖', '点餐', '翻车', '吃啥', '漫画', '送餐', '饿了么', '美团']
            
            has_theme = any(keyword in title or keyword in content_lower 
                        for keyword in theme_keywords)
            
            if not has_theme:
                self.logger.debug(f"笔记不符合主题: {title[:30]}...")
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"验证笔记时出错: {e}")
            return False
        
    def process_to_comic(self, note: Dict[str, Any]) -> Dict[str, Any]:
        """将笔记处理为连环画格式"""
        try:
            comic_id = f"comic_{len(self.collected_comics) + 1:03d}"
            
            comic_data = {
                'comic_id': comic_id,
                'note_id': note.get('note_id', ''),
                'title': note.get('title', '未命名连环画'),
                'content': note.get('content', ''),
                'original_url': note.get('url', ''),
                'tags': note.get('tags', []) + TAGS['primary_tags'],
                'images': note.get('images', []),
                'create_time': format_timestamp(),
                'image_count': len(note.get('images', [])),
                'username': note.get('username', ''),
                'likes': note.get('likes', 0)
            }
            
            return comic_data
            
        except Exception as e:
            self.logger.error(f"处理连环画数据失败: {e}")
            return None
    
    def save_comic(self, comic_data: Dict[str, Any]) -> bool:
        """保存连环画数据"""
        try:
            # 创建连环画目录
            comic_id = comic_data['comic_id']
            comic_dir = COMICS_DIR / comic_id
            images_dir = comic_dir / 'images'
            
            comic_dir.mkdir(parents=True, exist_ok=True)
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # 下载图片
            downloaded_images = []
            images = comic_data.get('images', [])
            
            for i, img_info in enumerate(images[:6]):  # 最多6张
                img_url = img_info['url'] if isinstance(img_info, dict) else img_info
                
                try:
                    img_name = f"image_{i+1:02d}.jpg"
                    img_path = images_dir / img_name
                    
                    # 下载图片
                    success, message = self.request_handler.download_image(img_url, str(img_path))
                    
                    if success:
                        downloaded_images.append({
                            'filename': img_name,
                            'path': str(img_path.relative_to(COMICS_DIR)),
                            'order': i + 1,
                            'original_url': img_url
                        })
                        self.logger.info(f"下载图片成功: {img_name}")
                    else:
                        self.logger.warning(f"下载图片失败: {message}")
                        
                except Exception as e:
                    self.logger.error(f"下载图片时出错: {e}")
            
            if len(downloaded_images) < 3:  # 至少需要3张合格图片
                self.logger.warning(f"合格图片数量不足: {len(downloaded_images)}")
                return False
            
            # 更新图片信息
            comic_data['images'] = downloaded_images
            comic_data['downloaded_image_count'] = len(downloaded_images)
            
            # 保存metadata
            meta_path = comic_dir / 'meta.json'
            safe_json_dump(comic_data, meta_path)
            
            # 生成标注文件
            self.generate_annotations(comic_data, comic_dir)
            
            self.logger.info(f"连环画保存成功: {comic_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存连环画失败: {e}")
            return False
    
    def generate_annotations(self, comic_data: Dict[str, Any], comic_dir: Path):
        """生成标注JSON文件"""
        try:
            annotations = {}
            
            for img_info in comic_data['images']:
                image_key = img_info['filename']
                annotations[image_key] = {
                    'image_path': img_info['path'],
                    'text': comic_data['content'][:200],  # 截取前200字符作为标注
                    'order': img_info['order'],
                    'tags': comic_data['tags']
                }
            
            # 保存到当前连环画目录
            annotations_path = comic_dir / 'annotations.json'
            safe_json_dump(annotations, annotations_path)
            
            # 更新全局标注文件
            self.update_global_annotations(annotations)
            
            self.logger.info(f"标注文件生成成功: {annotations_path}")
            
        except Exception as e:
            self.logger.error(f"生成标注文件失败: {e}")
    
    def update_global_annotations(self, new_annotations: Dict[str, Any]):
        """更新全局标注文件"""
        try:
            from config.settings import COMICS_DIR
            global_annotations_path = COMICS_DIR / 'annotations.json'
            
            # 初始化或读取现有标注
            all_annotations = {}
            
            if global_annotations_path.exists():
                try:
                    # 尝试读取文件
                    with open(global_annotations_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:  # 确保文件不为空
                            all_annotations = json.loads(content)
                except (json.JSONDecodeError, Exception) as e:
                    self.logger.warning(f"全局标注文件损坏，重新创建: {e}")
                    all_annotations = {}
            
            # 合并新标注
            all_annotations.update(new_annotations)
            
            # 保存
            with open(global_annotations_path, 'w', encoding='utf-8') as f:
                json.dump(all_annotations, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"全局标注文件更新成功: {global_annotations_path}")
            
        except Exception as e:
            self.logger.error(f"更新全局标注文件失败: {e}")  
    
    def generate_report(self) -> Dict[str, Any]:
        """生成爬取报告"""
        report = {
            'stats': {
                'total_found': self.stats.get('total_found', 0),
                'total_collected': len(self.collected_comics),
                'start_time': self.stats.get('start_time'),
                'end_time': self.stats.get('end_time')
            },
            'collected_comics': [
                {
                    'comic_id': comic['comic_id'],
                    'title': comic['title'],
                    'image_count': comic.get('downloaded_image_count', 0),
                    'create_time': comic.get('create_time')
                }
                for comic in self.collected_comics
            ],
            'summary': {
                'success_rate': (len(self.collected_comics) / max(self.stats.get('total_found', 1), 1)) * 100,
                'status': 'completed' if len(self.collected_comics) > 0 else 'no_data'
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any]):
        """保存报告到文件"""
        try:
            report_path = COMICS_DIR / 'crawl_report.json'
            safe_json_dump(report, report_path)
            self.logger.info(f"报告已保存到: {report_path}")
            
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
    
    def close(self):
        """关闭爬虫"""
        if self.selenium_handler:
            self.selenium_handler.close()
        if self.request_handler:
            self.request_handler.close()
        self.logger.info("爬虫已关闭")