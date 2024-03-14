from typing import Union, List
from numpy import ndarray
from torch import Tensor

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self):
        self.cache_dir = "transformers-cache/"
        self.model_name = "BAAI/bge-large-zh-v1.5"
        self.model = SentenceTransformer(self.model_name, cache_folder=self.cache_dir)

    def get_embedding(
            self, input_texts: list[str]
    ) -> Union[List[Tensor], ndarray, Tensor]:
        return self.model.encode(input_texts, normalize_embeddings=True)
