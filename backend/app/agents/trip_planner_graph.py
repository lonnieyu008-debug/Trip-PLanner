"""
LangGraph 多智能体旅行规划图

图结构：
    START
      │
    router_node  ← 意图识别，条件路由
      │
      ├─[new_plan]──┬── attraction_node ──┐
      │             ├── weather_node    ──┼──► planner_node ──► END
      │             └── hotel_node     ──┘
      │                (三个节点并行执行)
      │
      └─[edit_plan]── edit_node ──► END

核心改进（相比旧的 HelloAgents 版本）：
1. 景点/天气/酒店三个 Agent 并行执行，速度更快
2. 使用 MCP 标准协议调用高德地图工具，更可靠
3. 有真正的状态管理（TripState），不靠字符串拼接
4. 条件路由节点（router_node）：基于意图动态分发至新建/编辑两条子图分支
"""

import json
from typing import TypedDict, Optional
from datetime import datetime, timedelta

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END

from ..services.llm_service_lg import get_llm_lg, get_llm_tool
from ..services.amap_tools import get_mcp_client
from ..models.schemas import (
    TripRequest, TripPlan, DayPlan, Attraction, Meal,
    WeatherInfo, Location, Hotel, Budget
)

# ============ 1. 定义状态 ============

class TripState(TypedDict):
    """图的共享状态，在所有节点之间传递"""
    request: TripRequest            # 用户输入的旅行请求
    intent: str                     # router_node 识别的意图："new_plan" 或 "edit_plan"
    attractions: str                # 景点 Agent 的搜索结果
    weather: str                    # 天气 Agent 的查询结果
    hotels: str                     # 酒店 Agent 的搜索结果
    final_plan: Optional[TripPlan]  # 规划 Agent 生成的最终计划


# ============ 2. 提示词 ============

ATTRACTION_SYSTEM = """你是景点搜索专家。使用 amap_maps_text_search 工具搜索景点。
搜索完成后，整理出景点名称、地址、坐标、评分等关键信息。"""

WEATHER_SYSTEM = """你是天气查询专家。使用 amap_maps_weather 工具查询天气预报。
返回每天的天气状况、温度、风向风力等信息。"""

HOTEL_SYSTEM = """你是酒店推荐专家。使用 amap_maps_text_search 工具搜索酒店。
整理出酒店名称、地址、坐标、价格范围、评分等信息。"""

PLANNER_SYSTEM = """你是行程规划专家。根据景点、天气、酒店信息生成完整旅行计划。

请严格按照以下 JSON 格式返回（不要添加任何额外文字）：
```json
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 116.397128, "latitude": 39.916527},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "详细地址",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "visit_duration": 120,
          "description": "景点描述",
          "category": "景点类别",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "早餐推荐", "description": "描述", "estimated_cost": 30},
        {"type": "lunch", "name": "午餐推荐", "description": "描述", "estimated_cost": 50},
        {"type": "dinner", "name": "晚餐推荐", "description": "描述", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
```

要求：每天2-3个景点，早中晚三餐，温度用纯数字。"""

EDIT_SYSTEM = """你是行程编辑专家。用户已有一份旅行计划，需要你根据他的修改意图做局部调整。

要求：
1. 只修改用户提到的部分，其余内容完全保持不变
2. 输出的 JSON 结构必须与输入完全一致
3. 严格按照下方格式返回完整行程 JSON，不要添加任何额外文字

```json
{
  "city": "...",
  "start_date": "...",
  "end_date": "...",
  "days": [...],
  "weather_info": [...],
  "overall_suggestions": "...",
  "budget": {...}
}
```"""


# ============ 3. 节点函数 ============

async def _run_agent_with_tools(system_prompt: str, user_query: str) -> str:
    """
    通用的带工具调用的 Agent 执行逻辑（ReAct 循环）
    供景点/天气/酒店三个节点复用。

    langchain-mcp-adapters >= 0.1.0：不再用 async with，
    直接 await client.get_tools() 获取工具列表。
    """
    client = get_mcp_client()
    tools = await client.get_tools()      # 新 API：直接 await
    llm = get_llm_tool().bind_tools(tools)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query),
    ]

    response = None
    # ReAct 循环：最多 3 轮工具调用
    for _ in range(3):
        response = await llm.ainvoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break  # 没有工具调用，输出最终答案

        # 执行所有工具调用
        for tool_call in response.tool_calls:
            # 在 tools 列表里找到对应工具并调用
            matched = next((t for t in tools if t.name == tool_call["name"]), None)
            if matched:
                tool_result = await matched.ainvoke(tool_call["args"])
            else:
                tool_result = f"未找到工具: {tool_call['name']}"
            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

    return response.content if response else "未获取到结果"


