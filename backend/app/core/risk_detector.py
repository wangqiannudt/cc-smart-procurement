"""
风险检测器模块 - 检测品牌/型号/模糊表述等风险
"""
import re
from typing import Dict, List, Any, Optional


class RiskDetector:
    """风险检测器：检测品牌/型号/模糊表述等采购风险"""

    def __init__(self):
        """初始化风险检测器"""
        # 品牌关键词（高风险）
        self.brand_keywords = {
            # 国际品牌
            "cn": ["戴尔", "惠普", "联想", "华为", "浪潮", "曙光", "IBM", "思科", "英伟达", "AMD", "英特尔"],
            "en": ["Dell", "HP", "HPE", "Lenovo", "Huawei", "Inspur", "Sugon", "IBM", "Cisco",
                   "NVIDIA", "AMD", "Intel", "Supermicro", "Gigabyte", "ASUS"]
        }

        # 产品系列/型号关键词（高风险）
        self.model_patterns = [
            # GPU型号
            r"(?i)\b(geforce|quadro|rtx|gtx|tesla|titan|radeon|instinct|arc)\s*\d*\b",
            r"(?i)\b(rt\s*40|rt\s*30|gtx\s*16|rx\s*\d+|mi\s*\d+)\b",
            # CPU型号
            r"(?i)\b(xeon|epyc|threadripper|core\s*i\d|ryzen)\s*\d+\b",
            r"(?i)\b(i\d-\d{4,5}[a-z]*)\b",
            # 服务器型号
            r"(?i)\b(poweredge|proliant|thinksystem|altros|fusionserver|gen10|gen9)\b",
            r"(?i)\b(r\d{3,4}|dl\d{3,4}|ml\d{3,4}|sr\d{3,4})\b",
            # 通用型号模式
            r"(?i)\b(a\d{2,4}|h\d{2,4}|v\d{2,4}|mi\d{2,4}|nx\d{3,4})\b"
        ]

        # 模糊表述（中高风险）
        self.vague_expressions = {
            "P0": [
                "指定品牌", "指定型号", "仅限", "必须使用", "只能采购"
            ],
            "P1": [
                "大约", "大概", "左右", "尽可能", "尽量", "高性能计算机", "高端服务器",
                "先进水平", "国际领先", "国内领先", "性能优异", "行业标杆"
            ],
            "P2": [
                "高性能", "高配置", "主流配置", "通用型", "标准型"
            ]
        }

        # 标杆引用模式（中风险）
        self.benchmark_patterns = [
            r"性能不低于\s*[a-zA-Z0-9\-]+",
            r"不弱于\s*[a-zA-Z0-9\-]+",
            r"不差于\s*[a-zA-Z0-9\-]+",
            r"与\s*[a-zA-Z0-9\-]+\s*同等",
            r"相当于\s*[a-zA-Z0-9\-]+",
            r"对标\s*[a-zA-Z0-9\-]+"
        ]

    def detect_risks(self, content: str, risk_rules: List[Dict] = None) -> List[Dict]:
        """
        执行风险检测

        Args:
            content: 文档内容
            risk_rules: 风险规则列表（可选，使用自定义规则）

        Returns:
            检测到的风险列表
        """
        risks = []

        # 使用自定义规则或默认规则
        rules = risk_rules or self._get_default_rules()

        for rule in rules:
            detected = self._apply_rule(content, rule)
            if detected:
                risks.extend(detected)

        # 使用内置检测
        risks.extend(self._detect_brands(content))
        risks.extend(self._detect_models(content))
        risks.extend(self._detect_vague_expressions(content))
        risks.extend(self._detect_benchmark_references(content))

        # 去重
        risks = self._deduplicate_risks(risks)

        return risks

    def _get_default_rules(self) -> List[Dict]:
        """获取默认风险规则"""
        return []

    def _apply_rule(self, content: str, rule: Dict) -> List[Dict]:
        """
        应用单条风险规则

        Args:
            content: 文档内容
            rule: 风险规则

        Returns:
            检测到的风险列表
        """
        risks = []
        trigger_patterns = rule.get("trigger_patterns", {})
        rule_id = rule.get("rule_id", "unknown")
        priority = rule.get("priority", "P2")
        description = rule.get("description_cn", "")
        action = rule.get("action", {})
        message = action.get("report_message_cn", description)

        # 检查中文关键词
        cn_keywords = trigger_patterns.get("cn_keywords", [])
        for keyword in cn_keywords:
            if keyword in content:
                risks.append({
                    "rule_id": rule_id,
                    "type": "keyword",
                    "priority": priority,
                    "keyword": keyword,
                    "message": f"{message}（关键词：{keyword}）",
                    "suggestion": self._get_suggestion(rule_id, priority)
                })

        # 检查中文短语
        cn_phrases = trigger_patterns.get("cn_phrases", [])
        for phrase in cn_phrases:
            if phrase in content:
                risks.append({
                    "rule_id": rule_id,
                    "type": "phrase",
                    "priority": priority,
                    "keyword": phrase,
                    "message": f"{message}（短语：{phrase}）",
                    "suggestion": self._get_suggestion(rule_id, priority)
                })

        # 检查正则模式
        regex_patterns = trigger_patterns.get("regex", [])
        for pattern in regex_patterns:
            try:
                matches = re.finditer(pattern, content)
                for match in matches:
                    matched_text = match.group(0)
                    risks.append({
                        "rule_id": rule_id,
                        "type": "pattern",
                        "priority": priority,
                        "keyword": matched_text,
                        "position": match.start(),
                        "message": f"{message}（匹配：{matched_text}）",
                        "suggestion": self._get_suggestion(rule_id, priority)
                    })
            except re.error:
                continue

        return risks

    def _detect_brands(self, content: str) -> List[Dict]:
        """检测品牌指向性"""
        risks = []

        # 检查中文品牌名
        for brand in self.brand_keywords["cn"]:
            if brand in content:
                risks.append({
                    "rule_id": "risk.brand_directivity",
                    "type": "brand",
                    "priority": "P0",
                    "keyword": brand,
                    "message": f'检测到品牌名称"{brand}"，存在采购指向性风险',
                    "suggestion": "建议删除品牌名称，改用性能参数描述"
                })

        # 检查英文品牌名（区分大小写，避免误报）
        for brand in self.brand_keywords["en"]:
            # 使用单词边界匹配
            pattern = r'\b' + re.escape(brand) + r'\b'
            if re.search(pattern, content, re.IGNORECASE):
                risks.append({
                    "rule_id": "risk.brand_directivity",
                    "type": "brand",
                    "priority": "P0",
                    "keyword": brand,
                    "message": f'检测到品牌名称"{brand}"，存在采购指向性风险',
                    "suggestion": "建议删除品牌名称，改用性能参数描述"
                })

        return risks

    def _detect_models(self, content: str) -> List[Dict]:
        """检测型号指向性"""
        risks = []

        for pattern in self.model_patterns:
            try:
                matches = re.finditer(pattern, content)
                for match in matches:
                    matched_text = match.group(0)
                    # 排除一些常见的非型号匹配
                    if self._is_likely_model(matched_text):
                        risks.append({
                            "rule_id": "risk.model_designation",
                            "type": "model",
                            "priority": "P0",
                            "keyword": matched_text,
                            "position": match.start(),
                            "message": f'检测到型号"{matched_text}"，存在采购指向性风险',
                            "suggestion": "建议删除型号，改用性能参数描述（如核心数、主频、显存等）"
                        })
            except re.error:
                continue

        return risks

    def _is_likely_model(self, text: str) -> bool:
        """判断是否可能是产品型号"""
        # 排除一些常见的误报
        false_positives = ["i3", "i5", "i7", "i9", "4G", "5G", "3G"]  # 这些在上下文中可能不是型号
        text_lower = text.lower()

        # 如果是纯数字或太短，可能不是型号
        if len(text) < 3 or text.isdigit():
            return False

        # 检查是否包含字母（型号通常包含字母）
        has_letter = any(c.isalpha() for c in text)
        if not has_letter:
            return False

        return True

    def _detect_vague_expressions(self, content: str) -> List[Dict]:
        """检测模糊表述"""
        risks = []

        for priority, expressions in self.vague_expressions.items():
            for expr in expressions:
                if expr in content:
                    risks.append({
                        "rule_id": "risk.vague_expression",
                        "type": "vague",
                        "priority": priority,
                        "keyword": expr,
                        "message": f'检测到模糊表述"{expr}"',
                        "suggestion": "建议使用具体、可量化的表述替代模糊表达"
                    })

        return risks

    def _detect_benchmark_references(self, content: str) -> List[Dict]:
        """检测标杆引用"""
        risks = []

        for pattern in self.benchmark_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                matched_text = match.group(0)
                risks.append({
                    "rule_id": "risk.benchmark_reference",
                    "type": "benchmark",
                    "priority": "P1",
                    "keyword": matched_text,
                    "position": match.start(),
                    "message": f'检测到标杆引用"{matched_text}"，存在指向性风险',
                    "suggestion": "建议将标杆式引用改为参数化表达（如显存/算力/带宽等）"
                })

        return risks

    def _get_suggestion(self, rule_id: str, priority: str) -> str:
        """获取风险修复建议"""
        suggestions = {
            "risk.explicit_model_or_brand": "请使用性能参数（如核心数、主频、容量等）替代品牌/型号",
            "risk.benchmark_model_reference": "建议用具体参数（显存、算力、带宽）替代标杆型号引用",
            "risk.vague_expression": "建议使用具体数值和可量化指标替代模糊表述",
            "risk.brand_directivity": "建议删除品牌名称，改用通用性能描述",
            "risk.model_designation": "建议删除型号，改用性能参数描述"
        }
        return suggestions.get(rule_id, "建议修改以降低采购风险")

    def _deduplicate_risks(self, risks: List[Dict]) -> List[Dict]:
        """去重风险列表"""
        seen = set()
        unique_risks = []

        for risk in risks:
            # 使用 rule_id + keyword 作为唯一标识
            key = (risk.get("rule_id", ""), risk.get("keyword", ""))
            if key not in seen:
                seen.add(key)
                unique_risks.append(risk)

        return unique_risks

    def get_risk_summary(self, risks: List[Dict]) -> Dict:
        """
        获取风险摘要

        Args:
            risks: 风险列表

        Returns:
            风险摘要统计
        """
        summary = {
            "total": len(risks),
            "P0_count": 0,
            "P1_count": 0,
            "P2_count": 0,
            "by_type": {},
            "has_blocking_risks": False
        }

        for risk in risks:
            priority = risk.get("priority", "P2")
            risk_type = risk.get("type", "unknown")

            if priority == "P0":
                summary["P0_count"] += 1
            elif priority == "P1":
                summary["P1_count"] += 1
            else:
                summary["P2_count"] += 1

            summary["by_type"][risk_type] = summary["by_type"].get(risk_type, 0) + 1

        summary["has_blocking_risks"] = summary["P0_count"] > 0

        return summary

    def check_text_compliance(self, content: str) -> Dict:
        """
        检查文本合规性

        Args:
            content: 文档内容

        Returns:
            合规性检查结果
        """
        risks = self.detect_risks(content)
        summary = self.get_risk_summary(risks)

        return {
            "is_compliant": not summary["has_blocking_risks"],
            "risk_count": summary["total"],
            "blocking_risks": [r for r in risks if r.get("priority") == "P0"],
            "warning_risks": [r for r in risks if r.get("priority") in ["P1", "P2"]],
            "summary": summary
        }
