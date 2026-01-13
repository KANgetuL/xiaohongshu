# 创建 quality_check.py
import json
from pathlib import Path
from PIL import Image

def check_data_quality():
    """检查收集的数据质量"""
    data_dir = Path("data/processed/comics")
    
    if not data_dir.exists():
        print("数据目录不存在")
        return
    
    comic_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    print(f"找到 {len(comic_dirs)} 个连环画")
    
    for comic_dir in comic_dirs:
        print(f"\n检查连环画: {comic_dir.name}")
        
        # 检查meta.json
        meta_file = comic_dir / "meta.json"
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            print(f"  标题: {meta.get('title', '无标题')}")
            print(f"  图片数: {meta.get('downloaded_image_count', 0)}")
            print(f"  标签: {', '.join(meta.get('tags', []))}")
        
        # 检查图片
        images_dir = comic_dir / "images"
        if images_dir.exists():
            images = list(images_dir.glob("*.jpg"))
            print(f"  实际图片文件: {len(images)}个")
            
            # 检查图片分辨率
            for img_path in images[:3]:  # 只检查前3张
                try:
                    with Image.open(img_path) as img:
                        width, height = img.size
                        if width >= 500 and height >= 500:
                            print(f"    ✓ {img_path.name}: {width}x{height}")
                        else:
                            print(f"    ✗ {img_path.name}: {width}x{height} (分辨率不足)")
                except Exception as e:
                    print(f"    ✗ {img_path.name}: 无法打开 ({e})")
        
        # 检查标注文件
        ann_file = comic_dir / "annotations.json"
        if ann_file.exists():
            with open(ann_file, 'r', encoding='utf-8') as f:
                ann = json.load(f)
            print(f"  标注数量: {len(ann)}个")

if __name__ == "__main__":
    check_data_quality()