"""
需求规范审查智能体 - 重构版
集成规则引擎、字段提取器和风险检测器
"""
import re
from typing import List, Dict, Any, Optional
import jieba
import sys
from pathlib import Path

# 添加项目路径
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.rule_engine import RuleEngine
from app.core.field_extractor import FieldExtractor
from app.core.risk_detector import RiskDetector


class RequirementReviewer:
    """需求规范审查智能体"""

    def __init__(self, rules_dir: str = None):
        """
        初始化需求审查智能体

        Args:
            rules_dir: 规则文件目录路径（可选）
        """
        # 初始化jieba分词
        jieba.initialize()

        # 初始化核心模块
        self.rule_engine = RuleEngine(rules_dir)
        self.field_extractor = FieldExtractor()
        self.risk_detector = RiskDetector()

        # 通用规则（作为降级方案）
        self._init_generic_rules()

    def _init_generic_rules(self):
        """初始化通用规则（当未指定品类时使用）"""
        self.generic_required_elements = {
            "用途": ["用途", "应用场景", "使用场景", "应用于", "用于"],
            "功能边界": ["功能", "功能模块", "功能描述", "功能要求", "功能说明"],
            "关键性能指标": ["性能", "指标", "参数", "响应时间", "处理能力", "吞吐量"]
        }

        self.generic_expression_rules = {
            "模糊表述": ["大约", "大概", "左右", "尽可能", "尽量", "高性能"],
            "绝对化表述": ["必须", "绝对", "一定", "确保", "保证"]
        }

    def review(self, content: str, category_id: str = None, subtype_id: str = None) -> Dict[str, Any]:
        """
        审查需求文档

        Args:
            content: 需求文档内容
            category_id: 品类ID（可选），如 'server', 'workstation'
            subtype_id: 子类型ID（可选），如 'gpu_ai_server', 'graphics_workstation'

        Returns:
            审查结果字典
        """
        if category_id:
            return self._review_with_category(content, category_id, subtype_id)
        return self._generic_review(content)

    def _review_with_category(self, content: str, category_id: str, subtype_id: str = None) -> Dict[str, Any]:
        """
        使用品类特定规则进行审查

        Args:
            content: 文档内容
            category_id: 品类ID
            subtype_id: 子类型ID

        Returns:
            审查结果
        """
        issues = []
        extracted_fields = {}
        field_results = {}

        # 1. 加载品类规则
        fields = self.rule_engine.get_fields(category_id, subtype_id)
        risk_rules = self.rule_engine.get_risk_rules(category_id)

        if not fields:
            # 如果没有找到品类规则，降级到通用审查
            return self._generic_review(content)

        # 2. 提取字段
        field_results = self.field_extractor.extract_all_fields(content, fields)

        # 3. 验证字段
        issues = self._validate_fields(content, field_results, fields, subtype_id)

        # 4. 风险检测
        risks = self.risk_detector.detect_risks(content, risk_rules)

        # 将风险转换为问题格式
        for risk in risks:
            issues.append({
                "type": "risk",
                "level": self._priority_to_level(risk.get("priority", "P2")),
                "message": risk.get("message", f"检测到风险：{risk.get('keyword', '')}"),
                "suggestion": risk.get("suggestion", "建议修改以降低风险"),
                "keyword": risk.get("keyword"),
                "rule_id": risk.get("rule_id")
            })

        # 5. 组织提取的字段
        for field_id, result in field_results.items():
            if result.get("found"):
                extracted_fields[field_id] = {
                    "label": result.get("label", field_id),
                    "value": result.get("value"),
                    "confidence": result.get("confidence", 0)
                }

        # 6. 计算评分
        completeness_score = self._calculate_category_score(issues, fields, field_results)

        # 7. 生成建议
        suggestions = self._generate_category_suggestions(issues, fields, field_results)

        # 8. 分类统计
        p0_fields = [f for f in fields if f.get("priority") == "P0"]
        missing_p0 = [f for f in p0_fields if not field_results.get(f["field_id"], {}).get("found")]

        return {
            "category_id": category_id,
            "subtype_id": subtype_id,
            "issues": issues,
            "suggestions": suggestions,
            "completeness_score": completeness_score,
            "issue_count": len(issues),
            "error_count": sum(1 for i in issues if i["level"] == "error"),
            "warning_count": sum(1 for i in issues if i["level"] == "warning"),
            "info_count": sum(1 for i in issues if i["level"] == "info"),
            "extracted_fields": extracted_fields,
            "field_count": len(extracted_fields),
            "missing_p0_count": len(missing_p0),
            "risk_summary": self.risk_detector.get_risk_summary(risks)
        }

    def _validate_fields(self, content: str, field_results: Dict, fields: List[Dict],
                        subtype_id: str = None) -> List[Dict]:
        """
        验证字段完整性和合规性

        Args:
            content: 文档内容
            field_results: 字段提取结果
            fields: 字段定义列表
            subtype_id: 子类型ID

        Returns:
            问题列表
        """
        issues = []

        for field_def in fields:
            field_id = field_def.get("field_id")
            priority = field_def.get("priority", "P2")
            required_for = field_def.get("required_for", ["all"])
            validation = field_def.get("validation", {})

            # 检查字段是否适用于当前子类型
            if subtype_id and "all" not in required_for and subtype_id not in required_for:
                continue

            result = field_results.get(field_id, {})
            is_found = result.get("found", False)
            value = result.get("value")

            # P0 必填字段检查
            if priority == "P0" and not is_found:
                issues.append({
                    "type": "missing_field",
                    "level": "error",
                    "message": f"缺失必填字段：{field_def.get('label', field_id)}",
                    "suggestion": validation.get("message_cn", f"请补充{field_def.get('label', field_id)}"),
                    "field_id": field_id,
                    "priority": priority
                })
                continue

            # 验证规则检查
            if is_found and validation:
                # 检查禁止的表述
                reject_contains = validation.get("reject_if_contains_cn", [])
                for reject_word in reject_contains:
                    if isinstance(value, str) and reject_word in value:
                        issues.append({
                            "type": "invalid_content",
                            "level": "warning",
                            "message": f"{field_def.get('label')}包含不可测表述：{reject_word}",
                            "suggestion": validation.get("message_cn", "请使用可量化的表述"),
                            "field_id": field_id
                        })

                # 检查仅包含口号化表述
                reject_only = validation.get("reject_if_only_contains_cn", [])
                if reject_only and isinstance(value, str):
                    only_slogans = all(any(s in value for s in reject_only) for _ in [1])
                    # 简化检查：如果值很短且只包含口号词
                    if len(value) < 50:
                        for slogan in reject_only:
                            if slogan in value:
                                issues.append({
                                    "type": "slogan_content",
                                    "level": "warning",
                                    "message": f"{field_def.get('label')}描述过于口号化",
                                    "suggestion": validation.get("message_cn", "建议补充具体内容"),
                                    "field_id": field_id
                                })
                                break

                # 数值范围检查
                min_value = validation.get("min_value")
                if min_value is not None and value is not None:
                    actual_value = value
                    if isinstance(value, dict):
                        actual_value = value.get("value")
                    if isinstance(actual_value, (int, float)) and actual_value < min_value:
                        issues.append({
                            "type": "invalid_value",
                            "level": "warning",
                            "message": f"{field_def.get('label')}值{actual_value}小于最小值{min_value}",
                            "suggestion": f"请确认{field_def.get('label')}是否正确",
                            "field_id": field_id
                        })

        return issues

    def _generic_review(self, content: str) -> Dict[str, Any]:
        """
        通用审查（未指定品类时使用）

        Args:
            content: 文档内容

        Returns:
            审查结果
        """
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
        for rule in self._get_common_issue_rules():
            rule_issues = rule["check"](content, words)
            issues.extend(rule_issues)

        # 使用风险检测器进行通用风险检测
        risks = self.risk_detector.detect_risks(content)
        for risk in risks:
            issues.append({
                "type": "risk",
                "level": self._priority_to_level(risk.get("priority", "P2")),
                "message": risk.get("message", f"检测到风险：{risk.get('keyword', '')}"),
                "suggestion": risk.get("suggestion", "建议修改以降低风险")
            })

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
            "info_count": sum(1 for i in issues if i["level"] == "info"),
            "extracted_fields": {},
            "field_count": 0
        }

    def _check_required_elements(self, content: str, words: List[str]) -> List[str]:
        """检查必备要素"""
        missing = []
        for element, keywords in self.generic_required_elements.items():
            found = any(keyword in content for keyword in keywords)
            if not found:
                missing.append(element)
        return missing

    def _check_vague_expressions(self, content: str) -> List[str]:
        """检查模糊表述"""
        found = []
        for category, expressions in self.generic_expression_rules.items():
            for expr in expressions:
                if expr in content:
                    found.append(expr)
        return found

    def _get_common_issue_rules(self) -> List[Dict]:
        """获取常见问题检查规则"""
        return [
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
            }
        ]

    def _check_completeness(self, content: str, words: List[str]) -> List[Dict]:
        """检查完整性"""
        issues = []

        if len(content) < 100:
            issues.append({
                "type": "completeness",
                "level": "warning",
                "message": "需求文档内容过短",
                "suggestion": "建议补充更多需求细节"
            })

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

        number_pattern = re.findall(r'\d+(?:\.\d+)?', content)
        if len(number_pattern) < 3:
            issues.append({
                "type": "verifiability",
                "level": "warning",
                "message": "缺少可量化的指标",
                "suggestion": "建议增加具体的数值指标，便于验收验证"
            })

        return issues

    def _calculate_completeness_score(self, issues: List[Dict], content: str) -> float:
        """计算完整度评分"""
        base_score = 100

        for issue in issues:
            if issue["level"] == "error":
                base_score -= 15
            elif issue["level"] == "warning":
                base_score -= 8
            elif issue["level"] == "info":
                base_score -= 3

        if len(content) > 500:
            base_score = min(100, base_score + 5)
        elif len(content) > 200:
            base_score = min(100, base_score + 3)

        return max(0, min(100, base_score))

    def _calculate_category_score(self, issues: List[Dict], fields: List[Dict],
                                  field_results: Dict) -> float:
        """
        计算品类审查评分

        基于字段完成度和问题严重程度计算
        """
        base_score = 100

        # 统计P0字段完成率
        p0_fields = [f for f in fields if f.get("priority") == "P0"]
        p0_found = sum(1 for f in p0_fields if field_results.get(f["field_id"], {}).get("found"))
        p0_ratio = p0_found / len(p0_fields) if p0_fields else 1

        # 根据P0字段完成率调整分数
        base_score *= (0.5 + 0.5 * p0_ratio)  # P0字段占50%权重

        # 根据问题扣分
        for issue in issues:
            if issue["level"] == "error":
                base_score -= 10
            elif issue["level"] == "warning":
                base_score -= 5
            elif issue["level"] == "info":
                base_score -= 2

        return max(0, min(100, base_score))

    def _generate_suggestions(self, issues: List[Dict]) -> List[str]:
        """生成修改建议"""
        suggestions = []

        error_types = set(i.get("type", "") for i in issues if i.get("level") == "error")
        warning_types = set(i.get("type", "") for i in issues if i.get("level") == "warning")

        if "missing_element" in error_types or "missing_field" in error_types:
            suggestions.append("补充缺失的必备要素")

        if "vague_expression" in warning_types:
            suggestions.append("将模糊表述替换为具体、可量化的描述")

        if any(i["level"] == "warning" and i["type"] == "verifiability" for i in issues):
            suggestions.append("增加具体的数值指标和验收标准")

        if any(i["type"] == "risk" for i in issues):
            suggestions.append("修改存在指向性风险的表述，改用性能参数描述")

        if not suggestions:
            suggestions.append("需求文档质量良好，建议补充更多实施细节")

        return suggestions

    def _generate_category_suggestions(self, issues: List[Dict], fields: List[Dict],
                                       field_results: Dict) -> List[str]:
        """生成品类特定的修改建议"""
        suggestions = []

        # 获取缺失的P0字段
        p0_fields = [f for f in fields if f.get("priority") == "P0"]
        missing_p0 = [f for f in p0_fields if not field_results.get(f["field_id"], {}).get("found")]

        if missing_p0:
            labels = [f.get("label", f.get("field_id")) for f in missing_p0[:3]]
            suggestions.append(f"补充必填字段：{', '.join(labels)}")

        # 风险相关建议
        risk_issues = [i for i in issues if i.get("type") == "risk"]
        if risk_issues:
            suggestions.append("修改品牌/型号等指向性表述，改用性能参数描述")

        # 模糊表述建议
        vague_issues = [i for i in issues if "vague" in i.get("type", "")]
        if vague_issues:
            suggestions.append("使用具体数值替代模糊表述")

        if not suggestions:
            suggestions.append("需求文档质量良好")

        return suggestions

    def _priority_to_level(self, priority: str) -> str:
        """将优先级转换为问题级别"""
        mapping = {
            "P0": "error",
            "P1": "warning",
            "P2": "info"
        }
        return mapping.get(priority, "info")

    def get_available_categories(self) -> List[Dict]:
        """
        获取可用品类列表

        Returns:
            品类信息列表
        """
        return self.rule_engine.get_available_categories()

    def get_category_fields(self, category_id: str, subtype_id: str = None) -> List[Dict]:
        """
        获取品类字段定义

        Args:
            category_id: 品类ID
            subtype_id: 子类型ID

        Returns:
            字段定义列表
        """
        fields = self.rule_engine.get_fields(category_id, subtype_id)
        return [
            {
                "field_id": f.get("field_id"),
                "label": f.get("label"),
                "priority": f.get("priority"),
                "type": f.get("type"),
                "required": f.get("priority") == "P0"
            }
            for f in fields
        ]
