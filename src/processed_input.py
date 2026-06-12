import os
import torch
from pyvi import ViTokenizer
from transformers import AutoTokenizer, AutoModel
import google.generativeai as genai
import json
from pydantic import BaseModel, Field
from src import database
from unidecode import unidecode
import re
from dotenv import load_dotenv
import google.generativeai as genai


class ProcessedInput:

    # for postgres web search
    def reformat(text):
        text = ViTokenizer.tokenize(text)
        text = re.sub(r'[",.!?;]', '', text)
        text = unidecode(text)
        text = " or ".join(text.split())
        return text
    def mean_pooling(model_output, attention_mask):
        token_embeddings = model_output[0] 
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    def getEmbedding(checkpoint, text):
        tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        model = AutoModel.from_pretrained(checkpoint)
        text = ViTokenizer.tokenize(text)
        inputs = tokenizer(text, truncation=True, padding=True, max_length=256, return_tensors = 'pt')
        model_output = model(**inputs)
        final_embedding = ProcessedInput.mean_pooling(model_output, inputs['attention_mask'])
        return final_embedding[0].detach().tolist()
    def queryRewriting(input_text,env_file_path):
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
            bạn là 1 trợ lý am hiểu về pháp luật việt nam hãy viết lại 1 câu có nghĩa tương tự với câu: {input_text} sử dụng các từ ngữ pháp lý của bộ luật hình sự việt nam
            chú ý chỉ viết lại câu, không thêm bất kì thông tin nào, tuy nhiên có thể thêm ý kiến của bạn về việc tăng nặng giảm nhẹ. Chú ý chiều dài của câu không được quá 256 từ, viết làm sao để cô động mà vẫn đầy đủ ý
            """
        response = model.generate_content(prompt)
        return response.text