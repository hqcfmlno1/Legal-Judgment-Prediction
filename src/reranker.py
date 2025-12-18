from sentence_transformers import CrossEncoder
import torch


class ReRanker:
    def __init__(self, checkpoint):
        self.checkpoint = checkpoint
    def getTopK(self, query, candidate_list, top_k=10, batch_size=10):
        cross_encoder = CrossEncoder(self.checkpoint, model_kwargs={'torch_dtype': torch.float16})
        my_top_k = cross_encoder.rank(
            query,
            candidate_list,
            top_k = top_k,
            return_documents = True,
            batch_size=batch_size
        )
        final_list_for_prompt = [item['text'] for item in my_top_k]
        return final_list_for_prompt
