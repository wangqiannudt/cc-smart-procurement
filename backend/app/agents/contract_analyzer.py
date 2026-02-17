import re
from typing import List, Dict, Any, Optional
import jieba

class ContractAnalyzer:
    """合同要素识别与风险提示智能体"""

    def __init__(self):
        # 初始化jieba分词
        jieba.initialize()

        # 合同要素关键词
        self.contract_elements = {
            "合同金额": [
                "金额", "费用", "价格", "价款", "款项", "人民币",
                "万元", "元", "合计", "总计", "总价", "报价"
            ],
            "交付范围": [
                "交付", "范围", "交付物", "交付内容", "交付成果",
                "服务范围", "供货范围", "包含", "包括", "涉及"
            ],
            "交付期限": [
                "期限", "期限届满", "交付期限", "工期", "周期",
                "期限", "交货期", "交货时间", "交付时间", "完成时间",
                "日", "天", "月", "年", "工作日"
            ],
            "验收条款": [
                "验收", "验收标准", "验收条件", "验收流程", "验收方式",
                "验收测试", "验收合格", "验收确认", "试运行", "测试"
            ],
            "付款方式": [
                "付款", "支付", "付款方式", "支付方式", "付款条件",
                "支付条款", "预付款", "进度款", "尾款", "分期付款"
            ],
            "质保条款": [
                "质保", "保修", "质量保证", "维保", "维护", "质保期",
                "保修期", "服务期限", "免费维护"
            ],
            "违约责任": [
                "违约", "违约责任", "违约金", "赔偿", "损失赔偿",
                "逾期", "延迟", "违约处罚", "责任"
            ],
            "争议解决": [
                "争议", "争议解决", "仲裁", "诉讼", "管辖", "法律",
                "法院", "仲裁委", "协商"
            ]
        }

        # 风险条款关键词
        self.risk_keywords = {
            "高风险": [
                "无", "不承担", "免除", "不负", "概不负责",
                "单方面", "随时", "无限期", "无理由"
            ],
            "中风险": [
                "承担全部", "全部费用", "自行承担",
                "至少", "不低于", "不超过"
            ],
            "需特别关注": [
                "可能", "视情况", "具体", "另行", "另行约定",
                "协商", "双方协商", "待定", "补充协议"
            ]
        }

    def analyze(self, content: str) -> Dict[str, Any]:
        """分析合同文档"""
        # 提取合同要素
        elements = self._extract_elements(content)

        # 识别风险条款
        risks = self._identify_risks(content)

        # 评估风险等级
        risk_level = self._assess_risk_level(risks)

        # 生成分析报告
        report = self._generate_report(elements, risks, risk_level)

        return report

    def _extract_elements(self, content: str) -> Dict[str, Any]:
        """提取合同要素"""
        elements = {}

        for element_name, keywords in self.contract_elements.items():
            found_keywords = []
            found_contexts = []

            for keyword in keywords:
                if keyword in content:
                    found_keywords.append(keyword)

                    # 提取关键词附近的上下文
                    matches = re.finditer(rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}', content)
                    for match in matches:
                        context = match.group().strip()
                        if context not in found_contexts:
                            found_contexts.append(context)

            if found_keywords:
                elements[element_name] = {
                    "found": True,
                    "keywords": found_keywords,
                    "contexts": found_contexts[:3]  # 只保留前3个上下文
                }
            else:
                elements[element_name] = {
                    "found": False,
                    "keywords": [],
                    "contexts": []
                }

        # 特殊处理：提取合同金额的具体数值
        if elements.get("合同金额", {}).get("found"):
            amounts = self._extract_amounts(content)
            if amounts:
                elements["合同金额"]["values"] = amounts

        return elements

    def _extract_amounts(self, content: str) -> List[str]:
        """提取合同金额数值"""
        amounts = []

        # 匹配金额模式：数字+单位
        patterns = [
            r'(\d+(?:\.\d+)?)\s*万元',
            r'(\d+(?:\.\d+)?)\s*元',
            r'¥\s*(\d+(?:\.\d+)?)',
            r'人民币\s*(\d+(?:\.\d+)?)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            amounts.extend(matches)

        # 去重并返回
        return list(set(amounts))

    def _identify_risks(self, content: str) -> List[Dict[str, Any]]:
        """识别风险条款"""
        risks = []

        for risk_level, keywords in self.risk_keywords.items():
            for keyword in keywords:
                # 查找包含关键词的句子
                sentences = re.split(r'[。！？；]', content)
                for sentence in sentences:
                    if keyword in sentence:
                        risks.append({
                            "level": risk_level,
                            "keyword": keyword,
                            "sentence": sentence.strip(),
                            "suggestion": self._get_risk_suggestion(risk_level, keyword)
                        })

        return risks

    def _get_risk_suggestion(self, risk_level: str, keyword: str) -> str:
        """获取风险建议"""
        suggestions = {
            "高风险": {
                "无": "建议明确相关责任，避免无责任条款",
                "不承担": "建议明确责任划分，避免免责条款",
                "免除": "谨慎审查免责条款，确保合理分担风险",
                "不负": "建议明确相关责任，避免模糊表述",
                "概不负责": "建议修改为合理的责任分担条款",
                "单方面": "建议修改为双方协商确定",
                "随时": "建议明确具体时间和条件",
                "无限期": "建议设定明确期限",
                "无理由": "建议增加正当理由说明"
            },
            "中风险": {
                "承担全部": "建议评估是否合理，考虑风险分担",
                "全部费用": "建议明确费用构成和合理性",
                "自行承担": "建议评估责任分配是否公平",
                "至少": "建议核实最低标准的合理性",
                "不低于": "建议核实最低要求的合理性",
                "不超过": "建议核实上限的合理性"
            },
            "需特别关注": {
                "可能": "建议明确具体条件",
                "视情况": "建议补充具体判断标准",
                "具体": "建议补充详细说明",
                "另行": "建议在合同中明确相关条款",
                "另行约定": "建议避免另行约定，直接在合同中明确",
                "协商": "建议明确协商结果的确定方式",
                "双方协商": "建议补充协商不成时的处理方式",
                "待定": "建议避免待定条款，直接明确",
                "补充协议": "建议在主合同中明确主要内容"
            }
        }

        return suggestions.get(risk_level, {}).get(keyword, "建议仔细审查该条款")

    def _assess_risk_level(self, risks: List[Dict]) -> str:
        """评估整体风险等级"""
        high_count = sum(1 for r in risks if r["level"] == "高风险")
        medium_count = sum(1 for r in risks if r["level"] == "中风险")
        low_count = sum(1 for r in risks if r["level"] == "需特别关注")

        if high_count >= 3:
            return "高风险"
        elif high_count >= 1 or medium_count >= 3:
            return "中风险"
        elif medium_count >= 1 or low_count >= 5:
            return "低风险"
        else:
            return "风险可控"

    def _generate_report(self, elements: Dict[str, Any], risks: List[Dict], risk_level: str) -> Dict[str, Any]:
        """生成分析报告"""
        # 统计要素完成度
        found_elements = sum(1 for e in elements.values() if e["found"])
        total_elements = len(elements)
        completeness = round((found_elements / total_elements) * 100, 1)

        # 按风险等级分类
        risk_summary = {
            "高风险": [r for r in risks if r["level"] == "高风险"],
            "中风险": [r for r in risks if r["level"] == "中风险"],
            "需特别关注": [r for r in risks if r["level"] == "需特别关注"]
        }

        # 生成建议
        suggestions = self._generate_suggestions(elements, risks, risk_level)

        return {
            "elements": elements,
            "risks": risks,
            "risk_level": risk_level,
            "risk_summary": {
                k: len(v) for k, v in risk_summary.items()
            },
            "completeness": completeness,
            "suggestions": suggestions
        }

    def _generate_suggestions(self, elements: Dict[str, Any], risks: List[Dict], risk_level: str) -> List[str]:
        """生成修改建议"""
        suggestions = []

        # 检查缺失的要素
        missing_elements = [name for name, data in elements.items() if not data["found"]]
        if missing_elements:
            suggestions.append(f"建议补充以下合同要素: {', '.join(missing_elements)}")

        # 根据风险等级生成建议
        if risk_level == "高风险":
            suggestions.append("合同风险较高，建议重点修改高风险条款")
        elif risk_level == "中风险":
            suggestions.append("合同存在中等风险，建议审查并修改相关条款")
        elif risk_level == "低风险":
            suggestions.append("合同风险较低，建议关注需特别关注的条款")

        # 如果没有风险提示
        if not risks:
            suggestions.append("合同条款较为完善，建议仔细核对金额和期限等关键信息")

        return suggestions
