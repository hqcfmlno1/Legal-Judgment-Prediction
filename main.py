from dotenv import load_dotenv
import os
import psycopg2
import torch
from pyvi import ViTokenizer
from transformers import AutoTokenizer, AutoModel
import google.generativeai as genai

base_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_directory,'.env')  
load_dotenv(dotenv_path=dotenv_path)


conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)


checkpoint = 'bkai-foundation-models/vietnamese-bi-encoder'
model = AutoModel.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] 
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def return_similar_articles(input_embedding):
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("select distinct concat(article_name,' ',full_content), penal_code_version, (%s::vector <=> c.embedding ) as cosine_distance from articles a join chunk c using(article_id) where (%s::vector <=> c.embedding )<=0.8 order by cosine_distance limit 15;",(input_embedding, input_embedding, ))
            rows = cursor.fetchall()
    return rows        


def test():
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("select article_name from articles where article_id <= 5")
            row = cursor.fetchall()
    return row        


input_text = input()
word_segmented_input = ViTokenizer.tokenize(input_text)
inputs = tokenizer(word_segmented_input, truncation=True, padding=True, return_tensors = 'pt')
model_output = model(**inputs)
final_embedding = mean_pooling(model_output, inputs['attention_mask'])[0].detach().tolist()

# get all related articles
all_related_articles=return_similar_articles(final_embedding)
if(len(all_related_articles)==0):
    print("Không tìm thấy điều luật liên quan")
else:
    context_for_prompt = [article[0] for article in all_related_articles]
    context_for_prompt_str = "\n".join(context_for_prompt)
    context_for_prompt_str+=all_related_articles[0][1]  # add penal code version info

    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    generation_config = {
    "temperature": 0.2,   # 0.0 - 1.0 (Thấp = chính xác, Cao = sáng tạo)
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 10000, # Độ dài câu trả lời mong muốn
    }
    model = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    generation_config=generation_config
    )

    prompt = f"""
    Bạn là 1 trợ lý am hiểu về luật pháp hãy giúp tôi tìm ra các chủ thể có tội và hình phạt tương ứng của họ trong trường hợp sau:
    Ngữ cảnh: {input_text}
    Biết các điều luật có thể liên quan đến trường hợp trong ngữ cảnh của tôi là:
    {context_for_prompt_str}
    Hãy liệt kê các chủ thể có tội và hình phạt tương ứng của họ không cần liệt kê ra các điều luật trong các điều luật liên quan được gửi nếu bạn cảm thấy điều luật đó thực sự không liên quan.
    """
    response = model.generate_content(prompt)
    print(response.text)
    




