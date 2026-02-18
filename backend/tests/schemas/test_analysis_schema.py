from app.schemas.analysis import AnalysisWorkflowRequest, AnalysisWorkflowResponse


def test_analysis_workflow_request_defaults():
    payload = AnalysisWorkflowRequest()
    assert payload.requirement_text is None
    assert payload.contract_text is None
    assert payload.product_keyword is None
    assert payload.template_type is None


def test_analysis_workflow_response_has_evidence():
    response = AnalysisWorkflowResponse(
        success=True,
        summary={"overall_recommendation": "ok"},
        risk_score=30,
        evidence={"rules": [], "price_sources": [], "contract_clauses": []},
        history_id=1,
    )
    assert response.success is True
    assert response.history_id == 1
