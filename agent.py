import os
import json
from typing import Annotated, TypedDict, List, Union
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

# Import tools từ file đã viết
from tools.car_tools import get_vehicle_data, calculate_loan_plan, find_charging_stations, calculate_tco_comparison, book_test_drive

load_dotenv()

# Định nghĩa Tools cho Agent
@tool
def tool_get_vehicle_data(model_id: str):
    """Truy vấn thông số kỹ thuật và giá bán của các dòng xe VinFast (VF3, VF5, VF6, VF7, VF8, VF9)."""
    return get_vehicle_data(model_id)

@tool
def tool_calculate_loan(model_id: str, version: str, loan_percentage: float, duration_months: int, bank_id: str = "vietcombank"):
    """Tính toán phương án trả góp hàng tháng (số tiền trả trước, gốc lãi hàng tháng)."""
    return calculate_loan_plan(model_id, version, loan_percentage, duration_months, bank_id)

@tool
def tool_calculate_tco(model_id: str, version: str, monthly_km: float = 1500):
    """So sánh tổng chi phí sở hữu (TCO) giữa xe điện VinFast và xe xăng tương đương trong 1 tháng/năm."""
    return calculate_tco_comparison(model_id, version, monthly_km)

@tool
def tool_book_test_drive(name: str, phone: str, model_id: str, showroom_id: str, time_slot: str):
    """Đặt lịch lái thử xe tại showroom VinFast."""
    return book_test_drive(name, phone, model_id, showroom_id, time_slot)

tools = [tool_get_vehicle_data, tool_calculate_loan, tool_find_charging_stations, tool_calculate_tco, tool_book_test_drive]
tool_node = ToolNode(tools)

# Cấu hình Model (Mặc định dùng Gemini 1.5 Flash qua OpenAI interface nếu có API Key)
# Hoặc bạn có thể đổi sang model khác tùy ý
model = ChatOpenAI(model="gemini-1.5-flash", temperature=0).bind_tools(tools)

# Định nghĩa Trạng thái (State)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# Logic của Agent
def call_model(state: AgentState):
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "continue"
    return "end"

# Node ghi log Signal (Data Flywheel)
def log_signal(state: AgentState):
    messages = state['messages']
    last_user_message = next((m.content for m in reversed(messages) if isinstance(m, HumanMessage)), "")
    last_ai_response = next((m.content for m in reversed(messages) if isinstance(m, AIMessage)), "")
    
    # Logic đơn giản để phân loại Signal
    signal = "NEUTRAL"
    if any(word in last_user_message.lower() for word in ["sai", "nhầm", "không đúng", "tính lại"]):
        signal = "USER_CORRECTION"
    elif any(word in last_user_message.lower() for word in ["cảm ơn", "tốt", "hay quá", "ưng"]):
        signal = "POSITIVE_FEEDBACK"
    
    # Ghi vào file signals.log
    log_entry = {
        "user_query": last_user_message,
        "ai_response": last_ai_response,
        "signal": signal
    }
    
    log_path = os.path.join(os.path.dirname(__file__), "data", "signals.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
    return state

# Xây dựng Graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_node("logger", log_signal)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": "logger"
    }
)
workflow.add_edge("action", "agent")
workflow.add_edge("logger", END)

# Compile Agent
vssa_agent = workflow.compile()

# System Prompt chuyên nghiệp
SYSTEM_PROMPT = """Bạn là VinFast Smart Sales Agent (VSSA) - Chuyên gia tư vấn xe điện VinFast.
Nhiệm vụ của bạn:
1. Tư vấn dòng xe phù hợp dựa trên ngân sách và nhu cầu (số chỗ ngồi, loại xe).
2. Lập phương án tài chính chi tiết khi khách có nhu cầu vay vốn.
3. So sánh chi phí (TCO) giữa xe điện và xe xăng để thuyết phục khách hàng "Sống Xanh".
4. Chỉ đường, tìm trạm sạc và đặt lịch lái thử tại Showroom.

Phong cách: Chuyên nghiệp, lịch sự, luôn hỗ trợ khách hàng hết mình. 
Nếu khách đang rất quan tâm đến một mẫu xe, hãy chủ động mời họ sử dụng `tool_book_test_drive` để trải nghiệm thực tế.

Nếu thông tin khách hỏi nằm ngoài hiểu biết (như thông tin chi tiết nội thất xe cụ thể mà tool không trả về), hãy báo: "Thông tin này tôi chưa rõ. Hãy trao đổi với saler để được tư vấn kỹ hơn"."""

def get_response(user_input: str, chat_history: List[BaseMessage] = []):
    initial_messages = [SystemMessage(content=SYSTEM_PROMPT)] + chat_history + [HumanMessage(content=user_input)]
    output = vssa_agent.invoke({"messages": initial_messages})
    return output['messages'][-1].content

if __name__ == "__main__":
    # Test nhanh
    query = "Tôi có 900 triệu, muốn mua xe gia đình gầm cao. Bạn tư vấn xe nào và tính trả góp 80% trong 5 năm hộ tôi với ngân hàng Vietcombank."
    print("User:", query)
    print("VSSA:", get_response(query))
