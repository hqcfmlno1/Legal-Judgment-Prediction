from dotenv import load_dotenv
import os
import psycopg2
import torch
from pyvi import ViTokenizer
from transformers import AutoTokenizer, AutoModel
import google.generativeai as genai
import json
from pydantic import BaseModel, Field


base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_file_path = os.path.join(base_directory,'data','processed','graph_lookup.json')
dotenv_path = os.path.join(base_directory,'.env')  
load_dotenv(dotenv_path=dotenv_path)

with open(json_file_path, 'r', encoding='utf-8') as f:
    graph_lookup = json.load(f)

related={}
for item in graph_lookup:
    related[item['id']]=item['referenced_laws']

output_file_path_related_article = os.path.join(base_directory,'data','processed','related_article.json')
with open(output_file_path_related_article, 'w', encoding='utf-8') as f:
    json.dump(related, f, ensure_ascii=False, indent=4)
