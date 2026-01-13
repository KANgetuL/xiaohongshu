"""
请求处理器模块
处理HTTP请求、代理、重试策略等
"""

import time
import random
from typing import Dict, Optional, Tuple, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import (
    CRAWLER_SETTINGS,
    RETRY_SETTINGS,
    PROXY_SETTINGS,
    LOG_CONFIG
)
from config.constants import HEADERS
from src.utils.logger import setup_logger


class RequestHandler:
    """HTTP请求处理器"""
    
    def __init__(self, use_proxy: bool = None):
        """
        初始化请求处理器
        
        Args:
            use_proxy: 是否使用代理，如果为None则使用配置中的设置
        """
        self.logger = setup_logger("request_handler")
        self.session = requests.Session()
        
        # 配置重试策略
        self.max_retries = RETRY_SETTINGS["max_retries"]
        self.retry_delay = RETRY_SETTINGS["retry_delay"]
        self.retry_codes = RETRY_SETTINGS["retry_codes"]
        
        # 配置代理
        self.use_proxy = use_proxy if use_proxy is not None else PROXY_SETTINGS["enabled"]
        self.proxies = PROXY_SETTINGS["proxy_list"]
        self.current_proxy_index = 0
        
        # 配置请求参数
        self.request_delay = CRAWLER_SETTINGS["request_delay"]
        self.timeout = CRAWLER_SETTINGS["timeout"]
        
        # 设置请求头
        self.headers = HEADERS.copy()
        
        # 配置session
        self._setup_session()
    
    def _setup_session(self):
        """配置session的重试策略"""
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=self.retry_codes,
            allowed_methods=["GET", "POST"],
            backoff_factor=self.retry_delay
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """
        获取代理设置
        
        Returns:
            代理字典，如果没有代理则返回None
        """
        if not self.use_proxy or not self.proxies:
            return None
        
        if not self.proxies:
            return None
        
        # 如果轮换代理，选择下一个代理
        proxy = self.proxies[self.current_proxy_index]
        
        if PROXY_SETTINGS["rotate_proxy"]:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        self.logger.debug(f"使用代理: {proxy}")
        return {"http": proxy, "https": proxy}
    
    def _add_random_delay(self):
        """添加随机延迟，避免请求过快"""
        delay = self.request_delay + random.uniform(-0.5, 0.5)
        time.sleep(max(0.5, delay))
    
    def make_request(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> Tuple[bool, Optional[requests.Response], str]:
        """
        发送HTTP请求
        
        Args:
            url: 请求URL
            method: HTTP方法
            params: 查询参数
            data: 表单数据
            json_data: JSON数据
            headers: 请求头
            timeout: 超时时间
            
        Returns:
            (是否成功, 响应对象, 错误信息)
        """
        # 添加随机延迟
        self._add_random_delay()
        
        # 准备请求参数
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        request_timeout = timeout or self.timeout
        proxies = self._get_proxy()
        
        try:
            self.logger.info(f"发送{method}请求到: {url}")
            
            if method.upper() == "GET":
                response = self.session.get(
                    url,
                    params=params,
                    headers=request_headers,
                    timeout=request_timeout,
                    proxies=proxies
                )
            elif method.upper() == "POST":
                response = self.session.post(
                    url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=request_headers,
                    timeout=request_timeout,
                    proxies=proxies
                )
            else:
                return False, None, f"不支持的HTTP方法: {method}"
            
            # 检查响应状态
            if response.status_code == 200:
                self.logger.debug(f"请求成功: {url}")
                return True, response, "请求成功"
            else:
                error_msg = f"请求失败，状态码: {response.status_code}"
                self.logger.warning(f"{error_msg}: {url}")
                return False, response, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"请求超时: {url}"
            self.logger.error(error_msg)
            return False, None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = f"连接错误: {url}"
            self.logger.error(error_msg)
            return False, None, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"请求异常: {str(e)}"
            self.logger.error(f"{error_msg}: {url}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            self.logger.error(f"{error_msg}: {url}")
            return False, None, error_msg
    
    def download_image(self, url: str, save_path: str) -> Tuple[bool, str]:
        """
        下载图片
        
        Args:
            url: 图片URL
            save_path: 保存路径
            
        Returns:
            (是否成功, 错误信息)
        """
        self.logger.info(f"下载图片: {url}")
        
        success, response, error_msg = self.make_request(url)
        
        if not success or not response:
            return False, error_msg
        
        try:
            # 保存图片
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"图片保存成功: {save_path}")
            return True, "下载成功"
            
        except IOError as e:
            error_msg = f"保存图片失败: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"下载图片失败: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def close(self):
        """关闭session"""
        self.session.close()
        self.logger.info("请求处理器已关闭")


if __name__ == "__main__":
    # 测试请求处理器
    handler = RequestHandler(use_proxy=False)
    
    # 测试请求百度
    success, response, message = handler.make_request("https://www.baidu.com")
    print(f"请求测试: {success}, 状态码: {response.status_code if response else '无响应'}")
    
    handler.close()