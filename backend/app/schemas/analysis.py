from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class AnalysisWorkflowRequest(BaseModel):
    requirement_text: Optional[str] = None
    contract_text: Optional[str] = None
    product_keyword: Optional[str] = None
    budget: Optional[float] = Field(None, ge=0)
    template_type: Optional[str] = None


class AnalysisWorkflowResponse(BaseModel):
    success: bool
    summary: Dict[str, Any]
    risk_score: int = Field(ge=0, le=100)
    evidence: Dict[str, List[Dict[str, Any]]]
    history_id: int
    requirement_result: Optional[Dict[str, Any]] = None
    price_result: Optional[Dict[str, Any]] = None
    contract_result: Optional[Dict[str, Any]] = None


class AnalysisHistoryItem(BaseModel):
    id: int
    template_type: Optional[str] = None
    risk_score: int
    created_at: Optional[str] = None
    input_payload: Dict[str, Any]
    result_payload: Dict[str, Any]


class AnalysisHistoryListResponse(BaseModel):
    success: bool
    data: List[AnalysisHistoryItem]
    page: int
    page_size: int
    total: int
