from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from app.agents.chat_agent import ChatAgent
from app.agents.agent_coordinator import AgentCoordinator

router = APIRouter()

# 创建聊天智能体实例
chat_agent = ChatAgent()
agent_coordinator = AgentCoordinator()


@router.post("/chat/conversation")
async def chat_conversation(request: Dict[str, Any]):
    """
    AI聊天对话接口

    Request body:
    {
        "message": "用户消息",
        "session_id": "可选，会话ID。如果不提供，将使用默认会话或创建新会话"
    }

    Returns:
    {
        "success": true,
        "data": {
            "response": "AI回复",
            "session_id": "会话ID",
            "suggested_actions": []
        }
    }
    """
    try:
        message = request.get("message", "")
        session_id = request.get("session_id")  # 可选的session_id

        if not message:
            raise HTTPException(status_code=400, detail="消息不能为空")

        # 处理聊天消息，支持多会话
        result = chat_agent.chat(message, session_id)

        # 生成建议操作
        suggested_actions = _generate_suggested_actions(message, result["response"])

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "response": result["response"],
                    "session_id": result["session_id"],
                    "suggested_actions": suggested_actions
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.post("/chat/new-session")
async def create_new_session():
    """
    创建新会话

    Returns:
    {
        "success": true,
        "data": {
            "session_id": "新会话ID"
        }
    }
    """
    try:
        session_id = chat_agent.create_new_session()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "session_id": session_id
                }
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    获取指定会话的对话历史

    Args:
        session_id: 会话ID

    Returns:
    {
        "success": true,
        "data": {
            "session_id": "会话ID",
            "history": [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }
    }
    """
    try:
        history = chat_agent.get_history(session_id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "session_id": session_id,
                    "history": history
                }
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """
    清空指定会话的历史

    Args:
        session_id: 会话ID
    """
    try:
        chat_agent.clear_session(session_id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"会话 {session_id} 已清空"
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.post("/chat/procurement-analysis")
async def procurement_analysis(request: Dict[str, Any]):
    """
    采购场景分析接口

    Request body:
    {
        "product_type": "产品类型",
        "requirements": "需求描述"
    }
    """
    try:
        product_type = request.get("product_type", "")
        requirements = request.get("requirements", "")

        if not product_type or not requirements:
            raise HTTPException(status_code=400, detail="产品类型和需求描述不能为空")

        # 调用协调器进行分析
        result = agent_coordinator.analyze_procurement_scenario(
            product_type=product_type,
            requirements=requirements
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@router.post("/chat/price-recommendation")
async def price_recommendation(request: Dict[str, Any]):
    """
    价格推荐接口

    Request body:
    {
        "product_name": "产品名称",
        "budget": 预算金额
    }
    """
    try:
        product_name = request.get("product_name", "")
        budget = request.get("budget", 0.0)

        if not product_name or budget <= 0:
            raise HTTPException(status_code=400, detail="产品名称和预算不能为空且预算必须大于0")

        result = agent_coordinator.get_recommendations(product_name, budget)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


def _generate_suggested_actions(message: str, response: str) -> list:
    """根据消息和回复生成建议操作"""
    actions = []

    message_lower = message.lower()

    # 关键词匹配生成建议
    if "需求" in message_lower or "采购" in message_lower or "规格" in message_lower:
        actions.append({
            "type": "navigate",
            "label": "需求审查",
            "path": "/requirements"
        })

    if "价格" in message_lower or "报价" in message_lower or "预算" in message_lower or "比价" in message_lower:
        actions.append({
            "type": "navigate",
            "label": "价格参考",
            "path": "/price"
        })

    if "合同" in message_lower or "条款" in message_lower or "协议" in message_lower:
        actions.append({
            "type": "navigate",
            "label": "合同分析",
            "path": "/contract"
        })

    if "服务器" in message_lower or "机架" in message_lower or "存储" in message_lower:
        actions.append({
            "type": "function",
            "label": "分析采购方案",
            "function": "analyze_procurement",
            "params": {
                "product_type": "服务器",
                "requirements": message
            }
        })

    if "供应商" in message_lower or "厂商" in message_lower:
        actions.append({
            "type": "function",
            "label": "供应商评估",
            "function": "evaluate_supplier",
            "params": {
                "query": message
            }
        })

    if len(actions) == 0:
        # 默认操作
        actions.append({
            "type": "navigate",
            "label": "返回首页",
            "path": "/"
        })
        actions.append({
            "type": "function",
            "label": "开始新对话",
            "function": "new_conversation",
            "params": {}
        })

    return actions


@router.post("/chat/comprehensive-analysis")
async def comprehensive_analysis(request: Dict[str, Any]):
    """
    跨智能体综合分析接口

    整合需求审查、合同分析、价格查询等多个智能体的分析结果。

    Request body:
    {
        "requirement_text": "需求文档文本（可选）",
        "contract_text": "合同文档文本（可选）",
        "product_keyword": "产品关键词（可选）",
        "budget": 预算金额（可选）
    }

    Returns:
    {
        "success": true,
        "data": {
            "analysis_dimensions": ["requirements", "contract", "price", ...],
            "risk_score": 0-100,
            "risk_factors": [...],
            "cross_insights": [...],
            "overall_recommendation": {...}
        }
    }
    """
    try:
        requirement_text = request.get("requirement_text")
        contract_text = request.get("contract_text")
        product_keyword = request.get("product_keyword")
        budget = request.get("budget")

        result = agent_coordinator.comprehensive_analysis(
            requirement_text=requirement_text,
            contract_text=contract_text,
            product_keyword=product_keyword,
            budget=budget
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )
