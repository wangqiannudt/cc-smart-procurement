import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.agents.contract_analyzer import ContractAnalyzer
from app.agents.price_reference import PriceReference
from app.agents.requirement_reviewer import RequirementReviewer
from app.models.analysis_history import AnalysisHistory


class AnalysisWorkflowService:
    """Orchestrates requirement/price/contract analysis and produces evidence-backed output."""

    def __init__(self):
        self.requirement_reviewer = RequirementReviewer()
        self.price_reference = PriceReference()
        self.contract_analyzer = ContractAnalyzer()

    def run_workflow(
        self,
        user: Any,
        requirement_text: Optional[str] = None,
        contract_text: Optional[str] = None,
        product_keyword: Optional[str] = None,
        budget: Optional[float] = None,
        template_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        requirement_result = None
        price_result = None
        contract_result = None

        evidence = {
            "rules": [],
            "price_sources": [],
            "contract_clauses": [],
        }

        if requirement_text:
            requirement_result = self.requirement_reviewer.review(requirement_text)
            for issue in requirement_result.get("issues", [])[:20]:
                evidence["rules"].append(
                    {
                        "rule_id": issue.get("rule_id"),
                        "field": issue.get("field_id"),
                        "message": issue.get("message"),
                        "priority": issue.get("priority") or issue.get("level"),
                    }
                )

        if product_keyword:
            price_result = self.price_reference.query_price(keyword=product_keyword)
            for record in price_result.get("records", [])[:10]:
                evidence["price_sources"].append(
                    {
                        "product": record.get("name"),
                        "source": record.get("source"),
                        "date": record.get("date"),
                        "price": record.get("price"),
                    }
                )
            if budget and price_result.get("price_range"):
                price_min = price_result["price_range"].get("min", 0)
                if price_min and budget < price_min:
                    evidence["price_sources"].append(
                        {
                            "product": "budget-check",
                            "source": "system",
                            "date": None,
                            "price": budget,
                            "note": "budget lower than current minimum reference price",
                        }
                    )

        if contract_text:
            contract_result = self.contract_analyzer.analyze(contract_text)
            for risk in contract_result.get("risks", [])[:20]:
                evidence["contract_clauses"].append(
                    {
                        "clause_type": risk.get("level"),
                        "excerpt": risk.get("sentence"),
                        "keyword": risk.get("keyword"),
                    }
                )

        risk_score = self._calculate_risk_score(requirement_result, contract_result, budget, price_result)
        summary = self._build_summary(
            risk_score=risk_score,
            requirement_result=requirement_result,
            contract_result=contract_result,
            price_result=price_result,
            template_type=template_type,
        )

        return {
            "summary": summary,
            "risk_score": risk_score,
            "evidence": evidence,
            "requirement_result": requirement_result,
            "price_result": price_result,
            "contract_result": contract_result,
        }

    def create_history(
        self,
        db: Session,
        user_id: int,
        template_type: Optional[str],
        input_payload: Dict[str, Any],
        result_payload: Dict[str, Any],
        risk_score: int,
    ) -> AnalysisHistory:
        history = AnalysisHistory(
            user_id=user_id,
            template_type=template_type,
            input_payload=json.dumps(input_payload, ensure_ascii=False),
            result_payload=json.dumps(result_payload, ensure_ascii=False),
            risk_score=risk_score,
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    def list_history(self, db: Session, user: Any, page: int = 1, page_size: int = 10):
        query = db.query(AnalysisHistory)
        if getattr(user, "role", "") != "admin":
            query = query.filter(AnalysisHistory.user_id == user.id)

        total = query.count()
        records = (
            query.order_by(AnalysisHistory.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return records, total

    def get_history(self, db: Session, user: Any, history_id: int) -> Optional[AnalysisHistory]:
        record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
        if not record:
            return None
        if getattr(user, "role", "") == "admin":
            return record
        if record.user_id != user.id:
            return None
        return record

    @staticmethod
    def decode_history_json(record: AnalysisHistory) -> Dict[str, Any]:
        input_payload = json.loads(record.input_payload) if record.input_payload else {}
        result_payload = json.loads(record.result_payload) if record.result_payload else {}
        return {
            "id": record.id,
            "template_type": record.template_type,
            "risk_score": record.risk_score,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "input_payload": input_payload,
            "result_payload": result_payload,
        }

    @staticmethod
    def _calculate_risk_score(
        requirement_result: Optional[Dict[str, Any]],
        contract_result: Optional[Dict[str, Any]],
        budget: Optional[float],
        price_result: Optional[Dict[str, Any]],
    ) -> int:
        score = 0

        if requirement_result:
            req_score = requirement_result.get("completeness_score", 100)
            if req_score < 80:
                score += 20
            if req_score < 60:
                score += 20
            score += min(requirement_result.get("error_count", 0) * 5, 20)

        if contract_result:
            high = contract_result.get("risk_summary", {}).get("高风险", 0)
            medium = contract_result.get("risk_summary", {}).get("中风险", 0)
            score += min(high * 15, 45)
            score += min(medium * 5, 20)

        if budget is not None and price_result and price_result.get("price_range"):
            min_price = price_result["price_range"].get("min", 0)
            max_price = price_result["price_range"].get("max", 0)
            if min_price and budget < min_price:
                score += 15
            if max_price and budget > max_price * 2:
                score += 10

        return min(score, 100)

    @staticmethod
    def _build_summary(
        risk_score: int,
        requirement_result: Optional[Dict[str, Any]],
        contract_result: Optional[Dict[str, Any]],
        price_result: Optional[Dict[str, Any]],
        template_type: Optional[str],
    ) -> Dict[str, Any]:
        if risk_score >= 60:
            recommendation = "暂停采购并先处理高风险项"
            priority = "high"
        elif risk_score >= 30:
            recommendation = "谨慎推进，补充关键证据后决策"
            priority = "medium"
        else:
            recommendation = "可推进采购流程"
            priority = "low"

        return {
            "overall_recommendation": recommendation,
            "priority": priority,
            "template_type": template_type,
            "dimensions": {
                "requirements": bool(requirement_result),
                "price": bool(price_result),
                "contract": bool(contract_result),
            },
        }
