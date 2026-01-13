#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装ChromeDriver工具
"""

import os
import sys
import zipfile
import requests
import subprocess

def get_chrome_version():
    """获取Chrome浏览器版本"""
    try:
        # Windows系统获取Chrome版本
        import winreg
        try:
            # Chrome稳定版
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Google\Chrome\BLBeacon")
            version = winreg.QueryValueEx(key, "version")[0]
            winreg.CloseKey(key)
            return version
        except:
            # 尝试其他注册表位置
            pass
            
        # 通过命令行获取
        import subprocess
        result = subprocess.run(
            ['reg', 'query', 
             'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', 
             '/v', 'version'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'version' in line.lower():
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        return parts[-1]
                        
        print("⚠️ 无法自动获取Chrome版本")
        return None
        
    except Exception as e:
        print(f"获取Chrome版本时出错: {e}")
        return None

def download_chromedriver(version=None):
    """下载ChromeDriver"""
    if not version:
        version = input("请输入Chrome版本号（例如：120.0.6099.130）: ").strip()
    
    if not version:
        print("❌ 需要提供版本号")
        return False
    
    # 提取主版本号
    major_version = version.split('.')[0]
    
    # 构建下载URL
    base_url = "https://chromedriver.storage.googleapis.com"
    
    # 尝试不同格式的版本号
    version_formats = [
        version,  # 完整版本
        major_version,  # 主版本
        f"{major_version}.0.0.0"  # 主版本.0.0.0
    ]
    
    for v in version_formats:
        url = f"{base_url}/{v}/chromedriver_win32.zip"
        print(f"尝试下载: {url}")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                print(f"✅ 找到对应版本: {v}")
                
                # 下载文件
                zip_path = "chromedriver_win32.zip"
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✅ 下载完成: {zip_path}")
                
                # 解压文件
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(".")
                
                print("✅ 解压完成")
                
                # 清理
                os.remove(zip_path)
                print("✅ 清理临时文件")
                
                return True
                
        except Exception as e:
            print(f"下载失败: {e}")
    
    print("❌ 无法找到匹配的ChromeDriver版本")
    return False

def main():
    print("ChromeDriver安装工具")
    print("=" * 60)
    
    print("1. 自动检测Chrome版本并下载")
    print("2. 手动指定版本下载")
    print("3. 退出")
    
    choice = input("\n请选择操作 (1-3): ").strip()
    
    if choice == "1":
        version = get_chrome_version()
        if version:
            print(f"✅ 检测到Chrome版本: {version}")
            download_chromedriver(version)
        else:
            print("❌ 无法自动检测Chrome版本")
            version = input("请输入Chrome版本号: ").strip()
            if version:
                download_chromedriver(version)
    
    elif choice == "2":
        version = input("请输入Chrome版本号: ").strip()
        if version:
            download_chromedriver(version)
    
    print("\n📋 安装完成后:")
    print("1. chromedriver.exe 应该位于项目根目录")
    print("2. 重新运行测试脚本")

if __name__ == "__main__":
    main()