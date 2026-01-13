#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析器调试工具
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.crawler.parser import XHSParser

def debug_parser():
    """调试解析器"""
    print("解析器调试工具")
    print("=" * 60)
    
    # 读取保存的页面文件
    parser = XHSParser()
    
    # 测试不同关键词的页面
    test_files = [
        "debug_pages/search_外卖翻车_*.html",
        "debug_pages/search_点餐翻车_*.html"
    ]
    
    for pattern in test_files:
        import glob
        files = glob.glob(str(pattern))
        if files:
            latest_file = max(files, key=Path)
            print(f"\n解析文件: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                page_source = f.read()
            
            # 提取关键词
            keyword = Path(latest_file).stem.split('_')[1]
            
            # 解析
            notes = parser.parse_search_results_direct(page_source, keyword)
            
            print(f"找到 {len(notes)} 个笔记")
            
            if notes:
                print("\n前3个笔记:")
                for i, note in enumerate(notes[:3]):
                    print(f"  {i+1}. ID: {note.get('note_id', '无ID')}")
                    print(f"     标题: {note.get('title', '无标题')[:50]}...")
                    print(f"     内容长度: {len(note.get('content', ''))} 字符")
                    print()

def analyze_html_structure():
    """分析HTML结构"""
    print("\nHTML结构分析")
    print("=" * 60)
    
    import glob
    files = glob.glob("debug_pages/search_*.html")
    
    if not files:
        print("未找到调试页面文件")
        return
    
    latest_file = max(files, key=Path)
    print(f"分析文件: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计各种标签
    from collections import Counter
    import re
    
    # 查找所有div的类名
    div_classes = re.findall(r'<div[^>]*class="([^"]*)"', content)
    
    print("\n最常见的div类名:")
    counter = Counter(div_classes)
    for cls, count in counter.most_common(20):
        print(f"  {cls}: {count}")
    
    # 查找包含note的类名
    print("\n包含'note'的类名:")
    for cls in div_classes:
        if 'note' in cls.lower():
            print(f"  {cls}")
    
    # 查找包含explore的链接
    explore_links = re.findall(r'href="([^"]*explore[^"]*)"', content)
    print(f"\n找到 {len(explore_links)} 个explore链接")
    
    # 提取note_id
    note_ids = re.findall(r'/explore/([a-f0-9]{24})', content)
    note_ids = list(set(note_ids))
    print(f"提取到 {len(note_ids)} 个唯一note_id")
    
    if note_ids:
        print("前5个note_id:")
        for note_id in note_ids[:5]:
            print(f"  {note_id}")

if __name__ == "__main__":
    debug_parser()
    analyze_html_structure()