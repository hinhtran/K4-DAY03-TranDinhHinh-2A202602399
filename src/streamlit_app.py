"""
🍸 Streamlit Mixology AI Chatbot (Lab 03 - ReAct Agent with MCP Server)
Phong cách hiện đại, tông màu Xanh da trời (Sky-Blue) & Glassmorphism
"""

import os
import sys
import json
import time
import re
from pathlib import Path
import streamlit as st

def format_stream_answer(text: str) -> str:
    if not text:
        return ""
    formatted = re.sub(r"([^\n])\s*(\*\*[^*]+:\*\*)", r"\1\n\n\2 ", text)
    formatted = re.sub(r"([^\n])\s*([–\-•])\s+", r"\1\n- ", formatted)
    formatted = re.sub(r"([^\n])\s*(\d+\.)\s+", r"\1\n\2 ", formatted)
    return formatted

def ensure_full_recipe_content(final_answer: str, traces: list) -> str:
    """Đảm bảo luôn hiển thị đầy đủ 100% chi tiết công thức (Nguyên liệu, Cách làm) từ Observation"""
    if not final_answer:
        final_answer = "Đã hoàn thành xử lý thông qua MCP Server."

    # Nếu câu trả lời đã có mục nguyên liệu và cách làm thì giữ nguyên
    if "nguyên liệu" in final_answer.lower() or "cách làm" in final_answer.lower() or "ingredient" in final_answer.lower():
        return format_stream_answer(final_answer)

    # Nếu câu trả lời chỉ ghi chung chung "Đã tìm thấy...", tự động lấy dữ liệu từ Observation
    recipe_data = None
    is_saved = False
    for t in traces:
        if t.get("action_type") == "TOOL_EXECUTION":
            if t.get("tool_name") == "save_recipe":
                is_saved = True
            elif t.get("tool_name") == "recipe_search":
                obs = t.get("observation", {})
                if obs.get("status") == "SUCCESS":
                    d = obs.get("data")
                    if isinstance(d, list) and len(d) > 0:
                        recipe_data = d[0]
                    elif isinstance(d, dict):
                        recipe_data = d

    if recipe_data and isinstance(recipe_data, dict):
        name = recipe_data.get("drink_name", "Đồ uống")
        cat = recipe_data.get("category", "Cocktail")
        ings = "\n".join([f"- {i}" for i in recipe_data.get("ingredients", [])])
        steps = "\n".join([f"{idx+1}. {s}" for idx, s in enumerate(recipe_data.get("instructions", []))])

        enriched = f"Dưới đây là công thức **{name}** ({cat}) chi tiết dành cho bạn:\n\n"
        enriched += f"**Tên đồ uống:** {name} ({cat})\n\n"
        enriched += f"**Nguyên liệu:**\n{ings}\n\n"
        enriched += f"**Cách làm:**\n{steps}"
        if is_saved:
            enriched += f"\n\n**Trạng thái:** Đã lưu {name} vào danh sách yêu thích thành công!"
        return format_stream_answer(enriched)

    return format_stream_answer(final_answer)

# Setup import path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.mcp_server import MCPCocktailServer
from src.tools import SAVED_RECIPES
from src.providers import get_llm_provider, get_provider
from src.prompts import CHATBOT_BASELINE_PROMPT, REACT_AGENT_SYSTEM_PROMPT
from src.app import run_react_agent, save_waterfall_trace

# Initialize System without caching old instances
def init_system():
    import importlib
    import src.providers
    importlib.reload(src.providers)
    server = MCPCocktailServer()
    prov = src.providers.get_llm_provider()
    return server, prov

mcp_server, provider = init_system()

