import json
import re
import os
import torch
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
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

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

#chunks embedding

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] 
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


chunks = [chunk for item in metadata for chunk in item['chunks']]
inputs = tokenizer(chunks, padding=True, truncation=True, return_tensors='pt')
inputs = {key: value.to(device) for key, value in inputs.items()} #convert to gpu
input_attention_mask = inputs['attention_mask']
with torch.no_grad():
    model_output = model(**inputs)

embeddings = mean_pooling(model_output, input_attention_mask)
embeddings = embeddings.detach().tolist()
chunk_embedings = dict(zip(chunks, embeddings))
print(chunk_embedings)

