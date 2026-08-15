"""
AI分析质量评分模块

对大模型返回的分析结果进行自动质量评分（0-100分），
用于监控AI输出质量并为后续优化提供数据支撑。

评分维度：
- 格式合规性（30%）：JSON可解析、含必要字段
- 内容充实度（30%）：analysis_text长度
- 建议质量（20%）：suggestions数量与结构完整性
- 专业性（20%）：领域关键词覆盖度
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# 专业性评估关键词列表
PROFESSIONAL_KEYWORDS = [
    "温度", "湿度", "冰箱", "试剂", "样本", "设备",
    "报警", "失控", "维护", "校准", "监控", "风险"
]


class AIQualityScorer:
    """AI分析输出质量自动评分器"""

    def score(self, ai_result: Dict, raw_response: str = "") -> Dict:
        """
        对AI分析结果进行质量评分

        Args:
            ai_result: 解析后的AI结果字典（含analysis_text/ai_suggestions等）
            raw_response: 原始响应文本（用于格式合规性判断）

        Returns:
            {"total_score": 85, "details": {"format": 30, "content": 25, "suggestions": 15, "professional": 15}}
        """
        format_score = self._score_format(ai_result)
        content_score = self._score_content(ai_result)
        suggestions_score = self._score_suggestions(ai_result)
        professional_score = self._score_professional(ai_result)

        total = format_score + content_score + suggestions_score + professional_score

        result = {
            "total_score": min(total, 100),
            "details": {
                "format": format_score,
                "content": content_score,
                "suggestions": suggestions_score,
                "professional": professional_score
            }
        }

        logger.info(f"AI质量评分: {result['total_score']}/100 "
                    f"(格式={format_score}, 内容={content_score}, "
                    f"建议={suggestions_score}, 专业={professional_score})")
        return result

    @staticmethod
    def _score_format(ai_result: Dict) -> int:
        """格式合规性评分（满分30分）"""
        score = 0

        # 能作为字典存在，说明JSON可解析
        if isinstance(ai_result, dict):
            score += 10

        # 含 analysis_text 字段
        if ai_result.get("analysis_text"):
            score += 10

        # 含 ai_suggestions 字段
        if "ai_suggestions" in ai_result:
            score += 10

        return min(score, 30)

    @staticmethod
    def _score_content(ai_result: Dict) -> int:
        """内容充实度评分（满分30分）"""
        text = ai_result.get("analysis_text", "")
        length = len(text)

        if length >= 500:
            return 30
        elif length >= 100:
            return 20
        elif length > 0:
            return 10
        return 0

    @staticmethod
    def _score_suggestions(ai_result: Dict) -> int:
        """建议质量评分（满分20分）"""
        suggestions = ai_result.get("ai_suggestions", [])
        score = 0

        # 数量评分
        count = len(suggestions)
        if count >= 3:
            score += 15
        elif count >= 1:
            score += 8

        # 结构完整性（含priority字段）
        if suggestions and all(isinstance(s, dict) and "priority" in s for s in suggestions):
            score += 5

        return min(score, 20)

    @staticmethod
    def _score_professional(ai_result: Dict) -> int:
        """专业性评分（满分20分）"""
        text = ai_result.get("analysis_text", "")

        # 统计关键词命中数
        hit_count = sum(1 for kw in PROFESSIONAL_KEYWORDS if kw in text)

        # 每命中一个+3分，上限20分
        return min(hit_count * 3, 20)
