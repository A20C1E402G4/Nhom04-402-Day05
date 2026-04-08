---

# SPEC — AI Product Hackathon: VinFast Smart Sales Agent (VSSA)

**Nhóm:** VinSales AI-Powered  
**Track:** ☑ VinFast  
**Problem statement (1 câu):** Khách hàng mua xe điện thường bị "ngợp" bởi thông số kỹ thuật, bài toán chi phí thuê pin và các gói vay; VSSA là Agent thông minh giúp cá nhân hóa tư vấn 24/7, tự động lập phương án tài chính và chốt lịch lái thử trong 1 phút.

---

## 1\. AI Product Canvas

|  | Value | Trust | Feasibility |
| :---- | :---- | :---- | :---- |
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | Khách hàng mới. Sợ tính toán phức tạp. AI đóng vai trò Sales Expert tư vấn xe \+ tài chính. | AI báo sai giá/khuyến mãi. Luôn kèm link "Nguồn dữ liệu gốc" để đối chiếu. | \~$0.2/lượt tư vấn. Latency \<5s. Risk: "Ảo giác" (hallucinate) về các tính năng xe chưa ra mắt. |

**Automation hay augmentation?** ☑ Augmentation  
*Justify: AI đóng vai trò "phễu" dẫn dắt khách hàng. Việc ký hợp đồng và bàn giao xe vẫn cần con người để đảm bảo tính pháp lý và trải nghiệm thực tế.*	

**Learning signal:**   
1\. **User correction:** Khi user nói "Tôi thấy phí thuê pin này hơi cao", Agent ghi nhận phản đối để cải thiện kịch bản thuyết phục (Objection handling).  
2\. **Product signal:** Tỷ lệ người để lại thông tin trên tổng số người chat.

* **Tool Accuracy:** Tỷ lệ gọi đúng hàm dựa trên yêu cầu của khách.

3\. **Data thuộc loại nào:** ☑ User-specific (Thói quen di chuyển) · ☑ Domain-specific (Thông số xe) · ☑ Real-time (Giá & Tồn kho).

**Có marginal value không?** Rất lớn. Mỗi câu hỏi của khách hàng Việt Nam về xe điện là một dữ liệu độc quyền mà các mô hình LLM như GPT hay Gemini không bao giờ có được.

---

## 2\. User Stories — 4 paths (Agentic Workflow)

### Feature 1: Personal Sales Concierge

**Trigger:** User hỏi: *"Tôi có 800 triệu, nhà 4 người, ở chung cư, nên mua xe nào?"*

| Path | Câu hỏi thiết kế | Mô tả |
| :---- | :---- | :---- |
| **Happy — AI đúng** | User thấy gì? | Agent đề xuất VF 7\. Gọi **Financing Tool** tính trả góp: Trả trước 200tr, góp 8tr/tháng. Hiện nút "Chốt lịch lái thử" gần nhà khách. |
| **Low-confidence** | System báo "không chắc"? | Khách hỏi về thông tin ngoài data (ghế lái có bọc da không). Agent báo: "Thông tin này tôi chưa rõ. Hãy trao đổi với saler để được tư vấn kỹ hơn" |
| **Failure — AI sai** | User biết AI sai? | AI báo nhầm xe VF 8 có giá của VF 5\. User thấy vô lý. Hệ thống hiển thị cảnh báo: "Giá này chỉ mang tính tham khảo, vui lòng xác nhận với showroom." |
| **Correction — user sửa** | User sửa bằng cách nào? | User: "Tính lại với gói vay 80% đi". Agent lập tức gọi lại tool tính toán và cập nhật bảng dòng tiền mới trong 2 giây. |

### Feature 2: Green-Route & TCO Planner — Phân tích chi phí & Lộ trình xanh

**Trigger:** User chia sẻ thói quen đi lại: *"Tôi đi làm từ Quận 9 sang Quận 1 mỗi ngày, cuối tuần hay về quê ở Vũng Tàu thì có trạm sạc trên đường không. Quãng đường có đủ pin không, 1 tuần phải sạc mấy lần. Liệu dùng xe điện có bất tiện và tiết kiệm hơn xe xăng không?"*