def _route_intent(state: TripState):
    """
    条件路由函数：根据 intent 字段决定走哪条分支。
    - 返回列表 → LangGraph 并行启动列表中所有节点（Fan-out）
    - 返回字符串 → 只走那一个节点
    """
    intent = state.get("intent", "new_plan")
    if intent == "new_plan":
        return ["attraction_node", "weather_node", "hotel_node"]
    else:
        return "edit_node"


async def router_node(state: TripState) -> dict:
    """
    路由节点：识别本次请求的意图，写入 intent 字段。
    - 有 existing_plan → edit_plan（行程编辑分支）
    - 无 existing_plan → new_plan（新建规划分支）

    这里用最简单的规则判断，不消耗 LLM token。
    """
    request = state["request"]
    if request.existing_plan and request.edit_instruction:
        intent = "edit_plan"
        print(f"[路由节点] 意图识别：edit_plan（修改指令：{request.edit_instruction[:30]}...）")
    else:
        intent = "new_plan"
        print(f"[路由节点] 意图识别：new_plan（目的地：{request.city}）")
    return {"intent": intent}


async def attraction_node(state: TripState) -> dict:
    """景点搜索节点"""
    request = state["request"]
    print(f"[景点节点] 开始搜索 {request.city} 的景点...")

    keywords = request.preferences[0] if request.preferences else "旅游景点"
    query = f"请搜索{request.city}的{keywords}，找出适合旅游的景点，并整理信息。"

    result = await _run_agent_with_tools(ATTRACTION_SYSTEM, query)
    print(f"[景点节点] 完成，结果长度: {len(result)} 字符")
    return {"attractions": result}


async def weather_node(state: TripState) -> dict:
    """天气查询节点"""
    request = state["request"]
    print(f"[天气节点] 开始查询 {request.city} 的天气...")

    query = f"请查询{request.city}从{request.start_date}到{request.end_date}期间的天气预报。"

    result = await _run_agent_with_tools(WEATHER_SYSTEM, query)
    print(f"[天气节点] 完成，结果长度: {len(result)} 字符")
    return {"weather": result}


async def hotel_node(state: TripState) -> dict:
    """酒店搜索节点"""
    request = state["request"]
    print(f"[酒店节点] 开始搜索 {request.city} 的 {request.accommodation}...")

    query = f"请搜索{request.city}的{request.accommodation}，找出位置好、评分高的住宿选择。"

    result = await _run_agent_with_tools(HOTEL_SYSTEM, query)
    print(f"[酒店节点] 完成，结果长度: {len(result)} 字符")
    return {"hotels": result}


async def planner_node(state: TripState) -> dict:
    """规划节点：整合三个节点的结果，生成完整旅行计划"""
    request = state["request"]
    print(f"[规划节点] 开始整合信息生成旅行计划...")

    query = f"""请根据以下信息生成{request.city}的{request.travel_days}天旅行计划：

基本信息：
- 城市：{request.city}
- 日期：{request.start_date} 至 {request.end_date}
- 交通：{request.transportation}
- 住宿：{request.accommodation}
- 偏好：{', '.join(request.preferences) if request.preferences else '无'}
{f'- 额外要求：{request.free_text_input}' if request.free_text_input else ''}

景点信息：
{state.get('attractions', '暂无景点信息')}

天气信息：
{state.get('weather', '暂无天气信息')}

酒店信息：
{state.get('hotels', '暂无酒店信息')}"""

    llm = get_llm_lg()
    messages = [
        SystemMessage(content=PLANNER_SYSTEM),
        HumanMessage(content=query),
    ]
    response = await llm.ainvoke(messages)

    trip_plan = _parse_plan(response.content, request)
    print(f"[规划节点] 完成，生成了 {len(trip_plan.days)} 天的行程")
    return {"final_plan": trip_plan}


async def edit_node(state: TripState) -> dict:
    """
    行程编辑节点：不调用任何工具，纯 LLM 推理。
    接收已有行程 JSON + 用户修改意图，输出修改后的完整行程。
    """
    request = state["request"]
    print(f"[编辑节点] 开始处理修改请求：{request.edit_instruction}")

    # 把已有行程 dict 序列化成格式化 JSON 字符串，让 LLM 能看懂
    existing_plan_json = json.dumps(request.existing_plan, ensure_ascii=False, indent=2)

    query = f"""以下是用户当前的旅行计划（JSON 格式）：

{existing_plan_json}

用户的修改要求：{request.edit_instruction}

请根据修改要求调整行程，返回完整的修改后行程 JSON。"""

    llm = get_llm_lg()
    messages = [
        SystemMessage(content=EDIT_SYSTEM),
        HumanMessage(content=query),
    ]
    response = await llm.ainvoke(messages)

    # 复用 _parse_plan 解析输出，解析失败时用原行程兜底（不丢数据）
    try:
        trip_plan = _parse_plan(response.content, request)
    except Exception:
        print(f"[编辑节点] 解析失败，保留原行程")
        trip_plan = TripPlan(**request.existing_plan)

    print(f"[编辑节点] 完成")
    return {"final_plan": trip_plan}


