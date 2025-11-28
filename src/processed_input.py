import os
import torch
from pyvi import ViTokenizer
from transformers import AutoTokenizer, AutoModel
import google.generativeai as genai
import json
from pydantic import BaseModel, Field
from src import database
from unidecode import unidecode

class ProcessedInput:
    def reformat(text):
        text = ViTokenizer.tokenize(text)
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
        inputs = tokenizer(text, truncation=True, padding=True, return_tensors = 'pt')
        model_output = model(**inputs)
        final_embedding = ProcessedInput.mean_pooling(model_output, inputs['attention_mask'])
        return final_embedding[0].detach().tolist()

