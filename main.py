from dotenv import load_dotenv
import os
import psycopg2
import torch
from pyvi import ViTokenizer
from transformers import AutoTokenizer, AutoModel
import google.generativeai as genai
import json
from pydantic import BaseModel, Field
from src.database import LegalPostgresDb
from src.processed_input import ProcessedInput
from unidecode import unidecode
from src.graph_lookup import GraphLookUp
from src.reranker import ReRanker
from src.generation import genResponse

base_directory = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(base_directory,'data','processed','related_article.json')
dotenv_path = os.path.join(base_directory,'.env')  
load_dotenv(dotenv_path=dotenv_path)

host=os.getenv('DB_HOST')
port=os.getenv('DB_PORT')
dbname=os.getenv('DB_NAME')
user=os.getenv('DB_USER')
password=os.getenv('DB_PASSWORD')

postgres_db = LegalPostgresDb(host,port,dbname,user,password)



input_text = input()
rephrase_input_text = ProcessedInput.queryRewriting(input_text, dotenv_path)


word_for_fts = ProcessedInput.reformat(rephrase_input_text)
final_embedding = ProcessedInput.getEmbedding(checkpoint = 'bkai-foundation-models/vietnamese-bi-encoder', text = rephrase_input_text)

article_list = postgres_db.top_similar_articles(word_for_fts, final_embedding, limit=100, threshold=1.5)
print(article_list)

candidate_articles_id_mapper = postgres_db.find_article_content(article_list)
candidate_articles = [key for key in candidate_articles_id_mapper]


reranker_test = ReRanker(checkpoint = 'BAAI/bge-reranker-v2-m3')
final_candidate_articles = reranker_test.getTopK(rephrase_input_text, candidate_articles, top_k=30, batch_size=10)
article_id_set = set()
for article_content in final_candidate_articles:
    article_id_set.add(candidate_articles_id_mapper[article_content])

graph_lookup = GraphLookUp(filepath=json_file_path)
reference_article_id_list = set()
for article_id in article_id_set:
    reference_article_id_list.update(graph_lookup.getAllRelatedArticleId(article_id))
article_id_set.update(reference_article_id_list)
print(article_id_set)
prompt_articles = list(postgres_db.find_article_content(list(article_id_set)).keys())

print(genResponse(rephrase_input_text, prompt_articles, dotenv_path))
