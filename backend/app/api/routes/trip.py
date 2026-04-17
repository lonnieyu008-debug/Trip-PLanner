"""旅行规划API路由（LangGraph 版）"""

from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_graph import plan_trip_with_graph, get_trip_graph

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,使用 LangGraph 多智能体并行生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """
    生成旅行计划（LangGraph 版）

    Args:
        request: 旅行请求参数

    Returns:
        旅行计划响应
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"   模式: {'编辑行程' if request.existing_plan else '新建规划'}")
        if request.edit_instruction:
            print(f"   修改意图: {request.edit_instruction}")
        print(f"{'='*60}\n")

        # 使用 LangGraph 生成旅行计划（景点/天气/酒店并行执行）
        trip_plan = await plan_trip_with_graph(request)

        print("✅ 旅行计划生成成功,准备返回响应\n")

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )

    except Exception as e:
        print(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        get_trip_graph()  # 触发图的初始化，验证构建正常
        return {
            "status": "healthy",
            "service": "trip-planner",
            "engine": "LangGraph",
            "nodes": ["attraction_node", "weather_node", "hotel_node", "planner_node"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )

