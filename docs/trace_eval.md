# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3

> **Họ và Tên Học viên:** Trần Đình Hinh
> **Mã Sinh Viên / Mã Học viên:** 2A202602399 
> **Chủ đề:** Cocktail & Mocktail Recipe Agent 
> **Chủ đề Lựa chọn:** Trợ lý ReAct hỗ trợ tìm kiếm, kiểm tra và lưu công thức Cocktail/Mocktail dựa trên yêu cầu của người dùng. Agent tự quyết định khi nào cần tra cứu công thức và khi nào cần thực hiện hành động lưu công thức, thông qua MCP Tools.

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí | Điểm | Giải trình |
|---|---|---|
| Multi-step Reasoning | 4/5 | Một số yêu cầu cần tra cứu rồi thực hiện hành động tiếp theo. |
| Tool Interaction | 5/5 | Agent sử dụng recipe_search và save_recipe thông qua MCP. |
| Dynamic Decision | 5/5 | Kết quả recipe_search quyết định Agent có tiếp tục gọi save_recipe hay không |
| Long Horizon Goal | 2/5 | Nhiệm vụ thường hoàn thành trong một phiên với vài bước. |
| **Tổng** | **16/20** | Phù hợp triển khai ReAct Agent. |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Tìm Margarita và lưu vào yêu thích.",
    "action_type": "TOOL_EXECUTION",
    "thought": "Cần tìm công thức trước.",
    "tool_name": "recipe_search",
    "arguments": {
      "drink_name": "Margarita"
    },
    "observation": {
      "status": "SUCCESS",
      "data": {
        "drink_name": "Margarita",
        "category": "Cocktail"
      }
    },
    "latency_ms": 542.31
  },
  {
    "step": 2,
    "query": "Tìm Margarita và lưu vào yêu thích.",
    "action_type": "TOOL_EXECUTION",
    "thought": "Công thức đã tìm thấy, cần lưu theo yêu cầu.",
    "tool_name": "save_recipe",
    "arguments": {
      "drink_name": "Margarita"
    },
    "observation": {
      "status": "SUCCESS",
      "message": "Đã lưu Margarita vào danh sách yêu thích."
    },
    "latency_ms": 311.42
  },
  {
    "step": 3,
    "query": "Tìm Margarita và lưu vào yêu thích.",
    "action_type": "FINAL_ANSWER",
    "thought": "Đã hoàn thành mục tiêu.",
    "output": "Đã tìm thấy công thức Margarita và lưu vào danh sách yêu thích.",
    "latency_ms": 8.2
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 5 lượt.
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
