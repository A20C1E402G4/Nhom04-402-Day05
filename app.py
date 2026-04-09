import streamlit as st
from agent import get_response
from langchain_core.messages import HumanMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="VSSA - VinFast Smart Sales Agent", page_icon="⚡", layout="wide")

st.title("⚡ VSSA: VinFast Smart Sales Agent")
st.markdown("---")

# Kiểm tra xem có API Key chưa
if not os.getenv("OPENAI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    st.warning("⚠️ Chưa tìm thấy API Key (OpenAI hoặc Google). Hãy kiểm tra file `.env` để Agent có thể hoạt động.")

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar thông tin
with st.sidebar:
    st.image("https://vinfastauto.com/themes/custom/vinfast/logo.png", width=150)
    st.header("Về VSSA")
    st.info("VSSA là trợ lý AI thông minh giúp bạn tìm chiếc xe VinFast ưng ý nhất và lập kế hoạch tài chính chỉ trong 1 phút.")
    
    if st.button("Xóa lịch sử chat"):
        st.session_state.messages = []
        st.rerun()

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)

# Ô nhập chat
if prompt := st.chat_input("Hỏi tôi về xe VinFast hoặc gói trả góp..."):
    # Hiển thị tin nhắn user
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Chuyển lịch sử sang định dạng LangChain cho Agent
    chat_history = st.session_state.messages
    
    # Gọi Agent xử lý
    with st.chat_message("assistant"):
        with st.spinner("Đang suy luận..."):
            try:
                # Lấy message từ agent
                # Note: agent.py's get_response returns the content string
                # To handle structured tool output (like TCO tables), we might need to parse or rely on LLM formatting
                response = get_response(prompt, chat_history)
                
                # Hiển thị response
                st.markdown(response)
                
                # Lưu vào lịch sử
                st.session_state.messages.append(HumanMessage(content=prompt))
                st.session_state.messages.append(AIMessage(content=response))
                
                # Gợi ý xem file log nếu là developer
                with st.expander("Debug: Signals Log"):
                    log_path = os.path.join(os.path.dirname(__file__), "data", "signals.log")
                    if os.path.exists(log_path):
                        with open(log_path, "r", encoding="utf-8") as f:
                            st.text(f.readlines()[-1]) # Show last signal
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {str(e)}")

# Gợi ý nhanh
st.markdown("---")
st.caption("Câu hỏi gợi ý:")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Tư vấn xe cho gia đình 5 người"):
        st.chat_input("Tôi muốn mua xe cho gia đình 5 người, ngân hàng khoảng 800 triệu.")
with col2:
    if st.button("Tính gói vay VF3"):
        st.chat_input("Tính giá lăn bánh và trả góp VF 3 trong 8 năm.")
with col3:
    if st.button("Tìm trạm sạc đi Vũng Tàu"):
        st.chat_input("Tôi đi từ Quận 9 tới Vũng Tàu có trạm sạc không?")