| Path | Câu hỏi thiết kế | Mô tả |
| :---- | :---- | :---- |
| **Happy — AI đúng** | User thấy gì? | Agent gọi **Maps API** và **Energy-Cost Tool**. Nó vẽ ra lộ trình đi làm, đánh dấu các trạm sạc trên đường. Sau đó tính: *"Một tháng bạn tiết kiệm được 2.5 triệu tiền xăng, giảm 150kg CO2"*. |
| **Low-confidence** | System báo "không chắc"? | User ở khu vực vùng sâu vùng xa chưa có trạm sạc DC. Agent đề xuất phương án sạc tại nhà qua ổ cắm dân dụng và dự báo lịch trình lắp đặt trạm sạc mới của VinFast tại khu vực đó. |
| **Failure — AI sai** | User biết AI sai? | AI tính toán dựa trên giá điện bậc thang sai. User thấy con số tiết kiệm quá cao. Agent cho phép user điều chỉnh: *"Hãy nhập giá điện/xăng thực tế bạn đang trả để tôi tính lại chính xác"*. |
| **Correction — user sửa** | User sửa bằng cách nào? | User kéo thanh trượt điều chỉnh số km đi hàng tháng. Toàn bộ bảng tính toán Tổng chi phí sở hữu (TCO) trong 5 năm sẽ tự động nhảy số theo thực tế. |

---

## 3\. Eval metrics \+ threshold

**Optimize precision hay recall?** ***1*** Góc nhìn về thông số xe như giá bán, khoản vay, khuyến mãi: ☑ Precision  
***Tại sao?*** Trong bán hàng và tài chính, thông số phải tuyệt đối chính xác. Thà Agent nói "Tôi cần kiểm tra lại" còn hơn báo sai giá gây mất uy tín thương hiệu.

| Metric | Threshold | Red flag (dừng khi) |
| :---- | :---- | :---- |
| **Accuracy (Giá & Thông số)** | 100% | \< 100% (Bất kỳ sai số nào về giá) |
| **Lead Gen Rate** | ≥ 15% | \< 5% (Khách tương tác nhưng không để lại thông tin) |
| **Tool Call Success Rate** | \> 95% | \< 80% (Agent không gọi được API tính toán/bản đồ) |

***2*** Góc nhìn tối ưu khách hàng, tăng doanh số: ☑ Recall ***Tại sao?*** Với mục tiêu **tăng trưởng doanh số thần tốc (Aggressive Sales)**, Agent cần ưu tiên thu thập tối đa tệp khách hàng tiềm năng. Thà phản hồi một cách chủ động và gợi mở cho những khách hàng chưa thực sự sẵn sàng (Low Precision) còn hơn là "im lặng" hoặc quá khắt khe khiến bỏ lỡ một người mua thực sự (False Negative). Mục tiêu là giữ khách ở lại trong phễu bán hàng càng lâu càng tốt.

| Metric | Threshold | Red flag (dừng khi) |
| :---- | :---- | :---- |
| **Lead Generation Recall** | ≥ 90% | \< 70% (Bỏ sót quá nhiều khách hàng có ý định mua) |
| **Response Rate** | 100% | \< 95% (Agent không phản hồi hoặc phản hồi chậm) |
| **Engagement Rate** (Số lượt chat/phiên) | \> 5 câu | \< 2 câu (Khách rời đi ngay sau khi hỏi giá) |
| **Lỗi sai thông số nghiêm trọng** | \< 2% | \> 5% (Dù ưu tiên Recall nhưng vẫn phải kiểm soát lỗi giá) |

---

---

## 4\. Top 3 failure modes

