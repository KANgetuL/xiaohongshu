"""
小红书连环画爬取项目主入口文件（简化版）
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from config.settings import create_directories
from src.utils.logger import setup_logger
from src.crawler.xhs_crawler import SimpleXHSCrawler
from src.processor.data_filter import DataFilter


def check_dependencies():
    """检查依赖是否安装"""
    try:
        from selenium import webdriver
        print("✓ Selenium 已安装")
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("✓ webdriver-manager 已安装")
        except ImportError:
            print("✗ webdriver-manager 未安装，请运行: pip install webdriver-manager")
            return False
            
        return True
    except ImportError:
        print("✗ Selenium 未安装，请运行: pip install selenium")
        return False


def run_simple_crawler(max_comics: int = 3, headless: bool = False):
    """
    运行简化版爬虫
    
    Args:
        max_comics: 最大收集数量
        headless: 是否无头模式（False显示浏览器界面，方便调试）
    """
    logger = setup_logger()
    logger.info("开始执行简化版爬虫任务")
    
    try:
        # 创建爬虫实例
        crawler = SimpleXHSCrawler(max_comics=max_comics, headless=headless)
        
        # 执行爬取
        report = crawler.crawl()
        
        # 保存报告
        crawler.save_report(report)
        
        # 关闭爬虫
        crawler.close()
        
        logger.info(f"爬虫任务完成，收集到 {report['stats']['total_collected']} 个连环画")
        
        return report
        
    except Exception as e:
        logger.error(f"爬虫任务失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print("小红书连环画爬取项目 (简化版)")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装必要的依赖包。")
        print("运行以下命令安装:")
        print("pip install selenium webdriver-manager")
        return
    
    # 创建目录结构
    print("\n创建项目目录...")
    create_directories()
    
    # 初始化日志
    print("初始化日志系统...")
    logger = setup_logger()
    logger.info("项目初始化完成")
    
    # 显示配置信息
    from config.settings import (
        CRAWLER_SETTINGS,
        FILTER_RULES,
        TAGS
    )
    
    print("\n项目配置:")
    print(f"目标主题: {CRAWLER_SETTINGS['target_theme']}")
    print(f"搜索关键词: {', '.join(CRAWLER_SETTINGS['search_keywords'])}")
    print(f"图像要求: 至少{FILTER_RULES['min_image_width']}x{FILTER_RULES['min_image_height']}")
    print(f"文本要求: 至少{FILTER_RULES['min_text_length']}个中文字符")
    print(f"主要标签: {', '.join(TAGS['primary_tags'])}")
    
    print("\n注意:")
    print("1. 首次运行会自动下载浏览器驱动")
    print("2. 建议使用非无头模式（显示浏览器界面）进行调试")
    print("3. 小红书可能有登录弹窗，代码会尝试自动处理")
    
    print("\n请选择操作:")
    print("1. 运行爬虫（显示浏览器界面，便于调试）")
    print("2. 运行爬虫（无头模式，不显示界面）")
    print("3. 查看项目状态")
    print("4. 退出")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice in ["1", "2"]:
        print("\n运行简化版爬虫...")
        
        max_comics = input("请输入最大收集数量 (默认3，测试用): ").strip()
        max_comics = int(max_comics) if max_comics.isdigit() else 3
        
        headless = (choice == "2")  # 选项1显示界面，选项2无头模式
        
        if not headless:
            print("\n注意: 浏览器界面将会显示，请勿操作浏览器窗口")
            print("如果有登录弹窗，程序会尝试自动关闭")
            print("如果页面卡住，可以手动关闭浏览器窗口")
        
        report = run_simple_crawler(max_comics=max_comics, headless=headless)
        
        if report:
            print(f"\n爬取完成!")
            print(f"收集到 {report['stats']['total_collected']} 个连环画")
            print(f"成功率: {report['summary']['success_rate']}%")
            
            if report['collected_comics']:
                print("\n收集的连环画:")
                for comic in report['collected_comics']:
                    print(f"  - {comic['title']} ({comic['images_count']}张图片)")
            else:
                print("\n未收集到任何连环画，可能的原因:")
                print("1. 小红书页面结构变化")
                print("2. 登录弹窗未能自动关闭")
                print("3. 搜索结果不符合要求")
                print("4. 网络连接问题")
        else:
            print("爬取失败，请查看日志文件")
    
    elif choice == "3":
        print("\n项目状态:")
        from config.settings import COMICS_DIR
        from src.utils.helper import safe_json_load
        
        # 检查数据目录
        if COMICS_DIR.exists():
            comic_dirs = [d for d in COMICS_DIR.iterdir() if d.is_dir()]
            print(f"已收集连环画: {len(comic_dirs)}个")
            
            # 检查报告文件
            report_file = COMICS_DIR / "crawl_report.json"
            if report_file.exists():
                report = safe_json_load(report_file)
                if report:
                    print(f"最近爬取时间: {report['stats'].get('end_time', '未知')}")
                    print(f"总收集数: {report['stats'].get('total_collected', 0)}")
                    
                    if report['collected_comics']:
                        print("\n最近收集的连环画:")
                        for comic in report['collected_comics'][:3]:
                            print(f"  - {comic['title']}")
        else:
            print("数据目录为空")
    
    elif choice == "4":
        print("退出程序")
        return
    
    else:
        print("无效选择")


if __name__ == "__main__":
    main()