# Page configuration
st.set_page_config(
    page_title="Mixology AI Chatbot | ReAct & MCP",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Modern Sky-Blue Theme CSS (Extra Large Fonts: ~3x)
st.markdown("""
<style>
    /* Dark Sky-Blue Aesthetic with Large Typography */
    html, body {
        font-size: 140% !important;
    }

    .stApp {
        background: radial-gradient(circle at 50% -20%, #0c2340 0%, #080d1a 60%, #050811 100%) !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Fix Header margin */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
    }
    
    /* General Heading Typography (Scaled 2.5x - 3x) */
    h1 { font-size: 42px !important; }
    h2 { font-size: 34px !important; }
    h3 { font-size: 28px !important; }
    h4 { font-size: 24px !important; }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(56, 189, 248, 0.05));
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .main-header h1 {
        color: #38bdf8 !important;
        font-size: 44px !important;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .main-header p {
        color: #94a3b8 !important;
        margin: 8px 0 0 0;
        font-size: 22px !important;
        line-height: 1.6 !important;
    }

    /* Badge & status pills */
    .badge-mcp {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 18px;
        border-radius: 9999px;
        font-size: 20px !important;
        font-weight: 600;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.35);
        margin: 8px 0;
    }

    /* Sidebar text & padding */
    [data-testid="stSidebar"] {
        background-color: rgba(9, 14, 26, 0.98) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
        padding-top: 1.5rem !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] label {
        font-size: 20px !important;
        line-height: 1.6 !important;
    }
    [data-testid="stSidebar"] h3 {
        font-size: 28px !important;
    }
    [data-testid="stSidebar"] h4 {
        font-size: 24px !important;
    }

    /* Radio buttons / mode selector */
    [data-testid="stRadio"] label div p {
        font-size: 20px !important;
    }

    /* Button styling: ~3x Larger text & comfortable click area */
    .stButton button, 
    [data-testid="stSidebar"] button {
        background: rgba(14, 165, 233, 0.12) !important;
        color: #e0f2fe !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 10px !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 12px 18px !important;
        line-height: 1.5 !important;
        transition: all 0.2s ease !important;
    }
    .stButton button:hover, 
    [data-testid="stSidebar"] button:hover {
        background: rgba(14, 165, 233, 0.3) !important;
        border-color: #38bdf8 !important;
        color: #ffffff !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* Code chips in dark mode */
    code {
        background-color: rgba(56, 189, 248, 0.15) !important;
        color: #7dd3fc !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
        font-size: 20px !important;
    }

    /* Chat bubble: ~3x LARGER readable text */
    [data-testid="stChatMessage"] {
        background-color: rgba(15, 23, 42, 0.82) !important;
        border: 1px solid rgba(56, 189, 248, 0.22) !important;
        border-radius: 14px !important;
        padding: 18px 22px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
    }
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span {
        color: #f1f5f9 !important;
        font-size: 24px !important;
        line-height: 1.85 !important;
    }
    [data-testid="stChatMessage"] strong {
        color: #7dd3fc !important;
    }

    /* Bottom Chat Input: ~3x Larger text and height */
    [data-testid="stBottom"], 
    [data-testid="stBottom"] > div,
    footer {
        background-color: #080d1a !important;
        border-top: 1px solid rgba(56, 189, 248, 0.2) !important;
    }
    [data-testid="stChatInput"] {
        background-color: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 14px !important;
        padding: 6px !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #f8fafc !important;
        font-size: 22px !important;
        line-height: 1.6 !important;
    }

    /* Thought & Tool styling */
    .thought-box {
        background: rgba(30, 41, 59, 0.75);
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 22px !important;
        line-height: 1.75 !important;
        color: #e2e8f0 !important;
    }
    .action-badge {
        background: rgba(14, 165, 233, 0.2);
        color: #7dd3fc;
        padding: 8px 16px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 21px !important;
        font-weight: 600;
        border: 1px solid rgba(56, 189, 248, 0.35);
        display: inline-block;
        margin: 6px 0;
    }

    /* Expander & Status headers */
    [data-testid="stStatus"] {
        font-size: 22px !important;
    }
    [data-testid="stExpander"] summary span {
        font-size: 21px !important;
    }
    .stCaption, caption, [data-testid="stCaptionContainer"] p {
        font-size: 19px !important;
        color: #94a3b8 !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Singleton Instances in session state
@st.cache_resource
def init_system():
    server = MCPCocktailServer()
    prov = get_provider()
    return server, prov

mcp_server, provider = init_system()

# Load Test Cases config
def load_test_cases():
    path = ROOT_DIR / "config" / "test_cases.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

test_cases = load_test_cases()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Xin chào! Tôi là **Mixology AI Agent (Lab 03)** được trang bị giao thức **Model Context Protocol (MCP)**.\n\nTôi có thể tra cứu công thức Cocktail/Mocktail theo thời gian thực và lưu công thức yêu thích vào hệ thống quầy bar!",
            "traces": []
        }
    ]

if "trigger_prompt" not in st.session_state:
    st.session_state.trigger_prompt = None


# SIDEBAR (LEFT)
with st.sidebar:
    st.markdown("### 🍸 Mixology Control")
    st.markdown(f"""
    <div class="badge-mcp">
        <span style="height: 8px; width: 8px; background-color: #22c55e; border-radius: 50%; display: inline-block;"></span>
        MCP Server: Active
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**Server:** `{mcp_server.server_name}`")
    st.markdown(f"**Model:** `{provider.__class__.__name__}`")
    
    st.divider()

    # Agent Mode Selector
    st.markdown("#### ⚙️ Chế độ phản hồi")
    agent_mode = st.radio(
        "Lựa chọn cấp độ Agent:",
        ("ReAct Agent (Cấp 3 - Có MCP Tools)", "Baseline Chatbot (Cấp 2 - Không Tool)"),
        index=0
    )
    is_react = "ReAct" in agent_mode

    st.divider()
    if st.button("🗑️ Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# MAIN LAYOUT (CENTER: CHAT, RIGHT: TEST CASES & SAVED RECIPES)
col_chat, col_right = st.columns([2.7, 1.3], gap="large")

with col_right:
    st.markdown("### 🧪 Test Cases (1-Click Run)")
    st.caption("Nhấp để thử nghiệm nhanh kịch bản:")

    tc_names = {
        "TC01": "Phân biệt Cocktail & Mocktail",
        "TC02": "Công thức Mojito",
        "TC03": "Mocktail có bạc hà",
        "TC04": "Margarita & Lưu yêu thích",
        "TC05": "Dragon Fire (Edge Case)"
    }
    for tc in test_cases:
        tc_id = tc.get("id")
        tc_prompt = tc.get("question") or tc.get("prompt") or ""
        tc_name = tc.get("name") or tc_names.get(tc_id, tc_prompt[:25])
        
        btn_label = f"📌 {tc_id}: {tc_name}"
        if st.button(btn_label, key=f"btn_{tc_id}", use_container_width=True):
            st.session_state.trigger_prompt = tc_prompt

    st.divider()

    # Saved Recipes tracker
    st.markdown("### ❤️ Công thức đã lưu")
    if SAVED_RECIPES:
        for r in SAVED_RECIPES:
            st.markdown(f"- 🍹 **{r}**")
    else:
        st.caption("Chưa có công thức nào được lưu.")

    st.divider()
    st.markdown("### 📊 Waterfall Trace")
    st.caption("Toàn bộ nhật ký độ trễ và các bước ReAct được lưu tự động tại `docs/trace_waterfall.json`.")


with col_chat:
    # MAIN HEADER
    st.markdown("""
    <div class="main-header">
        <h1>🍸 Mixology AI Chatbot (Lab 03)</h1>
        <p>Trực quan hoá quy trình suy luận <strong>ReAct Agent</strong> và giao thức chuẩn hoá <strong>Model Context Protocol (MCP)</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # DISPLAY CHAT HISTORY
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🍸" if msg["role"] == "assistant" else "👤"):
            # ReAct Trace Steps
            traces = msg.get("traces", [])
            if traces:
                with st.status(f"⚡ Quy trình ReAct ({len(traces)} bước xử lý)", expanded=False):
                    for step in traces:
                        if step.get("action_type") == "TOOL_EXECUTION":
                            st.markdown(f"**🔄 Step {step.get('step')}: TOOL EXECUTION** `({step.get('latency_ms', 0)} ms)`")
                            st.markdown(f"""
                            <div class="thought-box">
                                🧠 <strong>Thought:</strong> {step.get('thought', 'Đang phân tích...')}
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown(f"<div class='action-badge'>🛠️ {step.get('tool_name')}({json.dumps(step.get('arguments', {}), ensure_ascii=False)})</div>", unsafe_allow_html=True)
                            with st.expander("👁️ Observation từ MCP Server"):
                                st.json(step.get("observation", {}))
                        elif step.get("action_type") == "FINAL_ANSWER":
                            st.markdown(f"**🏁 Step {step.get('step')}: FINAL ANSWER** `({step.get('latency_ms', 0)} ms)`")
                            st.markdown(f"""
                            <div class="thought-box">
                                🧠 <strong>Thought:</strong> {step.get('thought', 'Hoàn tất.')}
                            </div>
                            """, unsafe_allow_html=True)

            # Markdown Content
            msg_content = msg.get("content", "")
            if msg.get("role") == "assistant" and traces:
                msg_content = ensure_full_recipe_content(msg_content, traces)
            st.markdown(msg_content)


# PROCESS INPUT (from text input or Test Case button)
user_prompt = st.chat_input("Nhập câu hỏi về Cocktail, Mocktail hoặc yêu cầu pha chế...")

if st.session_state.trigger_prompt:
    user_prompt = st.session_state.trigger_prompt
    st.session_state.trigger_prompt = None

if user_prompt:
    # 1. Append User message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with col_chat:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_prompt)

        # 2. Assistant Response
        with st.chat_message("assistant", avatar="🍸"):
            if not is_react:
                # Baseline chatbot
                with st.spinner("🤖 Chatbot Baseline đang phản hồi..."):
                    resp = provider.generate(user_prompt, system_prompt=CHATBOT_BASELINE_PROMPT)
                    st.markdown(resp)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": resp,
                        "traces": []
                    })
            else:
                # ReAct Agent with MCP Server
                status_container = st.status("🧠 ReAct Agent đang suy luận và tương tác MCP Server...", expanded=True)
                
                with status_container:
                    st.write("🔍 Đang kích hoạt vòng lặp ReAct...")
                    traces = run_react_agent(user_prompt, provider, mcp_server)
                    save_waterfall_trace(traces)

                    for step in traces:
                        if step.get("action_type") == "TOOL_EXECUTION":
                            st.markdown(f"**🔄 Step {step.get('step')}: Gọi Tool** `{step.get('tool_name')}` ({step.get('latency_ms', 0)} ms)")
                            st.caption(f"Thought: {step.get('thought')}")
                        elif step.get("action_type") == "FINAL_ANSWER":
                            st.markdown(f"**🏁 Step {step.get('step')}: Hoàn thành**")

                    status_container.update(label="✅ Hoàn thành quy trình ReAct!", state="complete", expanded=False)

                # Extract final answer
                final_answer = ""
                for t in reversed(traces):
                    if t.get("action_type") == "FINAL_ANSWER":
                        final_answer = t.get("output", "")
                        break

                final_answer = ensure_full_recipe_content(final_answer, traces)

                st.markdown(final_answer)

                # Store in session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_answer,
                    "traces": traces
                })

    # Trigger re-render to update saved recipes if any
    st.rerun()
