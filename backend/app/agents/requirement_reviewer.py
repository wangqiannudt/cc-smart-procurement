import re
from typing import List, Dict, Any
import jieba

class RequirementReviewer:
    """需求规范审查智能体"""

    def __init__(self):
        # 初始化jieba分词
        jieba.initialize()

        # 必备要素关键词
        self.required_elements = {
            "用途": ["用途", "应用场景", "使用场景", "应用于", "用于"],
            "功能边界": ["功能", "功能模块", "功能描述", "功能要求", "功能说明"],
            "关键性能指标": ["性能", "指标", "参数", "响应时间", "处理能力", "吞吐量"]
        }

        # 表述规范性检查规则
        self.expression_rules = {
            "模糊表述": ["大约", "大概", "左右", "尽可能", "尽量", "尽可能好"],
            "绝对化表述": ["必须", "绝对", "一定", "确保", "保证"],
            "缺失量化指标": ["需要", "应该", "最好", "能够"]
        }

        # 常见问题规则
        self.common_issues = [
            {
                "category": "完整性",
                "check": self._check_completeness,
                "description": "检查需求文档的完整性"
            },
            {
                "category": "清晰度",
                "check": self._check_clarity,
                "description": "检查需求表述的清晰度"
            },
            {
                "category": "可验证性",
                "check": self._check_verifiability,
                "description": "检查需求是否可验证"
            },
            {
                "category": "一致性",
                "check": self._check_consistency,
                "description": "检查需求之间的一致性"
            }
        ]

    def review(self, content: str) -> Dict[str, Any]:
        """审查需求文档"""
        issues = []
        suggestions = []

        # 分词
        words = list(jieba.cut(content))

        # 检查必备要素
        missing_elements = self._check_required_elements(content, words)
        if missing_elements:
            issues.append({
                "type": "missing_element",
                "level": "error",
                "message": f"缺失必备要素: {', '.join(missing_elements)}",
                "suggestion": f"请补充 {', '.join(missing_elements)} 的详细说明"
            })

        # 检查表述规范性
        vague_expressions = self._check_vague_expressions(content)
        if vague_expressions:
            for expr in vague_expressions:
                issues.append({
                    "type": "vague_expression",
                    "level": "warning",
                    "message": f"存在模糊表述: '{expr}'",
                    "suggestion": "建议使用具体、可量化的表述"
                })

        # 运行常见问题检查规则
        for rule in self.common_issues:
            rule_issues = rule["check"](content, words)
            issues.extend(rule_issues)

        # 计算完整度评分
        completeness_score = self._calculate_completeness_score(issues, content)

        # 生成修改建议
        suggestions = self._generate_suggestions(issues)

        return {
            "issues": issues,
            "suggestions": suggestions,
            "completeness_score": completeness_score,
            "issue_count": len(issues),
            "error_count": sum(1 for i in issues if i["level"] == "error"),
            "warning_count": sum(1 for i in issues if i["level"] == "warning"),
            "info_count": sum(1 for i in issues if i["level"] == "info")
        }

    def _check_required_elements(self, content: str, words: List[str]) -> List[str]:
        """检查必备要素"""
        missing = []
        for element, keywords in self.required_elements.items():
            found = any(keyword in content for keyword in keywords)
            if not found:
                missing.append(element)
        return missing

    def _check_vague_expressions(self, content: str) -> List[str]:
        """检查模糊表述"""
        found = []
        for category, expressions in self.expression_rules.items():
            for expr in expressions:
                if expr in content:
                    found.append(expr)
        return found

    def _check_completeness(self, content: str, words: List[str]) -> List[Dict]:
        """检查完整性"""
        issues = []

        # 检查文档长度
        if len(content) < 100:
            issues.append({
                "type": "completeness",
                "level": "warning",
                "message": "需求文档内容过短",
                "suggestion": "建议补充更多需求细节"
            })

        # 检查是否包含技术参数
        tech_keywords = ["参数", "规格", "配置", "技术要求"]
        if not any(keyword in content for keyword in tech_keywords):
            issues.append({
                "type": "completeness",
                "level": "info",
                "message": "缺少技术参数说明",
                "suggestion": "建议补充具体技术参数"
            })

        return issues

    def _check_clarity(self, content: str, words: List[str]) -> List[Dict]:
        """检查清晰度"""
        issues = []

        # 检查是否有过长的句子
        sentences = re.split(r'[。！？；]', content)
        long_sentences = [s for s in sentences if len(s) > 100]
        if long_sentences:
            issues.append({
                "type": "clarity",
                "level": "info",
                "message": f"发现 {len(long_sentences)} 个过长的句子",
                "suggestion": "建议将长句子拆分为多个短句，提高可读性"
            })

        return issues

    def _check_verifiability(self, content: str, words: List[str]) -> List[Dict]:
        """检查可验证性"""
        issues = []

        # 检查是否包含可量化的指标
        number_pattern = re.findall(r'\d+(?:\.\d+)?', content)
        if len(number_pattern) < 3:
            issues.append({
                "type": "verifiability",
                "level": "warning",
                "message": "缺少可量化的指标",
                "suggestion": "建议增加具体的数值指标，便于验收验证"
            })

        return issues

    def _check_consistency(self, content: str, words: List[str]) -> List[Dict]:
        """检查一致性"""
        issues = []

        # 简单的一致性检查：检查重复的内容
        if len(words) > 50:
            # 检查是否有明显重复的短语
            phrases = [content[i:i+10] for i in range(0, len(content)-10, 10)]
            duplicate_phrases = [p for p in phrases if phrases.count(p) > 2]
            if duplicate_phrases:
                issues.append({
                    "type": "consistency",
                    "level": "info",
                    "message": "发现重复的内容",
                    "suggestion": "建议检查并整合重复的需求描述"
                })

        return issues

    def _calculate_completeness_score(self, issues: List[Dict], content: str) -> float:
        """计算完整度评分"""
        base_score = 100

        # 根据问题数量和严重程度扣分
        for issue in issues:
            if issue["level"] == "error":
                base_score -= 15
            elif issue["level"] == "warning":
                base_score -= 8
            elif issue["level"] == "info":
                base_score -= 3

        # 根据内容长度加分
        if len(content) > 500:
            base_score = min(100, base_score + 5)
        elif len(content) > 200:
            base_score = min(100, base_score + 3)

        return max(0, min(100, base_score))

    def _generate_suggestions(self, issues: List[Dict]) -> List[str]:
        """生成修改建议"""
        suggestions = []

        # 按类型汇总建议
        error_types = set(i.get("type", "") for i in issues if i.get("level") == "error")
        warning_types = set(i.get("type", "") for i in issues if i.get("level") == "warning")

        if "missing_element" in error_types:
            suggestions.append("补充缺失的必备要素（用途、功能边界、关键性能指标）")

        if "vague_expression" in warning_types:
            suggestions.append("将模糊表述替换为具体、可量化的描述")

        if any(i["level"] == "warning" and i["type"] == "verifiability" for i in issues):
            suggestions.append("增加具体的数值指标和验收标准")

        if any(i["level"] == "warning" and i["type"] == "completeness" for i in issues):
            suggestions.append("补充更多需求细节和技术参数")

        if not suggestions:
            suggestions.append("需求文档质量良好，建议补充更多实施细节")

        return suggestions