# ============ 4. 辅助函数 ============

def _parse_plan(text: str, request: TripRequest) -> TripPlan:
    """从 LLM 输出中提取 JSON 并解析为 TripPlan"""
    try:
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_str = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            json_str = text[start:end].strip()
        elif "{" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            json_str = text[start:end]
        else:
            raise ValueError("响应中未找到 JSON")

        data = json.loads(json_str)
        return TripPlan(**data)

    except Exception as e:
        print(f"[规划节点] JSON 解析失败: {e}，使用备用计划")
        return _fallback_plan(request)


def _fallback_plan(request: TripRequest) -> TripPlan:
    """解析失败时的备用计划"""
    start = datetime.strptime(request.start_date, "%Y-%m-%d")
    days = []
    for i in range(request.travel_days):
        current = start + timedelta(days=i)
        days.append(DayPlan(
            date=current.strftime("%Y-%m-%d"),
            day_index=i,
            description=f"第{i+1}天行程",
            transportation=request.transportation,
            accommodation=request.accommodation,
            attractions=[
                Attraction(
                    name=f"{request.city}景点{j+1}",
                    address=f"{request.city}市",
                    location=Location(longitude=116.4 + j * 0.01, latitude=39.9 + j * 0.01),
                    visit_duration=120,
                    description=f"{request.city}著名景点",
                    category="景点",
                )
                for j in range(2)
            ],
            meals=[
                Meal(type="breakfast", name="当地早餐", description="特色早餐"),
                Meal(type="lunch", name="当地午餐", description="特色午餐"),
                Meal(type="dinner", name="当地晚餐", description="特色晚餐"),
            ],
        ))

    # 计算一个简单的默认 budget
    default_budget = Budget(
        total_attractions=0,
        total_hotels=0,
        total_meals=request.travel_days * 160,  # 按每天160元估算
        total_transportation=200,
        total=request.travel_days * 160 + 200,
    )

    return TripPlan(
        city=request.city,
        start_date=request.start_date,
        end_date=request.end_date,
        days=days,
        weather_info=[],
        overall_suggestions=f"欢迎来到{request.city}！建议提前查看各景点开放时间。",
        budget=default_budget,
    )


# ============ 5. 构建图 ============

def build_trip_graph():
    """构建并编译旅行规划图（含条件路由）"""
    graph = StateGraph(TripState)

    # 注册所有节点
    graph.add_node("router_node", router_node)
    graph.add_node("attraction_node", attraction_node)
    graph.add_node("weather_node", weather_node)
    graph.add_node("hotel_node", hotel_node)
    graph.add_node("planner_node", planner_node)
    graph.add_node("edit_node", edit_node)

    # START → router_node（所有请求先过路由）
    graph.add_edge(START, "router_node")

    # router_node → 条件分支
    # new_plan：返回列表，LangGraph 自动并行启动三个节点（Fan-out）
    # edit_plan：返回字符串，直接进 edit_node
    graph.add_conditional_edges("router_node", _route_intent)

    # new_plan 分支：三个并行节点完成后 → planner_node（LangGraph 自动 join）
    graph.add_edge("attraction_node", "planner_node")
    graph.add_edge("weather_node", "planner_node")
    graph.add_edge("hotel_node", "planner_node")

    # 两条分支最终都到 END
    graph.add_edge("planner_node", END)
    graph.add_edge("edit_node", END)

    return graph.compile()


# 编译好的图（单例）
_compiled_graph = None


def get_trip_graph():
    """获取编译好的图（单例）"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_trip_graph()
        print("✅ LangGraph 旅行规划图构建成功")
    return _compiled_graph


# ============ 6. 对外调用入口 ============

async def plan_trip_with_graph(request: TripRequest) -> TripPlan:
    """
    使用 LangGraph 生成旅行计划

    Args:
        request: 旅行请求（TripRequest）

    Returns:
        旅行计划（TripPlan）
    """
    graph = get_trip_graph()

    initial_state: TripState = {
        "request": request,
        "intent": "",               # 由 router_node 写入
        "attractions": "",
        "weather": "",
        "hotels": "",
        "final_plan": None,
    }

    print(f"\n{'='*60}")
    print(f"🚀 LangGraph 开始规划：{request.city} {request.travel_days}天")
    print(f"{'='*60}\n")

    final_state = await graph.ainvoke(initial_state)

    print(f"\n{'='*60}")
    print(f"✅ LangGraph 规划完成！")
    print(f"{'='*60}\n")

    return final_state["final_plan"]
