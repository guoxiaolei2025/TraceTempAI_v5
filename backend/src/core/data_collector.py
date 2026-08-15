import requests
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
import time
from core.config import Config

logger = logging.getLogger(__name__)

class DataCollector:
    """
    数据采集器
    
    负责从阿里云369平台API采集设备数据和报警历史数据
    包含错误处理和重试机制
    """
    
    def __init__(self, api_key: str, base_url: str = "https://cloudapi.369clouds.com/openapi"):
        """
        初始化数据采集器
        
        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.max_retries = 3
        self.retry_delay = 2
    
    def get_all_devices(self) -> List[Dict]:
        """
        获取所有设备列表
        
        Returns:
            List[Dict]: 设备列表，每个设备包含设备信息和序列号
        
        Raises:
            requests.RequestException: 当API请求失败时抛出异常
        """
        device_api_url = f"{self.base_url}/devices"
        params = {'key': self.api_key}
        
        # 首先获取第一页数据，确定总页数
        all_devices = []
        try:
            response = self._make_request('GET', device_api_url, params=params)
            api_response = response.json()
            
            # 获取总页数
            all_page = self._get_total_pages(api_response)
            
            # 将第一页数据加入结果
            if 'data' in api_response and 'items' in api_response['data']:
                all_devices.extend(api_response['data']['items'])
            
            # 遍历剩余页
            for page in range(2, all_page + 1):
                params['pageNo'] = page
                response = self._make_request('GET', device_api_url, params=params)
                api_response = response.json()
                
                if 'data' in api_response and 'items' in api_response['data']:
                    all_devices.extend(api_response['data']['items'])
            
            return all_devices
            
        except Exception as e:
            logger.error(f"获取设备列表失败: {e}")
            raise
    
    def get_device_alarms(self, device_sn: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        获取指定设备的报警历史数据
        
        Args:
            device_sn: 设备序列号
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            List[Dict]: 报警记录列表
        
        Raises:
            requests.RequestException: 当API请求失败时抛出异常
        """
        alarm_api_url = f"{self.base_url}/trigger/history"
        params = {
            'key': self.api_key,
            'sn': device_sn,
            'start': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end': end_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            response = self._make_request('GET', alarm_api_url, params=params)
            api_response = response.json()
            
            if 'data' in api_response and 'items' in api_response['data']:
                return api_response['data']['items']
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取设备 {device_sn} 的报警数据失败: {e}")
            raise
    
    def get_all_alarms(self, start_date: datetime, end_date: datetime, progress_callback=None) -> Dict[str, List[Dict]]:
        """
        获取所有设备的报警历史数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            progress_callback: 进度回调函数，参数为(当前进度, 总进度)
        
        Returns:
            Dict[str, List[Dict]]: 设备名称到报警记录列表的映射
        """
        # 获取所有设备
        devices = self.get_all_devices()
        all_alarms = {}
        
        total_devices = len(devices)
        
        for i, device in enumerate(devices):
            device_sn = device.get('sn', '')
            device_name_raw = device.get('name', device_sn)
            # 添加设备编号到设备名称中，格式：设备名称【设备编号】
            device_name = f"{device_name_raw}【{device_sn}】" if device_sn else device_name_raw
            
            try:
                # 获取设备的报警数据
                alarms = self.get_device_alarms(device_sn, start_date, end_date)
                
                # 转换报警数据格式
                formatted_alarms = self._format_alarms(alarms)
                
                if formatted_alarms:
                    all_alarms[device_name] = formatted_alarms
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(i + 1, total_devices)
                    
            except Exception as e:
                logger.warning(f"获取设备 {device_name} 的报警数据失败: {e}")
                continue
        
        return all_alarms
    
    def _format_alarms(self, alarms: List[Dict]) -> List[Dict]:
        """
        格式化报警数据
        
        Args:
            alarms: 原始报警数据列表
        
        Returns:
            List[Dict]: 格式化后的报警数据列表
        """
        handle_mapper = {1: "未处理", 2: "已处理"}
        
        formatted_alarms = []
        for alarm in alarms:
            # 解析datetime对象
            alarm_date = self._parse_datetime(alarm.get('alarmdate', ''))
            
            # 确保alarm_date是datetime对象或None
            if alarm_date and isinstance(alarm_date, datetime):
                alarmdate_str = alarm_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                alarmdate_str = str(alarm.get('alarmdate', '')) if alarm.get('alarmdate') else ''
            
            formatted_alarm = {
                'alarmdate': alarmdate_str,
                'message': alarm.get('message', ''),
                'handlestate': handle_mapper.get(alarm.get('handlestate', 1), '未知'),
                'handleremark': alarm.get('handleremark', ''),
                'remark': alarm.get('remark', ''),
                'alarmtrigger': alarm.get('alarmtrigger', '')
            }
            formatted_alarms.append(formatted_alarm)
        
        return formatted_alarms
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """
        解析日期时间字符串为datetime对象
        
        Args:
            date_str: 日期时间字符串
        
        Returns:
            datetime: datetime对象
        """
        # 尝试ISO 8601格式
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            # 尝试其他格式
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        
        # 如果都失败，返回None（调用方会使用原始字符串）
        logger.warning(f"无法解析日期时间: {date_str}")
        return None
    
    def _get_total_pages(self, api_response: Dict) -> int:
        """
        从API响应中获取总页数
        
        Args:
            api_response: API响应字典
        
        Returns:
            int: 总页数
        """
        if 'data' in api_response and 'totalPages' in api_response['data']:
            return api_response['data']['totalPages']
        elif 'data' in api_response and 'totalCount' in api_response['data'] and 'pageSize' in api_response['data']:
            # 根据totalCount和pageSize计算总页数
            total_records = api_response['data']['totalCount']
            page_size = api_response['data']['pageSize']
            return (total_records + page_size - 1) // page_size
        elif 'data' in api_response and 'total' in api_response['data']:
            # 如果只有总记录数，假设每页10条记录计算总页数
            total_records = api_response['data']['total']
            return (total_records + 9) // 10
        else:
            # 如果都没有，尝试获取第一页数据
            return 1
    
    def _build_proxies(self) -> Optional[Dict]:
        """
        根据配置构建 requests 代理参数
        
        Returns:
            Dict/None: 代理字典；None 表示让 requests 使用系统默认
        """
        proxy_url = Config.PROXY_URL
        if proxy_url.lower() == 'none':
            # 显式禁用代理（覆盖系统环境变量中的代理设置）
            return {'http': None, 'https': None}
        if proxy_url:
            proxies = {'http': proxy_url, 'https': proxy_url}
            no_proxy = Config.NO_PROXY
            if no_proxy:
                # requests 会自动读取 NO_PROXY 环境变量
                # 但为了保险，也设置到 os.environ
                original_no_proxy = os.environ.get('NO_PROXY', '')
                os.environ['NO_PROXY'] = no_proxy
            return proxies
        # 未配置 PROXY_URL：检查系统代理环境变量是否指向死掉的 localhost 代理
        # （常见于 VPN 客户端关闭后残留的 HTTP_PROXY/HTTPS_PROXY）
        for env_var in ('HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy'):
            val = os.environ.get(env_var, '')
            if val and ('127.0.0.1' in val or 'localhost' in val):
                logger.warning(
                    "检测到系统代理 %s=%s 指向本地地址，但该代理似乎未运行。"
                    "临时禁用代理以继续请求。如需使用代理，请在 .env 中设置 PROXY_URL。",
                    env_var, val
                )
                return {'http': None, 'https': None}
        # 未配置且没有检测到死掉的本地代理，则使用系统默认
        return None
    
    def _make_request(self, method: str, url: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> requests.Response:
        """
        发送HTTP请求，包含重试机制和代理支持
        
        Args:
            method: HTTP方法（GET/POST等）
            url: 请求URL
            params: 查询参数
            json_data: JSON请求体
        
        Returns:
            requests.Response: 响应对象
        
        Raises:
            requests.RequestException: 当所有重试都失败时抛出异常
        """
        last_exception = None
        proxies = self._build_proxies()
        
        for attempt in range(self.max_retries):
            try:
                request_kwargs = {'params': params, 'timeout': 30}
                if proxies is not None:
                    request_kwargs['proxies'] = proxies
                
                if method.upper() == 'GET':
                    response = requests.get(url, **request_kwargs)
                elif method.upper() == 'POST':
                    request_kwargs['json'] = json_data
                    response = requests.post(url, **request_kwargs)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                # 检查响应状态码
                response.raise_for_status()
                
                return response
                
            except requests.exceptions.ProxyError as e:
                last_exception = e
                logger.error("代理连接失败: %s", e)
                # 代理错误不重试，直接抛出并提供解决方案
                raise requests.exceptions.ProxyError(
                    f"无法连接到代理服务器。"
                    f"请在 .env 文件中设置 PROXY_URL=none 以禁用代理，"
                    f"或检查系统代理环境变量 HTTP_PROXY/HTTPS_PROXY。"
                ) from e
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"请求失败（尝试 {attempt + 1}/{self.max_retries}）: {e}")
                
                # 如果不是最后一次尝试，等待一段时间后重试
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        # 所有重试都失败，抛出异常
        raise last_exception
    
    def get_device_count(self) -> int:
        """
        获取设备总数
        
        Returns:
            int: 设备总数
        """
        try:
            devices = self.get_all_devices()
            return len(devices)
        except Exception as e:
            logger.error(f"获取设备总数失败: {e}")
            return 0
    
    def get_alarm_count(self, start_date: datetime, end_date: datetime) -> int:
        """
        获取指定时间范围内的报警总数
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            int: 报警总数
        """
        try:
            all_alarms = self.get_all_alarms(start_date, end_date)
            total_alarms = sum(len(alarms) for alarms in all_alarms.values())
            return total_alarms
        except Exception as e:
            logger.error(f"获取报警总数失败: {e}")
            return 0