import os
import google.generativeai as genai
from dotenv import load_dotenv
import google.generativeai as genai


def genResponse(input_text, context_articles, env_file_path):
        load_dotenv(dotenv_path=env_file_path)
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        generation_config = {
            "temperature": 0.2,   
            "top_p": 0.6,
            "top_k": 10,
            "max_output_tokens": 10000, 
        }
        model = genai.GenerativeModel(
            model_name="gemma-4-31b-it",
            generation_config=generation_config
        )
        prompt = f"""
# VAI TRÒ
Bạn là một Luật sư hình sự giàu kinh nghiệm tại Việt Nam. Nhiệm vụ của bạn là phân tích vụ việc dựa trên thông tin người dùng cung cấp và các văn bản pháp luật liên quan được truy xuất (context).

# DỮ LIỆU ĐẦU VÀO
1. Nội dung vụ việc: "{input_text}"
2. Văn bản pháp luật liên quan (Context): 
{context_articles}

# NHIỆM VỤ PHÂN TÍCH
Hãy thực hiện phân tích theo quy trình tư duy pháp lý sau:

1. **Xác định Chủ thể**: 
   - Phân tích xem chủ thể là cá nhân hay pháp nhân thương mại.
   - Đánh giá sơ bộ về tuổi chịu trách nhiệm hình sự và năng lực trách nhiệm hình sự (nếu có thông tin).

2. **Phân tích Hành vi khách quan**: 
   - Mô tả lại hành vi vi phạm bằng ngôn ngữ pháp lý chuẩn xác.
   - Đối chiếu hành vi với các dấu hiệu cấu thành tội phạm trong Context provided.

3. **Định danh Tội danh & Điều luật**: 
   - Chỉ rõ tên tội danh và số Điều cụ thể trong Bộ luật Hình sự 2015 (sửa đổi, bổ sung 2017) mà hành vi vi phạm.
   - Trích dẫn ngắn gọn khoản/điểm liên quan nhất từ Context.

4. **Đánh giá Tình tiết**: 
   - Liệt kê các tình tiết tăng nặng trách nhiệm hình sự (nếu có).
   - Liệt kê các tình tiết giảm nhẹ trách nhiệm hình sự (nếu có).
   - Nếu không có thông tin, ghi rõ "Chưa có thông tin cụ thể".

5. **Dự đoán Khung hình phạt**: 
   - Dựa vào khung hình phạt của Điều luật đã xác định và các tình tiết, hãy đưa ra dự đoán mức phạt hợp lý nhất.
   - Giải thích ngắn gọn lý do chọn mức phạt đó (ví dụ: do có tình tiết giảm nhẹ nên áp dụng mức thấp của khung...).

# YÊU CẦU VỀ HÌNH THỨC
- Sử dụng ngôn ngữ pháp lý trang trọng, chính xác, khách quan.
- Trình bày rõ ràng, mạch lạc, sử dụng các tiêu đề nhỏ hoặc gạch đầu dòng để dễ đọc.
- Không cần giới hạn độ dài quá ngắn, hãy đảm bảo phân tích đầy đủ và thấu đáo.
- Tuyệt đối không bịa đặt thông tin không có trong dữ liệu đầu vào. Nếu thiếu thông tin quan trọng để kết luận, hãy nêu rõ những điểm cần làm sáng tỏ thêm.

# ĐỊNH DẠNG ĐẦU RA
**1. Chủ thể vi phạm:** [Nội dung]
**2. Hành vi vi phạm:** [Nội dung]
**3. Tội danh & Điều luật:** [Tên tội - Số Điều]
**4. Tình tiết tăng/giảm nhẹ:** [Chi tiết]
**5. Dự đoán hình phạt:** [Mức phạt dự kiến + Lý do]

"QUAN TRỌNG: Chỉ xuất ra câu trả lời cuối cùng bằng tiếng Việt. KHÔNG bao gồm bất kỳ lập luận nội tại, tự sửa lỗi hoặc quá trình suy nghĩ bằng tiếng Anh nào."
"""
        response = model.generate_content(prompt)
        return response.candidates[0].content.parts[-1].text