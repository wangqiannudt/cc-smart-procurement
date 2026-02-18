from app.services.analysis_workflow import AnalysisWorkflowService
from app.models.analysis_history import AnalysisHistory


class DummyUser:
    id = 123


def test_workflow_returns_structured_payload():
    service = AnalysisWorkflowService()

    result = service.run_workflow(
        user=DummyUser(),
        requirement_text="采购10台服务器，预算20万",
        contract_text="甲方应在7日内付款，违约责任由乙方承担",
        product_keyword="服务器",
        budget=200000,
        template_type="server",
    )

    assert "summary" in result
    assert "risk_score" in result
    assert "evidence" in result
    assert isinstance(result["risk_score"], int)


def test_calculate_risk_score_detects_contract_and_requirement_risks():
    score = AnalysisWorkflowService._calculate_risk_score(
        requirement_result={"completeness_score": 50, "error_count": 2},
        contract_result={"risk_summary": {"高风险": 1, "中风险": 2}},
        budget=10000,
        price_result={"price_range": {"min": 20000, "max": 50000}},
    )
    assert score >= 50


def test_decode_history_json_parses_payload():
    record = AnalysisHistory(
        id=7,
        template_type="server",
        risk_score=22,
        input_payload='{"product_keyword":"服务器"}',
        result_payload='{"summary":{"overall_recommendation":"ok"}}',
    )
    decoded = AnalysisWorkflowService.decode_history_json(record)
    assert decoded["id"] == 7
    assert decoded["input_payload"]["product_keyword"] == "服务器"
    assert decoded["result_payload"]["summary"]["overall_recommendation"] == "ok"
