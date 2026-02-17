from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Optional
from app.agents.price_reference import PriceReference

router = APIRouter()
price_ref = PriceReference()


@router.get("/price-reference")
async def get_price_reference(
    category: Optional[str] = Query(None, description="商品分类"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格")
):
    """查询价格参考信息"""
    try:
        result = price_ref.query_price(category, keyword, min_price, max_price)
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


@router.get("/price-reference/categories")
async def get_categories():
    """获取所有价格分类"""
    try:
        categories = price_ref._get_categories()
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": categories
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


@router.get("/price-reference/product/{product_name}")
async def get_product_price(product_name: str):
    """根据产品名称获取价格信息"""
    try:
        result = price_ref.get_price_by_name(product_name)
        if result:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": result
                }
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "未找到该产品的价格信息"
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


@router.post("/price-reference/analyze")
async def analyze_price(product_name: str, quoted_price: float):
    """分析报价合理性"""
    try:
        result = price_ref.analyze_price(product_name, quoted_price)
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


@router.get("/price-reference/predict")
async def predict_price(
    keyword: str = Query(..., description="产品关键词"),
    months: int = Query(3, description="预测未来月数", ge=1, le=12)
):
    """
    预测价格趋势

    基于历史数据使用线性回归和季节性分析预测未来价格走势。

    Returns:
        - predictions: 各产品的预测价格
        - overall_trend: 整体趋势判断
        - buying_advice: 采购时机建议
    """
    try:
        result = price_ref.predict_price(keyword, months)
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


@router.get("/price-reference/market-insights")
async def get_market_insights(category: Optional[str] = Query(None, description="商品分类")):
    """
    获取市场洞察

    分析各类产品的价格走势，提供采购建议。

    Returns:
        - categories: 各分类统计
        - insights: 趋势洞察和建议
    """
    try:
        result = price_ref.get_market_insights(category)
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