| \# | Trigger | Hậu quả | Mitigation |
| :---- | :---- | :---- | :---- |
| 1 | API Outdated/Down | Agent không có dữ liệu để trả lời (do không có file backup) | Thiết lập **Fallback Response**: Nếu API lỗi, Agent xin lỗi và tự động gửi thông báo cho Sales thật gọi lại ngay. |
| 2 | LLM Hallucination trong tham số | Agent tự chế ra một con số (VD: 50% lãi suất) để điền vào hàm tính toán | **Input Validation**: Kiểm tra logic tham số trước khi thực hiện hàm (ví dụ: lãi suất phải nằm trong khoảng 0-20%). |
| 3 | Logic Loop (Vòng lặp suy luận) | Agent gọi API liên tục nhưng không ra kết quả khách muốn (do ưu tiên Recall) | **Max-turn Limit**: Giới hạn tối đa 3 lần gọi tool cho một câu hỏi. Nếu không xong, chuyển sang chế độ "Hỏi thêm thông tin từ khách". |

---

## 5\. ROI 3 kịch bản

|  | Conservative | Realistic | Optimistic |
| :---- | :---- | :---- | :---- |
| **Assumption** | 1,000 khách/tháng | 5,000 khách/tháng | 20,000 khách/tháng |
| **Cost** | $200 (API & Infra) | $800 | $2,500 |
| **Benefit** | Thu được 50 Leads | Thu được 500 Leads | Thu được 3,000 Leads \+ 200 lịch lái thử |
| **Net** | Rẻ hơn 1 nhân viên tư vấn | Tương đương đội sales 10 người | Trở thành kênh bán hàng chủ lực toàn cầu |

**Kill criteria:** Khi chi phí thu thập 1 Lead từ AI cao hơn chi phí quảng cáo truyền thống trong 3 tháng liên tiếp.

---

## 6\. Mini AI spec (Technical Summary)

**VSSA** được xây dựng theo kiến trúc **API-First Agent** tập trung vào tốc độ và khả năng thực thi tác vụ trực tiếp thay vì tra cứu văn bản.:

* **Planning & Reasoning:** Sử dụng LLM (như GPT-4o, Gemini 3 Pro, Claude 3.5 hoặc local như Qwen 2.5, Llama 3.2 ) để phân tích nhu cầu khách hàng (ngân sách, số thành viên gia đình, địa điểm sạc) trước khi đưa ra gợi ý.  
* **Tool Use (Function Calling):**  
  * `get_vehicle_data(model_id)`: Truy vấn trực tiếp vào Database sản phẩm để lấy thông số/giá.  
  * `get_promotion(vin_id)`: Kiểm tra các mã giảm giá và chương trình ưu đãi real-time.  
  * `calculate_loan()`: Tính toán lãi suất thực tế dựa trên các ngân hàng đối tác.  
  * `find_charging_stations()`: Dùng Google Maps API để chứng minh sự tiện lợi của trạm sạc quanh khu vực khách sống.  
* **Memory:** Nhớ các lựa chọn trước đó của khách trong cùng một phiên chat để không hỏi lại những điều đã biết.  
* **Data Flywheel:**   
  * **The Signal:**  
    * **Failed Intent Logs:** Ghi lại những câu hỏi khách hàng mà Agent không thể phân loại vào các Tool hiện có (ví dụ: khách hỏi về độ bền màu sơn trong 10 năm \- một data chưa có API).  
    * **Conversion Path:** Lưu lại toàn bộ luồng hội thoại dẫn đến hành động "Đăng ký lái thử" thành công.  
    * **Sales Feedback:** Khi Lead được đẩy xuống showroom, nhân viên Sales thật sẽ đánh giá: "Khách này đã được tư vấn đúng nhu cầu chưa?" (Thang điểm 1-5).  
  * **Optimize:**  
    * **System Prompt Tuning:** Cập nhật kịch bản dẫn dụ (Sales Pitch) dựa trên những luồng hội thoại có tỷ lệ chốt đơn cao nhất.  
    * **API Expansion:** Nếu khách hỏi quá nhiều về một chủ đề chưa có Tool (ví dụ: Phụ kiện lắp thêm), đội ngũ kỹ thuật sẽ ưu tiên xây dựng API `get_accessories()` để Agent gọi hàm trong tương lai.

---

