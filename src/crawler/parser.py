"""
页面解析器模块
解析HTML/JSON，提取图片和文本数据
支持小红书页面解析
"""

import re
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, urljoin, unquote

from bs4 import BeautifulSoup

from config.settings import TAGS
from src.utils.logger import setup_logger


class XHSParser:
    """小红书页面解析器"""
    
    def __init__(self):
        self.logger = setup_logger("xhs_parser")
    
    def parse_search_results_direct(self, page_source: str, keyword: str) -> List[Dict[str, Any]]:
        """
        解析小红书直接搜索结果页面
        """
        notes = []
        
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 小红书搜索结果有多种布局，尝试多种选择器
            selectors = [
                'div[data-note-id]',  # 小红书2024年新的数据结构
                'div.note-item',       # 笔记项
                'article',             # 文章标签
                'div[class*="note-"]', # 包含note的类
                'div[class*="feed-"]', # feed流
                'div[class*="card-"]', # 卡片
                'a[href*="/explore/"]', # 探索链接
                'div[class*="item"]',   # item类
                'section',              # 区块
            ]
            
            all_elements = []
            for selector in selectors:
                elements = soup.select(selector)
                all_elements.extend(elements)
                self.logger.debug(f"选择器 '{selector}' 找到 {len(elements)} 个元素")
            
            # 去重
            unique_elements = []
            seen = set()
            for elem in all_elements:
                elem_str = str(elem)
                if len(elem_str) > 100 and elem_str not in seen:  # 过滤太小的元素
                    seen.add(elem_str)
                    unique_elements.append(elem)
            
            self.logger.info(f"总共找到 {len(unique_elements)} 个候选元素")
            
            # 尝试不同的提取方法
            for element in unique_elements[:50]:  # 限制处理数量
                # 尝试多种提取方法
                note_info = None
                
                # 方法1: 新方法
                note_info = self._extract_note_from_element_v2(element)
                
                # 方法2: 如果新方法失败，尝试旧方法
                if not note_info:
                    note_info = self._extract_note_from_element(element)
                
                if note_info and self._validate_note_info(note_info):
                    # 关键词过滤：确保笔记内容与关键词相关
                    if self._is_related_to_keyword(note_info, keyword):
                        note_info['search_keyword'] = keyword
                        notes.append(note_info)
                        
            self.logger.info(f"成功解析 {len(notes)} 个笔记")
            
        except Exception as e:
            self.logger.error(f"解析搜索结果失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return notes

    def _is_related_to_keyword(self, note_info: Dict[str, Any], keyword: str) -> bool:
        """
        检查笔记是否与关键词相关
        """
        # 提取所有文本
        texts = []
        if note_info.get('title'):
            texts.append(note_info['title'].lower())
        if note_info.get('content'):
            texts.append(note_info['content'].lower())
        if note_info.get('tags'):
            for tag in note_info['tags']:
                texts.append(tag.lower())
        
        all_text = ' '.join(texts)
        
        # 关键词字典
        keyword_dict = {
            '外卖翻车': ['外卖', '翻车', '美团', '饿了么', '送餐', '外卖小哥', '点餐', '吃啥'],
            '点餐翻车': ['点餐', '翻车', '外卖', '美团', '饿了么', '餐厅', '吃啥'],
            '外卖漫画': ['外卖', '漫画', '美团', '饿了么', '送餐', '画', '插图'],
            '点餐漫画': ['点餐', '漫画', '外卖', '餐厅', '画', '插图']
        }
        
        # 获取相关关键词
        related_keywords = keyword_dict.get(keyword, [keyword])
        
        # 检查是否包含任一关键词
        for kw in related_keywords:
            if kw in all_text:
                return True
        
        return False

    def _extract_note_from_element(self, element) -> Optional[Dict[str, Any]]:
        """
        从元素中提取笔记信息（兼容旧版本）
        
        Args:
            element: BeautifulSoup元素
            
        Returns:
            笔记信息字典
        """
        try:
            note_info = {}
            
            # 1. 提取笔记ID和URL
            note_id = None
            note_url = None
            
            # 查找包含/explore/的链接
            links = element.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/explore/' in href:
                    # 提取笔记ID
                    match = re.search(r'/explore/([a-f0-9]+)', href)
                    if match:
                        note_id = match.group(1)
                        note_url = urljoin('https://www.xiaohongshu.com', href)
                        break
            
            if not note_id:
                # 尝试从其他属性提取
                if element.has_attr('data-note-id'):
                    note_id = element['data-note-id']
                elif element.has_attr('data-id'):
                    data_id = element['data-id']
                    if len(data_id) == 24:  # 小红书笔记ID通常是24位十六进制
                        note_id = data_id
            
            if not note_id:
                return None
            
            note_info['note_id'] = note_id
            note_info['url'] = note_url or f"https://www.xiaohongshu.com/explore/{note_id}"
            
            # 2. 提取标题和描述
            text_elements = element.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'div', 'span'])
            texts = []
            for elem in text_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 5 and len(text) < 200:
                    texts.append(text)
            
            if texts:
                # 取最长的文本作为标题
                note_info['title'] = max(texts, key=len)
                
                # 所有文本作为内容
                note_info['content'] = ' '.join(texts[:3])  # 只取前3个
            
            # 3. 提取封面图片
            img_elements = element.find_all('img', src=True)
            for img in img_elements:
                src = img.get('src')
                if src and 'http' in src:
                    # 过滤小图标
                    if any(x in src.lower() for x in ['icon', 'avatar', 'logo', 'default']):
                        continue
                    
                    # 确保URL完整
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = urljoin('https://www.xiaohongshu.com', src)
                    
                    note_info['cover_url'] = src
                    break
            
            # 4. 提取用户信息
            user_elements = element.find_all(['div', 'span'], class_=re.compile(r'user|author|name'))
            for user_elem in user_elements:
                text = user_elem.get_text(strip=True)
                if text and 2 <= len(text) <= 20:
                    note_info['username'] = text
                    break
            
            # 5. 提取标签
            tags = []
            tag_elements = element.find_all(['a', 'span'], class_=re.compile(r'tag|topic|label'))
            for tag_elem in tag_elements:
                tag_text = tag_elem.get_text(strip=True)
                if tag_text and tag_text.startswith('#'):
                    tags.append(tag_text[1:])  # 去掉#号
            
            # 从文本中提取标签
            all_text = element.get_text()
            hash_tags = re.findall(r'#([^#\s]+)', all_text)
            tags.extend(hash_tags[:5])  # 最多取5个
            
            note_info['tags'] = list(set(tags))
            
            return note_info
            
        except Exception as e:
            self.logger.debug(f"提取笔记信息失败: {str(e)}")
            return None

    def _extract_note_from_element_v2(self, element) -> Optional[Dict[str, Any]]:
        """
        备用方法提取笔记信息
        """
        try:
            # 方法1: 从data-note-id属性提取
            if element.has_attr('data-note-id'):
                note_id = element['data-note-id']
                if len(note_id) == 24:  # 小红书笔记ID通常是24位十六进制
                    return self._extract_from_element_with_id(element, note_id)
            
            # 方法2: 从链接中提取
            links = element.find_all('a', href=True)
            for link in links:
                href = link['href']
                if '/explore/' in href:
                    match = re.search(r'/explore/([a-f0-9]{24})', href)
                    if match:
                        note_id = match.group(1)
                        return self._extract_from_element_with_id(element, note_id)
            
            # 方法3: 从类名中识别
            element_str = str(element)
            if 'data-note-id' in element_str:
                match = re.search(r'data-note-id="([a-f0-9]{24})"', element_str)
                if match:
                    note_id = match.group(1)
                    return self._extract_from_element_with_id(element, note_id)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"备用提取方法失败: {str(e)}")
            return None

    def _extract_from_element_with_id(self, element, note_id: str) -> Dict[str, Any]:
        """
        从具有ID的元素中提取信息
        """
        note_info = {'note_id': note_id}
        
        # 提取标题
        title_elements = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'div', 'span'])
        for elem in title_elements:
            text = elem.get_text(strip=True)
            if 5 <= len(text) <= 100:  # 合理的标题长度
                note_info['title'] = text
                break
        
        # 提取内容
        content_elements = element.find_all(['p', 'div', 'span'])
        content_texts = []
        for elem in content_elements:
            text = elem.get_text(strip=True)
            if 10 <= len(text) <= 200:
                content_texts.append(text)
        
        if content_texts:
            note_info['content'] = ' '.join(content_texts[:3])
        
        # 提取图片
        img_elements = element.find_all('img', src=True)
        for img in img_elements:
            src = img.get('src')
            if src and 'http' in src and not any(x in src.lower() for x in ['icon', 'avatar', 'logo']):
                note_info['cover_url'] = src
                break
        
        return note_info    
    def _validate_note_info(self, note_info: Dict[str, Any]) -> bool:
        """
        验证笔记信息是否有效
        
        Args:
            note_info: 笔记信息
            
        Returns:
            是否有效
        """
        # 必须有note_id
        if not note_info.get('note_id'):
            return False
        
        # 应该有标题或内容
        if not note_info.get('title') and not note_info.get('content'):
            return False
        
        # 笔记ID应该是24位十六进制
        note_id = note_info['note_id']
        if not re.match(r'^[a-f0-9]{24}$', note_id):
            return False
        
        return True
    
    def parse_note_detail_direct(self, page_source: str, note_url: str) -> Dict[str, Any]:
        """
        解析笔记详情页面
        
        Args:
            page_source: 页面HTML源代码
            note_url: 笔记URL
            
        Returns:
            笔记详情字典
        """
        note_detail = {
            'note_id': '',
            'title': '',
            'content': '',
            'images': [],
            'tags': [],
            'username': '',
            'publish_time': '',
            'likes': 0,
            'comments': 0,
            'collections': 0,
            'url': note_url,
        }
        
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 1. 从script标签提取JSON数据（主要方法）
            json_data = self._extract_json_data(soup)
            if json_data:
                parsed_data = self._parse_json_data(json_data)
                note_detail.update(parsed_data)
            
            # 2. 如果JSON解析失败，从HTML提取
            if not note_detail.get('note_id') or not note_detail.get('content'):
                html_data = self._parse_html_data(soup)
                note_detail.update(html_data)
            
            # 3. 确保有note_id
            if not note_detail['note_id']:
                note_detail['note_id'] = self._extract_note_id_from_url(note_url)
            
            # 4. 提取图片（如果JSON中没有）
            if not note_detail['images']:
                note_detail['images'] = self._extract_images_from_html(soup)
            
            # 5. 清理数据
            note_detail = self._clean_note_data(note_detail)
            
            self.logger.info(f"解析到笔记: ID={note_detail['note_id']}, 标题长度={len(note_detail.get('title', ''))}, 图片数={len(note_detail['images'])}")
            
        except Exception as e:
            self.logger.error(f"解析笔记详情失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return note_detail
    
    def _extract_json_data(self, soup) -> Optional[Dict]:
        """从script标签中提取JSON数据"""
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if not script.string:
                continue
            
            text = script.string
            
            # 小红书常见的JSON数据模式
            patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*;',
                r'"noteDetailMap"\s*:\s*({[^}]+})',
                r'"note"\s*:\s*({[^}]+})',
                r'"id"\s*:\s*"[^"]+"[^}]+"desc"\s*:\s*"[^"]+"',
            ]
            
            for pattern in patterns:
                try:
                    match = re.search(pattern, text, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                        
                        # 清理JSON字符串
                        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                        json_str = re.sub(r',\s+}', '}', json_str)
                        json_str = re.sub(r',\s+]', ']', json_str)
                        
                        # 尝试解析
                        data = json.loads(json_str)
                        return data
                except:
                    continue
        
        return None
    
    def _parse_json_data(self, json_data: Dict) -> Dict[str, Any]:
        """从JSON数据中解析笔记信息"""
        result = {
            'note_id': '',
            'title': '',
            'content': '',
            'images': [],
            'tags': [],
            'username': '',
            'likes': 0,
        }
        
        try:
            # 深度优先搜索有用的数据
            def search_in_dict(data, target_keys, result_key=None):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key in target_keys:
                            if result_key:
                                result[result_key] = value
                            return value
                        
                        # 递归搜索
                        found = search_in_dict(value, target_keys, result_key)
                        if found is not None:
                            return found
                elif isinstance(data, list):
                    for item in data:
                        found = search_in_dict(item, target_keys, result_key)
                        if found is not None:
                            return found
                return None
            
            # 搜索笔记ID
            note_id = search_in_dict(json_data, ['id', 'noteId', 'note_id'], 'note_id')
            if note_id:
                result['note_id'] = str(note_id)
            
            # 搜索标题
            title = search_in_dict(json_data, ['title', 'noteTitle', 'name'], 'title')
            if title:
                result['title'] = str(title)
            
            # 搜索内容
            content = search_in_dict(json_data, ['desc', 'content', 'description', 'noteDesc'], 'content')
            if content:
                result['content'] = str(content)
            
            # 搜索用户名
            username = search_in_dict(json_data, ['nickname', 'name', 'username', 'userNickname'], 'username')
            if username:
                result['username'] = str(username)
            
            # 搜索点赞数
            likes = search_in_dict(json_data, ['likes', 'likeCount', 'favCount'])
            if likes:
                result['likes'] = int(likes) if str(likes).isdigit() else 0
            
            # 搜索图片
            def extract_images(data):
                images = []
                if isinstance(data, dict):
                    if 'url' in data and ('http' in str(data['url']) or '//' in str(data['url'])):
                        images.append({
                            'url': data['url'],
                            'width': data.get('width', 0),
                            'height': data.get('height', 0),
                            'caption': data.get('desc', '') or data.get('title', '')
                        })
                    else:
                        for key, value in data.items():
                            images.extend(extract_images(value))
                elif isinstance(data, list):
                    for item in data:
                        images.extend(extract_images(item))
                return images
            
            result['images'] = extract_images(json_data)
            
            # 搜索标签
            def extract_tags(data):
                tags = []
                if isinstance(data, dict):
                    if 'name' in data and isinstance(data['name'], str):
                        tags.append(data['name'])
                    else:
                        for key, value in data.items():
                            tags.extend(extract_tags(value))
                elif isinstance(data, list):
                    for item in data:
                        tags.extend(extract_tags(item))
                elif isinstance(data, str) and data.startswith('#'):
                    tags.append(data[1:])
                return tags
            
            result['tags'] = list(set(extract_tags(json_data)))
            
        except Exception as e:
            self.logger.debug(f"从JSON解析数据失败: {str(e)}")
        
        return result
    
    def _parse_html_data(self, soup) -> Dict[str, Any]:
        """从HTML元素中解析笔记信息"""
        result = {
            'title': '',
            'content': '',
            'images': [],
            'tags': [],
            'username': '',
            'likes': 0,
        }
        
        try:
            # 提取标题
            title_selectors = ['h1', '.title', '[class*="title"]', 'h2']
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    result['title'] = element.get_text(strip=True)[:100]
                    break
            
            # 提取内容
            content_selectors = ['.content', '.desc', 'article', 'main', 'section']
            for selector in content_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if len(text) > 20:
                        result['content'] = text[:500]  # 限制长度
                        break
                if result['content']:
                    break
            
            # 提取用户名
            user_selectors = ['.user-name', '.author', '.nickname', '[class*="user"]']
            for selector in user_selectors:
                element = soup.select_one(selector)
                if element:
                    result['username'] = element.get_text(strip=True)[:20]
                    break
            
            # 提取标签
            tag_elements = soup.find_all(['a', 'span'], class_=re.compile(r'tag|topic|label'))
            for elem in tag_elements:
                tag_text = elem.get_text(strip=True)
                if tag_text and '#' in tag_text:
                    tag = tag_text.replace('#', '').strip()
                    if tag and tag not in result['tags']:
                        result['tags'].append(tag)
            
            # 从文本中提取标签
            all_text = soup.get_text()
            hash_tags = re.findall(r'#([^#\s]+)', all_text)
            result['tags'].extend(hash_tags[:10])
            result['tags'] = list(set(result['tags']))
            
        except Exception as e:
            self.logger.debug(f"从HTML解析数据失败: {str(e)}")
        
        return result
    

    def parse_search_results_simple(self, page_source: str, keyword: str) -> List[Dict[str, Any]]:
        """
        简单方法解析搜索结果 - 只提取笔记ID
        """
        notes = []
        
        try:
            # 使用正则直接提取笔记ID
            note_ids = re.findall(r'/explore/([a-f0-9]{24})', page_source)
            note_ids = list(set(note_ids))  # 去重
            
            for note_id in note_ids[:20]:  # 最多20个
                note_info = {
                    'note_id': note_id,
                    'url': f"https://www.xiaohongshu.com/explore/{note_id}",
                    'title': f"笔记 {note_id}",
                    'content': f"从搜索 '{keyword}' 找到的笔记",
                    'tags': [keyword],
                    'search_keyword': keyword
                }
                notes.append(note_info)
            
            self.logger.info(f"简单方法解析到 {len(notes)} 个笔记ID")
            
        except Exception as e:
            self.logger.error(f"简单方法解析失败: {str(e)}")
        
        return notes

    
    def _extract_images_from_html(self, soup) -> List[Dict[str, Any]]:
        """从HTML中提取图片信息"""
        images = []
        
        try:
            img_elements = soup.find_all('img')
            
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if not src:
                    continue
                
                # 确保URL完整
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin('https://www.xiaohongshu.com', src)
                elif not src.startswith('http'):
                    continue
                
                # 过滤小图标
                src_lower = src.lower()
                if any(keyword in src_lower for keyword in ['icon', 'avatar', 'logo', 'spinner', 'loading', 'default']):
                    continue
                
                # 获取alt文本
                alt = img.get('alt', '')
                
                images.append({
                    'url': src,
                    'caption': alt[:100],
                    'width': 0,
                    'height': 0,
                })
            
            # 去重和限制数量
            unique_images = []
            seen_urls = set()
            for img in images:
                if img['url'] not in seen_urls:
                    seen_urls.add(img['url'])
                    unique_images.append(img)
            
            return unique_images[:20]  # 最多20张
            
        except Exception as e:
            self.logger.debug(f"从HTML提取图片失败: {str(e)}")
        
        return images
    
    def _extract_note_id_from_url(self, url: str) -> str:
        """从URL中提取笔记ID"""
        match = re.search(r'/explore/([a-f0-9]+)', url)
        return match.group(1) if match else ""
    
    def _clean_note_data(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """清理和规范化笔记数据"""
        # 清理内容
        if 'content' in note_data and note_data['content']:
            note_data['content'] = re.sub(r'\s+', ' ', note_data['content']).strip()
        
        # 清理标签
        if 'tags' in note_data:
            note_data['tags'] = [tag.strip() for tag in note_data['tags'] if tag and tag.strip()]
            note_data['tags'] = list(set(note_data['tags']))[:10]  # 去重并限制数量
        
        # 确保图片URL完整
        if 'images' in note_data:
            for img in note_data['images']:
                if 'url' in img and img['url']:
                    if img['url'].startswith('//'):
                        img['url'] = 'https:' + img['url']
                    elif img['url'].startswith('/'):
                        img['url'] = urljoin('https://www.xiaohongshu.com', img['url'])
        
        return note_data
    
    def filter_by_theme(self, note_data: Dict[str, Any], theme: str) -> bool:
        """
        根据主题过滤笔记
        
        Args:
            note_data: 笔记数据
            theme: 主题关键词
            
        Returns:
            是否符合主题
        """
        if not note_data:
            return False
        
        # 提取所有文本
        texts = []
        if note_data.get('title'):
            texts.append(note_data['title'].lower())
        if note_data.get('content'):
            texts.append(note_data['content'].lower())
        
        all_text = ' '.join(texts)
        
        # 主题关键词
        theme_keywords = []
        theme_parts = theme.lower().split('/')
        for part in theme_parts:
            theme_keywords.extend(part.split())
        
        # 添加中文关键词
        theme_keywords.extend(['外卖', '点餐', '翻车', '漫画', '吃啥', '美食', '吐槽'])
        
        # 检查是否包含关键词
        for keyword in theme_keywords:
            if keyword and keyword in all_text:
                return True
        
        # 检查标签
        for tag in note_data.get('tags', []):
            tag_lower = tag.lower()
            for keyword in theme_keywords:
                if keyword and keyword in tag_lower:
                    return True
        
        return False


if __name__ == "__main__":
    # 测试解析器
    parser = XHSParser()
    
    # 测试主题过滤
    test_note = {
        'title': '外卖翻车记',
        'content': '今天点的外卖太难吃了',
        'tags': ['外卖', '翻车', '美食']
    }
    
    is_match = parser.filter_by_theme(test_note, "外卖/点餐翻车")
    print(f"主题匹配结果: {is_match}")