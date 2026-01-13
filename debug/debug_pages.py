#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析保存的调试页面
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from bs4 import BeautifulSoup
import re
import json

def analyze_search_pages():
    """分析搜索页面"""
    debug_dir = Path("debug_pages")
    
    if not debug_dir.exists():
        print("debug_pages目录不存在")
        return
    
    html_files = list(debug_dir.glob("search_*.html"))
    
    print(f"找到 {len(html_files)} 个搜索页面文件")
    
    for html_file in html_files:
        print(f"\n{'='*60}")
        print(f"分析文件: {html_file.name}")
        print(f"{'='*60}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 1. 查找所有包含笔记ID的元素
        print("\n1. 查找笔记ID:")
        
        # 方法1: data-note-id 属性
        elements_with_note_id = soup.find_all(attrs={'data-note-id': True})
        print(f"   data-note-id 属性: {len(elements_with_note_id)} 个")
        
        if elements_with_note_id:
            for i, elem in enumerate(elements_with_note_id[:3]):
                note_id = elem['data-note-id']
                print(f"    {i+1}. note_id: {note_id}")
                print(f"       类名: {elem.get('class', '无')}")
                print(f"       标签: {elem.name}")
        
        # 方法2: 从链接中提取
        explore_links = soup.find_all('a', href=re.compile(r'/explore/'))
        print(f"   /explore/ 链接: {len(explore_links)} 个")
        
        note_ids_from_links = []
        for link in explore_links[:5]:
            href = link['href']
            match = re.search(r'/explore/([a-f0-9]{24})', href)
            if match:
                note_ids_from_links.append(match.group(1))
                print(f"     链接: {href[:80]}...")
        
        # 2. 查找常见的笔记容器
        print("\n2. 常见的容器类名:")
        
        all_divs = soup.find_all('div')
        class_counter = {}
        
        for div in all_divs[:100]:  # 只检查前100个div
            classes = div.get('class', [])
            if classes:
                for cls in classes:
                    class_counter[cls] = class_counter.get(cls, 0) + 1
        
        # 按出现次数排序
        sorted_classes = sorted(class_counter.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for cls, count in sorted_classes:
            print(f"   {cls}: {count} 次")
        
        # 3. 查找包含特定关键词的文本
        print("\n3. 页面中的相关文本:")
        
        all_text = soup.get_text()
        keywords = ['外卖', '点餐', '翻车', '漫画']
        
        lines = all_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                for keyword in keywords:
                    if keyword in line:
                        print(f"   '{keyword}' 在: {line[:80]}...")
                        break
        
        # 4. 保存一些示例元素用于调试
        print("\n4. 保存示例元素:")
        
        example_elements = []
        
        # 收集一些可能的笔记元素
        potential_elements = []
        
        # 查找所有div，寻找可能的笔记
        for div in all_divs[:50]:
            div_str = str(div)
            if len(div_str) > 500 and len(div_str) < 5000:
                # 检查是否包含图片和文本
                has_img = bool(div.find('img'))
                has_text = len(div.get_text(strip=True)) > 20
                
                if has_img and has_text:
                    potential_elements.append(div)
        
        for i, elem in enumerate(potential_elements[:3]):
            example_file = debug_dir / f"example_{html_file.stem}_{i}.html"
            with open(example_file, 'w', encoding='utf-8') as f:
                f.write(str(elem))
            print(f"   保存示例元素到: {example_file.name}")
        
        # 5. 提取所有图片URL
        print("\n5. 图片URL统计:")
        
        img_tags = soup.find_all('img')
        valid_imgs = []
        
        for img in img_tags[:20]:  # 只检查前20个
            src = img.get('src') or img.get('data-src')
            if src and 'http' in src and not any(x in src.lower() for x in ['icon', 'avatar', 'logo']):
                valid_imgs.append(src)
                print(f"   图片: {src[:80]}...")
        
        print(f"   总共找到 {len(img_tags)} 个img标签，其中 {len(valid_imgs)} 个有效图片")

def create_test_parser():
    """创建测试解析器"""
    from src.crawler.parser import XHSParser
    
    parser = XHSParser()
    
    debug_dir = Path("debug_pages")
    html_files = list(debug_dir.glob("search_*.html"))
    
    if not html_files:
        print("没有找到测试文件")
        return
    
    # 使用最新的文件
    latest_file = max(html_files, key=lambda x: x.stat().st_mtime)
    print(f"\n使用文件进行解析测试: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取关键词
    keyword = latest_file.stem.split('_')[1]
    
    print(f"关键词: {keyword}")
    
    # 解析
    notes = parser.parse_search_results_direct(content, keyword)
    
    print(f"解析到 {len(notes)} 个笔记")
    
    if notes:
        print("\n解析结果:")
        for i, note in enumerate(notes[:3]):
            print(f"\n笔记 {i+1}:")
            print(f"  ID: {note.get('note_id', '无')}")
            print(f"  标题: {note.get('title', '无标题')}")
            print(f"  内容长度: {len(note.get('content', ''))}")
            print(f"  标签: {note.get('tags', [])}")
            print(f"  封面URL: {note.get('cover_url', '无')}")
    else:
        print("没有解析到笔记")
        
        # 尝试直接提取笔记ID
        import re
        note_ids = re.findall(r'/explore/([a-f0-9]{24})', content)
        note_ids = list(set(note_ids))
        
        print(f"\n直接正则提取到 {len(note_ids)} 个笔记ID")
        if note_ids:
            print("前5个ID:")
            for note_id in note_ids[:5]:
                print(f"  {note_id}")

if __name__ == "__main__":
    print("调试页面分析工具")
    print("=" * 60)
    
    print("1. 分析搜索页面结构")
    print("2. 测试解析器")
    print("3. 退出")
    
    choice = input("\n请选择操作 (1-3): ").strip()
    
    if choice == "1":
        analyze_search_pages()
    elif choice == "2":
        create_test_parser()
    else:
        print("退出")