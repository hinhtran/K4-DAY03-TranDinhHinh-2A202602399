# 🍸 SỔ TAY TỔNG HỢP: HIỂU VÀ VẬN HÀNH HỆ THỐNG AI MIXOLOGY (LAB 03)

> **Mục tiêu của tài liệu:** Giải thích toàn bộ bài toán, cơ chế hoạt động, tư duy cốt lõi theo **góc nhìn thực tế đời sống** (dễ hiểu, trực quan, không nặng về thuật ngữ code) và hướng dẫn cách chạy hệ thống nhanh nhất.

---

## 🌟 PHẦN 1: BÀI TOÁN THỰC TẾ & TẠI SAO CẦN HỆ THỐNG NÀY?

### 1. Bối cảnh đời thực
Hãy tưởng tượng bạn đang điều hành một **Quán Bar thông minh**. Khách hàng bước vào quán và có đủ kiểu nhu cầu:
- Có người hỏi lý thuyết: *"Cocktail khác Mocktail thế nào em ơi?"*
- Có người có sở thích riêng: *"Pha cho anh món gì không cồn mà có mùi bạc hà nhé!"*
- Có người vừa uống xong thấy thích quá: *"Món Margarita này ngon quá, lưu lại vào danh sách yêu thích cho anh lần sau quay lại gọi tiếp!"*
- Có người gọi một món nghe đồn trên mạng nhưng quán không có: *"Làm cho anh ly Dragon Fire Cocktail XYZ đi!"*

---

### 2. Sự khác biệt giữa "Chatbot thông thường" và "AI Agent thông minh"

| Tiêu chí | 🤖 Chatbot truyền thống (Baseline - Cấp độ 2) | 🧠 AI ReAct Agent + MCP (Cấp độ 3 - Hệ thống này) |
| :--- | :--- | :--- |
| **Hình tượng thực tế** | Như một **nhân viên phục vụ mới vào nghề**, chỉ biết chém gió bằng trí nhớ mang máng, không có sổ tay quán và không có máy tính thu ngân. | Như một **Bartender kỳ cựu & chuyên nghiệp**, có máy tính tra cứu công thức chuẩn của quán và có phần mềm lưu trữ hồ sơ khách hàng. |
| **Khi khách hỏi công thức món lạ** | **Bịa đại (Ảo giác / Hallucination):** Tự bịa bừa nguyên liệu dù quán không bán, khiến khách uống phải thứ đồ uống thảm họa. | **Tra sổ trước:** Tra cứu cơ sở dữ liệu của quán; nếu không có thì trả lời trung thực *"Quán không có món này"*. |
| **Khi khách bảo "Lưu lại cho anh"** | **Bất lực:** Chỉ biết nói mồm *"Dạ em nhớ rồi"* nhưng quay đi là quên sạch, vì không có công cụ ghi nhận. | **Hành động thực tế:** Bật phần mềm quản lý, bấm nút lưu món đó vào danh sách yêu thích của khách. |
| **Tính minh bạch** | Khách không biết tại sao nó trả lời như vậy. | Khách thấy rõ: Nhân viên suy nghĩ gì ➡️ Tra công cụ nào ➡️ Kết quả máy tính báo về ra sao ➡️ Mới đưa ra ly nước hoàn chỉnh. |

---

## 🧩 PHẦN 2: CÁC KHÁI NIỆM CỐT LÕI QUA ẨN DỤ ĐỜI SỐNG

### 1. ReAct (Reasoning + Acting) là gì?
ReAct là cơ chế giúp AI hành động giống hệt như một con người cẩn thận và thấu đáo qua chu trình 4 bước:
1. **Thought (Suy nghĩ):** AI tự độc thoại trong đầu: *"Khách muốn tìm món Mocktail có bạc hà, vậy mình cần mở sổ pha chế ra tìm."*
2. **Action (Hành động):** AI dùng tay mở sổ tra cứu từ khóa `Mocktail` + `bạc hà`.
3. **Observation (Quan sát kết quả):** AI nhìn vào trang sách và thấy công thức `Virgin Mojito`.
4. **Final Answer (Kết luận):** AI tổng hợp thông tin và mỉm cười nói với khách: *"Em gửi anh công thức Virgin Mojito gồm có..."*.

### 2. MCP (Model Context Protocol) là gì?
- **Ẩn dụ:** Hãy coi AI là một chiếc **Laptop** thông minh, còn Database công thức và Nút bấm lưu trữ là chiếc **Máy in** hoặc **Cổng USB**. 
- Nếu không có dây cắm chuẩn USB, laptop và máy in không thể nói chuyện với nhau.
- **MCP chính là chiếc cáp kết nối tiêu chuẩn** giúp AI có thể bấm mở khóa an toàn vào hệ thống dữ liệu của quán bar để tra cứu hoặc lưu trữ mà không sợ bị xung đột phần mềm.

### 3. Waterfall Trace (Nhật ký hành trình) là gì?
- Giống như **Hộp đen máy bay** hoặc **Hóa đơn chi tiết** ghi rõ từng mili-giây:
  - Giây thứ 0: Bắt đầu nghe khách hỏi.
  - Giây thứ 0.5: Mở máy tính tra cứu.
  - Giây thứ 0.8: Máy tính trả về kết quả.
  - Giây thứ 1.2: Hoàn tất trả lời.
