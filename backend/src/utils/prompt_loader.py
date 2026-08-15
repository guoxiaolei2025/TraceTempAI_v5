import os
import logging

logger = logging.getLogger(__name__)

class PromptLoader:
    """
    提示词模板加载器
    
    功能：从文件中加载不同科室的提示词模板，支持统一的内容和版本管理
    """
    
    def __init__(self, prompts_dir="prompts"):
        """
        初始化提示词加载器
        
        Args:
            prompts_dir: 提示词模板文件目录
        """
        self.prompts_dir = prompts_dir
    
    def load_prompt(self, department):
        """
        加载指定科室的提示词模板
        
        Args:
            department: 科室名称
            
        Returns:
            str: 提示词模板内容
        """
        # 使用统一的标准提示词模板
        prompt_file = os.path.join(self.prompts_dir, "standard_prompt.txt")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            # 如果文件读取失败，返回默认提示词
            logger.warning(f"提示词模板读取失败: {e}")
            return self._get_default_prompt(department)
    
    def _get_default_prompt(self, department):
        """
        获取默认提示词模板
        
        Args:
            department: 科室名称
            
        Returns:
            str: 默认提示词模板
        """
        return "请分析以下设备报警数据，按时间段和设备生成汇总描述。\n\n输入数据："
