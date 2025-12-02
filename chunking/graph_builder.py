from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
from pydantic import BaseModel, Field


base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_file_path = os.path.join(base_directory,'data','processed','luat_hinh_su_metadata.json')
dotenv_path = os.path.join(base_directory,'.env')  
load_dotenv(dotenv_path=dotenv_path)

with open(json_file_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)


class content_one_article(BaseModel):
    id: int = Field(description="id của điều luật chính là số thứ tự của điều luật đó và là số nguyên")
    referenced_laws: list[int] = Field(description="danh sách các điều luật được đề cập trong điều luật hiện tại")

class content_response(BaseModel):
    items : list[content_one_article]

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
generation_config = {
    "temperature": 0.0,   
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 10000, 
    "response_mime_type": "application/json",
    "response_schema" : content_response
    }
model = genai.GenerativeModel(
model_name="gemini-2.5-flash",
    generation_config=generation_config
    )


def list_of_referenced_laws(law_list):
    prompt = f"""
    tôi có một đoạn văn bản pháp luật chứa thông tin đầy đủ của các điều luật như sau: {law_list} và mỗi điểu luật có id chính là số thứ tự của điều luật đó ví dụ điều 36 có id là 36
    tôi cần bạn tạo giúp tôi 1 kiểu dữ liệu list của các dict trong python trong đó key là id của điều luật hiện tại và value là list của các điều luật được đề cập đến trong điều luật hiện tại
    nhớ là bạn chỉ được cung cấp cho tôi theo định dạng list của các dict trong python thôi không được thêm bất kỳ lời giải thích nào khác ngoài định dạng dict đó, nếu điều luật hiện tại không đề cập đến điều luật khác thì đưa ra value là list rỗng, tuyệt đối chỉ đưa ra định dạng tôi đề cập không được thêm bất kì thông tin nào khác output chỉ được có dạng '{{[{{id:val}}]}}' thôi KHÔNG ĐƯỢC THÊM KÍ HIỆU HOẶC CÁI GÌ KHÁC ĐỊNH DẠNG TÔI MUỐN OUTPUT CHỈ 1 DÒNG THÔI VÀ ĐỊNH DẠNG ĐÓ PHẢI CÓ THỂ DÙNG ĐƯỢC TRONG HÀM LOADS CỦA JSON PYTHON, GIÁ TRỊ CỦA KEY LÀ INT, CHÚ Ý dấu nháy đơn là ' KHÔNG PHẢI LÀ ` làm ơn output là 1 dòng để nếu tôi sử dụng output này cho hàm loads thì sử dụng được
    """
    response = model.generate_content(prompt)
    return response.text
    

graph_list = []
for i in range(0,len(metadata),10):
    if i!=0:
        law_list = [article['title']+article['content'] for article in metadata[i-10:i]]
        law_list = "\n\n".join(law_list)
        graph_list += json.loads(list_of_referenced_laws(law_list))['items']

final_index = int((len(metadata)-1)/10)*10
if final_index!=len(metadata)-1:
    law_list = [article['title']+article['content'] for article in metadata[final_index:len(metadata)]]
    law_list = "\n\n".join(law_list)
    graph_list += json.loads(list_of_referenced_laws(law_list))['items']
else:
    law_list = [article['title']+article['content'] for article in metadata[final_index]]
    law_list = "\n\n".join(law_list)
    graph_list += json.loads(list_of_referenced_laws(law_list))['items']

# save to json (type list of dict)
output_file_path_meta = os.path.join(base_directory,'data','processed','graph_lookup.json')
with open(output_file_path_meta, 'w', encoding='utf-8') as f:
    json.dump(graph_list, f, ensure_ascii=False, indent=4)

