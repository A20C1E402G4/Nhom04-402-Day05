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

# Load environment variables từ file .env cùng thư mục với agent.py
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

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

@tool
def tool_find_charging_stations(origin: str, destination: str):
    """Tìm kiếm danh sách các trạm sạc VinFast trên lộ trình của khách hàng."""
    return find_charging_stations(origin, destination)

tools = [tool_get_vehicle_data, tool_calculate_loan, tool_find_charging_stations, tool_calculate_tco, tool_book_test_drive]
tool_node = ToolNode(tools)

# --- Khởi tạo Agent (Lazy Loading) ---
_vssa_agent = None

def get_agent():
    global _vssa_agent
    if _vssa_agent is not None:
        return _vssa_agent
    
    # Kiểm tra API Key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        return None  # Không có key thì không khởi tạo
    
    # Cấu hình Model
    try:
        model = ChatOpenAI(model="gemini-1.5-flash", temperature=0).bind_tools(tools)
        
        # Xây dựng Graph
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", lambda state: {"messages": [model.invoke(state['messages'])]})
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
        
        _vssa_agent = workflow.compile()
        return _vssa_agent
    except Exception as e:
        print(f"Lỗi khởi tạo Agent: {e}")
        return None

# --- Logic chính ---

def get_response(user_input: str, chat_history: List[BaseMessage] = []):
    agent = get_agent()
    
    if agent is None:
        # Chế độ Mock Demo khi không có API Key
        return f"[MOCK DEMO] Chào bạn! Tôi đang chạy ở chế độ Demo (thiếu API Key).\n\nBạn vừa hỏi: '{user_input}'\n\nKhi có API Key, tôi sẽ sử dụng LangGraph để truy vấn dữ liệu xe VinFast, tính toán TCO và đặt lịch lái thử cho bạn một cách chuyên nghiệp!"
    
    initial_messages = [SystemMessage(content=SYSTEM_PROMPT)] + chat_history + [HumanMessage(content=user_input)]
    try:
        output = agent.invoke({"messages": initial_messages})
        return output['messages'][-1].content
    except Exception as e:
        return f"Lỗi khi thực thi Agent: {e}"

if __name__ == "__main__":
    # Test nhanh
    query = "Tôi có 900 triệu, muốn mua xe gia đình gầm cao. Bạn tư vấn xe nào và tính trả góp 80% trong 5 năm hộ tôi với ngân hàng Vietcombank."
    print("User:", query)
    print("VSSA:", get_response(query))
