from typing import Any, Dict

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.analysis import AnalysisWorkflowRequest
from app.services.analysis_workflow import AnalysisWorkflowService

router = APIRouter()
workflow_service = AnalysisWorkflowService()


@router.post("/workflow")
async def run_analysis_workflow(
    request: AnalysisWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = request.model_dump()
    result = workflow_service.run_workflow(current_user, **payload)

    history = workflow_service.create_history(
        db=db,
        user_id=current_user.id,
        template_type=request.template_type,
        input_payload=payload,
        result_payload=result,
        risk_score=result["risk_score"],
    )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                **result,
                "history_id": history.id,
            },
        },
    )


@router.get("/history")
async def get_analysis_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records, total = workflow_service.list_history(db, current_user, page, page_size)
    data = [workflow_service.decode_history_json(record) for record in records]

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": data,
            "page": page,
            "page_size": page_size,
            "total": total,
        },
    )


@router.post("/history/{history_id}/reuse")
async def reuse_analysis_history(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = workflow_service.get_history(db, current_user, history_id)
    if not history:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "分析历史不存在或无权访问"},
        )

    source = workflow_service.decode_history_json(history)
    source_input: Dict[str, Any] = source["input_payload"]
    result = workflow_service.run_workflow(current_user, **source_input)

    new_history = workflow_service.create_history(
        db=db,
        user_id=current_user.id,
        template_type=source_input.get("template_type"),
        input_payload=source_input,
        result_payload=result,
        risk_score=result["risk_score"],
    )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                **result,
                "history_id": new_history.id,
            },
        },
    )
