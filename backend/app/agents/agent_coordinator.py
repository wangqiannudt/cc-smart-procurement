from typing import Dict, Any, List, Optional
from app.agents.requirement_reviewer import RequirementReviewer
from app.agents.price_reference import PriceReference
from app.agents.contract_analyzer import ContractAnalyzer
from app.knowledge.knowledge_base import KnowledgeBase


class AgentCoordinator:
    """智能体协调器 - 增强版，支持跨智能体协作和综合分析"""

    def __init__(self):
        self.requirement_reviewer = RequirementReviewer()
        self.price_reference = PriceReference()
        self.contract_analyzer = ContractAnalyzer()

        # 初始化知识库
        self.knowledge_base = None
        try:
            self.knowledge_base = KnowledgeBase()
            print("知识库初始化成功")
        except Exception as e:
            print(f"知识库初始化失败: {e}")
            print("将继续使用基础功能")

    def analyze_procurement_scenario(self, product_type: str, requirements: str) -> Dict[str, Any]:
        """
        分析采购场景，协调多个智能体提供综合建议

        Args:
            product_type: 产品类型（如：服务器、工作站等）
            requirements: 需求描述

        Returns:
            综合分析报告
        """
        result = {}

        # 1. 需求分析
        result["requirement_analysis"] = self._analyze_requirements(requirements)

        # 2. 价格参考查询
        price_result = self.price_reference.query_price(keyword=product_type)
        result["price_references"] = price_result.get("records", [])[:5]

        # 3. 价格预测（新增）
        try:
            prediction = self.price_reference.predict_price(product_type, months_ahead=3)
            if prediction.get("success"):
                result["price_prediction"] = prediction
        except Exception as e:
            print(f"价格预测失败: {e}")

        # 4. 知识库查询相关建议
        knowledge_tip = "知识库功能暂未启用"
        if self.knowledge_base and hasattr(self.knowledge_base, 'query'):
            try:
                knowledge_tip = self.knowledge_base.query(f"{product_type} 选型")
            except:
                knowledge_tip = "知识库查询失败"

        result["knowledge_tips"] = knowledge_tip

        # 从价格数据计算实际价格范围
        if price_result.get("records"):
            prices = [r["price"] for r in price_result["records"]]
            result["price_range"] = {
                "min": min(prices),
                "max": max(prices),
                "avg": round(sum(prices) / len(prices), 2)
            }
        else:
            result["price_range"] = {"min": 0, "max": 0, "avg": 0}

        # 5. 生成综合建议
        result["synthesis"] = self._generate_synthesis(result)

        return result

    def get_recommendations(self, product_name: str, budget: float) -> Dict[str, Any]:
        """
        根据产品名称和预算获取购买建议

        Args:
            product_name: 产品名称
            budget: 预算

        Returns:
            购买建议
        """
        result = {}

        # 1. 分析报价合理性
        price_analysis = self.price_reference.analyze_price(product_name, budget)
        result["price_analysis"] = price_analysis

        # 2. 查询知识库获取建议
        knowledge_tip = "知识库功能暂未启用"
        if self.knowledge_base and hasattr(self.knowledge_base, 'query'):
            try:
                knowledge_tip = self.knowledge_base.query(f"{product_name} 配置建议")
            except:
                knowledge_tip = "知识库查询失败"

        result["configuration_tips"] = knowledge_tip

        # 3. 获取价格预测建议（新增）
        try:
            prediction = self.price_reference.predict_price(product_name, months_ahead=2)
            if prediction.get("success") and prediction.get("buying_advice"):
                result["timing_advice"] = prediction["buying_advice"]
        except Exception as e:
            print(f"获取购买时机建议失败: {e}")

        # 4. 生成最终建议
        result["recommendation"] = self._generate_recommendation(price_analysis, knowledge_tip)

        return result

    def comprehensive_analysis(self,
                               requirement_text: Optional[str] = None,
                               contract_text: Optional[str] = None,
                               product_keyword: Optional[str] = None,
                               budget: Optional[float] = None) -> Dict[str, Any]:
        """
        跨智能体综合分析

        整合需求审查、合同分析、价格查询等多个智能体的分析结果，
        提供全局视角的采购建议。

        Args:
            requirement_text: 需求文档文本
            contract_text: 合同文档文本
            product_keyword: 产品关键词
            budget: 预算

        Returns:
            综合分析报告，包含各维度分析结果和整体建议
        """
        result = {
            "analysis_dimensions": [],
            "cross_insights": [],
            "risk_score": 0,
            "overall_recommendation": None
        }

        risk_factors = []
        insights = []

        # 1. 需求分析
        if requirement_text:
            req_analysis = self._analyze_requirements(requirement_text)
            result["requirement_analysis"] = req_analysis
            result["analysis_dimensions"].append("requirements")

            if req_analysis["completeness_score"] < 60:
                risk_factors.append({
                    "type": "requirement",
                    "severity": "high",
                    "description": "需求文档不完整",
                    "details": req_analysis["suggestions"]
                })

        # 2. 合同分析
        if contract_text:
            try:
                contract_result = self.contract_analyzer.analyze_contract(contract_text)
                result["contract_analysis"] = contract_result
                result["analysis_dimensions"].append("contract")

                # 检查高风险条款
                high_risks = [r for r in contract_result.get("risks", [])
                              if r.get("level") == "高风险"]
                if high_risks:
                    risk_factors.append({
                        "type": "contract",
                        "severity": "high",
                        "description": f"发现{len(high_risks)}个高风险条款",
                        "details": [r["clause"] for r in high_risks[:3]]
                    })

                # 检查合同与需求的一致性
                if requirement_text:
                    consistency = self._check_requirement_contract_consistency(
                        requirement_text, contract_text
                    )
                    result["consistency_check"] = consistency
                    if consistency.get("inconsistencies"):
                        insights.append({
                            "type": "consistency",
                            "description": "合同与需求存在不一致",
                            "details": consistency["inconsistencies"]
                        })
            except Exception as e:
                result["contract_analysis"] = {"error": str(e)}

        # 3. 价格分析
        if product_keyword:
            try:
                price_result = self.price_reference.query_price(keyword=product_keyword)
                result["price_analysis"] = price_result
                result["analysis_dimensions"].append("price")

                # 价格预测
                prediction = self.price_reference.predict_price(product_keyword, 3)
                if prediction.get("success"):
                    result["price_prediction"] = prediction
                    result["analysis_dimensions"].append("prediction")

                    # 购买时机建议
                    if prediction.get("buying_advice"):
                        insights.append({
                            "type": "timing",
                            "description": prediction["buying_advice"].get("recommendation", ""),
                            "details": prediction["buying_advice"].get("reason", "")
                        })

                # 预算匹配检查
                if budget and price_result.get("price_range"):
                    price_range = price_result["price_range"]
                    if budget < price_range["min"] * 0.8:
                        risk_factors.append({
                            "type": "budget",
                            "severity": "medium",
                            "description": "预算可能不足",
                            "details": f"预算{budget}元低于市场最低价{price_range['min']}元"
                        })
                    elif budget > price_range["max"] * 1.5:
                        insights.append({
                            "type": "budget",
                            "description": "预算充足，可考虑高端产品",
                            "details": f"预算{budget}元高于市场均价{price_range['avg']}元"
                        })
            except Exception as e:
                result["price_analysis"] = {"error": str(e)}

        # 4. 知识库查询
        if product_keyword and self.knowledge_base:
            try:
                knowledge = self.knowledge_base.query(f"{product_keyword} 采购建议")
                result["knowledge_tips"] = knowledge
                result["analysis_dimensions"].append("knowledge")
            except Exception as e:
                pass

        # 5. 计算综合风险评分
        result["risk_score"] = self._calculate_risk_score(risk_factors)
        result["risk_factors"] = risk_factors
        result["cross_insights"] = insights

        # 6. 生成综合建议
        result["overall_recommendation"] = self._generate_overall_recommendation(
            result, risk_factors, insights
        )

        return result

    def _check_requirement_contract_consistency(self,
                                                  requirement: str,
                                                  contract: str) -> Dict[str, Any]:
        """检查需求与合同的一致性"""
        inconsistencies = []

        # 检查关键规格是否在合同中体现
        key_specs = ["内存", "存储", "CPU", "处理器", "硬盘", "SSD", "HDD"]
        for spec in key_specs:
            if spec in requirement and spec not in contract:
                inconsistencies.append(f"需求中提到的{spec}规格未在合同中明确")

        # 检查数量一致性（简单关键词匹配）
        import re
        req_numbers = re.findall(r'\d+', requirement)
        contract_numbers = re.findall(r'\d+', contract)

        return {
            "consistent": len(inconsistencies) == 0,
            "inconsistencies": inconsistencies,
            "specs_checked": key_specs
        }

    def _calculate_risk_score(self, risk_factors: List[Dict]) -> int:
        """计算综合风险评分（0-100）"""
        if not risk_factors:
            return 10  # 低风险

        score = 0
        for factor in risk_factors:
            severity = factor.get("severity", "low")
            if severity == "high":
                score += 30
            elif severity == "medium":
                score += 15
            else:
                score += 5

        return min(score, 100)

    def _generate_overall_recommendation(self,
                                          analysis_result: Dict[str, Any],
                                          risk_factors: List[Dict],
                                          insights: List[Dict]) -> Dict[str, Any]:
        """生成综合采购建议"""
        risk_score = analysis_result.get("risk_score", 0)

        if risk_score >= 60:
            return {
                "action": "暂停采购",
                "priority": "紧急",
                "summary": "存在较高风险，建议先解决以下问题",
                "action_items": [f["description"] for f in risk_factors],
                "next_steps": [
                    "完善需求文档",
                    "重新审核合同条款",
                    "重新评估预算"
                ]
            }
        elif risk_score >= 30:
            return {
                "action": "谨慎推进",
                "priority": "高",
                "summary": "存在一定风险，建议关注以下方面",
                "action_items": [f["description"] for f in risk_factors] +
                               [i["description"] for i in insights],
                "next_steps": [
                    "核实关键条款",
                    "对比多个供应商报价",
                    "考虑价格趋势"
                ]
            }
        else:
            return {
                "action": "可以推进",
                "priority": "正常",
                "summary": "风险较低，可以按计划进行采购",
                "action_items": [i["description"] for i in insights] if insights else ["无特别注意事项"],
                "next_steps": [
                    "完成最终审批",
                    "准备合同签署",
                    "安排交付验收"
                ]
            }

    def _analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """分析需求的完整性和合理性"""
        has_memory = "内存" in requirements or "RAM" in requirements.upper()
        has_storage = "存储" in requirements or "硬盘" in requirements or "SSD" in requirements.upper() or "HDD" in requirements.upper()
        has_budget = "预算" in requirements

        score = 0
        suggestions = []

        if has_memory:
            score += 30
        else:
            suggestions.append("建议明确内存容量要求")

        if has_storage:
            score += 30
        else:
            suggestions.append("建议明确存储容量和类型")

        if has_budget:
            score += 40
        else:
            suggestions.append("建议明确预算范围")

        return {
            "completeness_score": score,
            "has_memory": has_memory,
            "has_storage": has_storage,
            "has_budget": has_budget,
            "suggestions": suggestions
        }

    def _generate_synthesis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合分析"""
        requirement_score = analysis_result["requirement_analysis"]["completeness_score"]
        price_options = len(analysis_result.get("price_references", []))

        # 考虑价格预测
        prediction = analysis_result.get("price_prediction", {})
        trend = prediction.get("overall_trend", {}).get("direction", "未知")

        if requirement_score >= 80 and price_options >= 3:
            status = "需求明确，选择丰富"
            action = "可以进行详细比价和方案评估"
        elif requirement_score >= 60:
            status = "需求基本明确"
            action = "建议补充部分细节后进一步分析"
        else:
            status = "需求需要完善"
            action = "请先完善需求规格"

        # 添加价格趋势建议
        if trend == "下降":
            action += "；当前价格呈下降趋势，可适当延后采购"
        elif trend == "上升":
            action += "；当前价格呈上升趋势，建议尽快完成采购"

        return {
            "status": status,
            "recommended_action": action,
            "priority": "高" if requirement_score < 60 else "中",
            "price_trend": trend
        }

    def _generate_recommendation(self, price_analysis: Dict[str, Any], knowledge: str) -> Dict[str, Any]:
        """生成购买建议"""
        assessment = price_analysis.get("assessment", "")

        if "合理" in assessment:
            return {
                "action": "建议采购",
                "priority": "正常",
                "notes": "价格处于合理区间"
            }
        elif "偏低" in assessment:
            return {
                "action": "谨慎采购",
                "priority": "高",
                "notes": "价格偏低，请核实产品质量和服务条款"
            }
        else:  # 偏高
            return {
                "action": "建议议价",
                "priority": "中",
                "notes": "价格偏高，建议与供应商协商降价"
            }
