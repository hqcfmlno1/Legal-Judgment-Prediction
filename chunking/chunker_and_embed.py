import json
import re
import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pyvi import ViTokenizer

base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_file_path = os.path.join(base_directory,'data','processed','luat_hinh_su_metadata.json')
dotenv_path = os.path.join(base_directory,'.env')  
load_dotenv(dotenv_path=dotenv_path)

with open(json_file_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# model for chunking and embedding
checkpoint = 'bkai-foundation-models/vietnamese-bi-encoder'
model = AutoModel.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# calculate number of tokens per word-segmented title to find the max number of tokens for adjusting chunk size
number_of_tokens_per_word_segmented_title = [len( tokenizer.tokenize(ViTokenizer.tokenize(item['title'])) ) for item in metadata]

# text splitter
text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer,
    chunk_size = 256 - max(number_of_tokens_per_word_segmented_title),
    chunk_overlap = int((256 - max(number_of_tokens_per_word_segmented_title))*0.17),
    separators=["\n\n", "\n", r".", " ", ""]
)

# func for chunking
def chunk_text(article):
    chunks = text_splitter.split_text(article)
    return chunks

# create chunks for all articles and adding word segmentation
for item in metadata:
    item['id'] = int(re.findall(r"Điều\s(\d+)\.",item['title'])[0])
    word_segmented_title = ViTokenizer.tokenize(item['title'])
    chunks = [(word_segmented_title + " " + chunk) for chunk in chunk_text(item['content'])]
    item['chunks'] = [ViTokenizer.tokenize(chunk) for chunk in chunks]

