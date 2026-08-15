import json
import logging
import os
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Department:
    id: str
    name: str
    api_key: str
    rules: Dict
    report_templates: Dict

class DepartmentManager:
    def __init__(self, config_path: str = None):
        import os
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'departments.json')
        
        self.config_path = config_path
        self.departments: Dict[str, Department] = {}
        self.load_config()
    
    def _get_api_key_from_env(self, env_var_name: str) -> str:
        """
        从环境变量获取 API Key
        
        Args:
            env_var_name: 环境变量名称
        
        Returns:
            str: API Key 值，如果未设置则返回空字符串
        """
        api_key = os.getenv(env_var_name, '')
        if not api_key:
            logger.warning(f"环境变量 {env_var_name} 未设置")
        return api_key
    
    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            for dept_config in config.get('departments', []):
                # 从环境变量获取 API Key
                api_key_env_var = dept_config.get('api_key_env', '')
                api_key = self._get_api_key_from_env(api_key_env_var)
                
                dept = Department(
                    id=dept_config['id'],
                    name=dept_config['name'],
                    api_key=api_key,
                    rules=dept_config.get('rules', {}),
                    report_templates=dept_config.get('report_templates', {})
                )
                self.departments[dept.id] = dept
                
        except FileNotFoundError:
            logger.warning(f"学科配置文件不存在: {self.config_path}，将使用默认配置")
            self._load_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"学科配置文件格式错误: {e}，将使用默认配置")
            self._load_default_config()
        except Exception as e:
            logger.error(f"加载学科配置失败: {e}，将使用默认配置")
            self._load_default_config()
    
    def _load_default_config(self):
        default_departments = [
            {
                'id': 'infection',
                'name': '感染中心常规PCR室',
                'api_key_env': 'DEPARTMENT_INFECTION_API_KEY',
                'rules': {
                    'uncontrol_threshold_minutes': 30,
                    'allow_time_merge': True,
                    'merge_gap_hours': 2,
                    'importance_order': ['temperature', 'humidity']
                },
                'report_templates': {
                    'monthly': 'templates/monthly_review_infection.docx',
                    'correction': 'templates/correction_report_infection.docx'
                }
            },
            {
                'id': 'flowcytometry',
                'name': '血液流式中心流式室',
                'api_key_env': 'DEPARTMENT_FLOWCYTOMETRY_API_KEY',
                'rules': {
                    'uncontrol_threshold_minutes': 30,
                    'allow_time_merge': False,
                    'importance_order': ['temperature', 'humidity']
                },
                'report_templates': {
                    'monthly': 'templates/monthly_review_flowcytometry.docx',
                    'correction': 'templates/correction_report_flowcytometry.docx'
                }
            }
        ]
        
        for dept_config in default_departments:
            api_key_env_var = dept_config.get('api_key_env', '')
            api_key = self._get_api_key_from_env(api_key_env_var)
            
            dept = Department(
                id=dept_config['id'],
                name=dept_config['name'],
                api_key=api_key,
                rules=dept_config.get('rules', {}),
                report_templates=dept_config.get('report_templates', {})
            )
            self.departments[dept.id] = dept
    
    def get_department(self, dept_id: str) -> Optional[Department]:
        return self.departments.get(dept_id)
    
    def get_department_by_name(self, dept_name: str) -> Optional[Department]:
        for dept in self.departments.values():
            if dept.name == dept_name:
                return dept
        return None
    
    def get_all_departments(self) -> List[Department]:
        return list(self.departments.values())
    
    def get_department_names(self) -> List[str]:
        return [dept.name for dept in self.departments.values()]
    
    def get_department_ids(self) -> List[str]:
        return list(self.departments.keys())
    
    def add_department(self, department: Department) -> bool:
        if department.id in self.departments:
            logger.warning(f"学科ID {department.id} 已存在，将覆盖原有配置")
        
        self.departments[department.id] = department
        return self.save_config()
    
    def remove_department(self, dept_id: str) -> bool:
        if dept_id not in self.departments:
            logger.warning(f"学科ID {dept_id} 不存在")
            return False
        
        del self.departments[dept_id]
        return self.save_config()
    
    def update_department(self, dept_id: str, **kwargs) -> bool:
        if dept_id not in self.departments:
            logger.warning(f"学科ID {dept_id} 不存在")
            return False
        
        dept = self.departments[dept_id]
        
        for key, value in kwargs.items():
            if hasattr(dept, key):
                setattr(dept, key, value)
        
        return self.save_config()
    
    def save_config(self) -> bool:
        try:
            config = {
                'departments': [
                    {
                        'id': dept.id,
                        'name': dept.name,
                        'api_key_env': self._get_env_var_name(dept.id),
                        'rules': dept.rules,
                        'report_templates': dept.report_templates
                    }
                    for dept in self.departments.values()
                ]
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"保存学科配置失败: {e}")
            return False
    
    def _get_env_var_name(self, dept_id: str) -> str:
        """
        根据学科ID生成环境变量名称
        
        Args:
            dept_id: 学科ID
        
        Returns:
            str: 环境变量名称
        """
        # 使用标准化的环境变量命名规则
        normalized_id = dept_id.replace('广州金域', 'GZJY_').replace(' ', '_').replace('-', '_').upper()
        return f"DEPARTMENT_{normalized_id}_API_KEY"
    
    def reload_config(self):
        self.load_config()
    
    def get_department_rules(self, dept_id: str) -> Optional[Dict]:
        dept = self.get_department(dept_id)
        if dept:
            return dept.rules
        return None
    
    def get_department_templates(self, dept_id: str) -> Optional[Dict]:
        dept = self.get_department(dept_id)
        if dept:
            return dept.report_templates
        return None
    
    def get_department_api_key(self, dept_id: str) -> Optional[str]:
        dept = self.get_department(dept_id)
        if dept:
            return dept.api_key
        return None
    
    def validate_departments(self) -> Dict[str, List[str]]:
        validation_results = {}
        
        for dept_id, dept in self.departments.items():
            errors = []
            
            if not dept.name:
                errors.append("学科名称不能为空")
            
            if 'uncontrol_threshold_minutes' not in dept.rules:
                errors.append("缺少失控阈值配置")
            if 'importance_order' not in dept.rules:
                errors.append("缺少重要性顺序配置")
            
            validation_results[dept_id] = errors
        
        return validation_results