- Giúp người quản lý quán bar biết chính xác AI có làm đúng quy trình không, có bị chậm hay bị lỗi ở khâu nào không.

---

## 🎯 PHẦN 3: GIẢI THÍCH 5 KỊCH BẢN THỰC TẾ (TEST CASES)

| Mã | Tình huống thực tế | Cách AI ứng xử theo thực tế |
| :---: | :--- | :--- |
| **TC01** | Khách hỏi: *"Cocktail và Mocktail khác nhau như thế nào?"* | **Trả lời trực tiếp bằng kiến thức chung:** Đây là câu hỏi lý thuyết, không cần mở máy tính hay tra sổ kho. AI giải thích ngay: Cocktail có cồn, Mocktail không cồn. |
| **TC02** | Khách hỏi: *"Tìm cho tôi một loại Mocktail có bạc hà."* | **Tra cứu dữ liệu (1 bước):** AI thấy yêu cầu tìm kiếm ➡️ Dùng công cụ `recipe_search` tìm Mocktail + bạc hà ➡️ Nhận kết quả là Virgin Mojito ➡️ Trình bày công thức cho khách. |
| **TC03** | Khách hỏi: *"Nếu không có Cointreau thì thay bằng gì?"* | **Tra cứu thay thế nguyên liệu:** AI tìm trong sổ tay xem loại rượu/siro nào có vị cam tương đương (như Triple Sec, Grand Marnier) để gợi ý cho khách. |
| **TC04** | Khách bảo: *"Tìm công thức Margarita rồi lưu vào danh sách yêu thích cho tôi."* | **Hành động chuỗi đa bước (Multi-step):**<br>1. Bước 1: Tra cứu xem quán có món Margarita không (`recipe_search`).<br>2. Bước 2: Khi thấy có công thức, AI mới bấm nút lưu (`save_recipe`).<br>3. Bước 3: Thông báo cho khách đã tìm và lưu thành công. |
| **TC05** | Khách yêu cầu: *"Tìm món Dragon Fire Cocktail XYZ và lưu lại cho tôi."* | **Quy tắc bảo vệ dữ liệu (Edge Case):**<br>1. AI tìm món `Dragon Fire Cocktail XYZ` trong hệ thống.<br>2. Hệ thống báo: **Không tìm thấy (NOT_FOUND)**.<br>3. AI tuyệt đối **KHÔNG** tự bịa công thức và **KHÔNG** bấm lưu thứ không có thật vào hệ thống ➡️ Trả lời từ chối lịch sự với khách. |

---

## 🚀 PHẦN 4: HƯỚNG DẪN VẬN HÀNH HỆ THỐNG

### Cách 1: Sử dụng Giao diện Web trực quan (Khuyên dùng - Đẹp nhất)
Giao diện được thiết kế hiện đại tông xanh da trời (Sky-Blue) mô phỏng ứng dụng quầy bar chuyên nghiệp:

1. **Địa chỉ truy cập:** Mở trình duyệt và vào:
   👉 **`http://localhost:5000`**
2. **Khởi động ứng dụng Streamlit:**
   ```bash
   .venv/bin/streamlit run src/streamlit_app.py --server.port 5000
   ```
3. **Cách dùng trên giao diện Streamlit:**
   - **Thanh bên trái (Sidebar):** 
     - Chọn chế độ phản hồi (**ReAct Agent Cấp 3** vs **Baseline Chatbot Cấp 2**).
     - Bấm trực tiếp vào các nút **TC01, TC02, TC03, TC04, TC05** để kiểm thử tức thì.
     - Theo dõi danh sách công thức đã lưu (**Công thức đã lưu**).
     - Nút xóa hội thoại nhanh.
   - **Màn hình trò chuyện chính:**
     - Tự động hiển thị thẻ trạng thái quy trình ReAct (*Thought*, *Action gọi Tool*, *Observation từ MCP* với độ trễ ms).
     - Kết quả pha chế hoàn chỉnh với mỗi nguyên liệu và bước làm trên một dòng riêng.


---

### Cách 2: Chạy kiểm thử tự động qua Terminal (Command Line)
Nếu bạn muốn chạy chấm điểm toàn bộ Test Case hoặc chạy dòng lệnh:

- **Chạy tự động toàn bộ 5 Test Case và xuất báo cáo:**
  ```bash
  python3 src/app.py --all
  ```
- **Chạy chế độ gõ lệnh trò chuyện trực tiếp (Interactive CLI):**
  ```bash
  python3 src/app.py --interactive
  ```

---

## 📊 PHẦN 5: TÀI LIỆU MINH CHỨNG & BÁO CÁO (EVALUATION)

Khi cần nộp bài hoặc đối chiếu kết quả:
- **`docs/trace_waterfall.json`**: Chứa toàn bộ vết thực thi thời gian thực, các bước ReAct và latency (độ trễ ms) của hệ thống.
- **`docs/trace_eval.md`**: Bảng đánh giá chất lượng Agent, tỷ lệ thành công (Success Rate), mức độ phù hợp bài toán (Agentic Fit) và các chỉ số đo lường hiệu năng.
