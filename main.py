from dotenv import load_dotenv
import os
import psycopg2
import torch
from pyvi import ViTokenizer
from transformers import AutoTokenizer, AutoModel

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
            cursor.execute("select concat(article_name,' ',full_content), (%s::vector <=> c.embedding ) as cosine_distance from articles a join chunk c using(article_id) where (%s::vector <=> c.embedding )<=0.63 order by cosine_distance limit 15;",(input_embedding, input_embedding, ))
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

all_related_articles=return_similar_articles(final_embedding)
if(len(all_related_articles)==0):
    print("Không tìm thấy điều luật liên quan")
else:
    for article in all_related_articles:
        print(article[0])




