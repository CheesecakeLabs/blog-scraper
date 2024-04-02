import json
import os
from typing import Union, List
from chromadb import Documents, EmbeddingFunction, Embeddings
import boto3
from dotenv import load_dotenv
from numpy import ndarray
from torch import Tensor

from sentence_transformers import SentenceTransformer


class BAAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.cache_dir = "../transformers-cache/"
        self.model_name = "BAAI/bge-large-zh-v1.5"
        self.model = SentenceTransformer(self.model_name, cache_folder=self.cache_dir)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = self.get_embedding(input)
        return embeddings

    def get_embedding(
            self, input_texts: list[str]
    ) -> Union[List[Tensor], ndarray, Tensor]:
        return self.model.encode(input_texts, normalize_embeddings=True)


class AWSEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        load_dotenv(dotenv_path="../config/.env.development")
        AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
        AWS_BEDROCK_REGION = os.getenv("AWS_BEDROCK_REGION")

        if (AWS_ACCESS_KEY_ID is not None and
                AWS_SECRET_ACCESS_KEY is not None and
                AWS_SESSION_TOKEN is not None
        ):
            self.bedrock_runtime = boto3.client(
                service_name="bedrock-runtime",
                region_name=AWS_BEDROCK_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                aws_session_token=AWS_SESSION_TOKEN,
            )
        else:
            self.bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name=AWS_BEDROCK_REGION)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = self.get_embedding(input)
        return embeddings

    @staticmethod
    def build_body(prompt_data):
        return json.dumps(
            {
                "inputText": prompt_data,
            }
        )

    def get_embedding(
            self, input_texts: list[str]
    ) -> Union[List[Tensor], ndarray, Tensor]:
        embeddings = []
        for input_text in input_texts:
            body = self.build_body(input_text)
            response = self.bedrock_runtime.invoke_model(
                body=body,
                modelId="amazon.titan-embed-text-v1",
                accept="application/json",
                contentType="application/json",
            )
            response_body = json.loads(response["body"].read())
            embedding = response_body.get("embedding")
            embeddings.append(embedding)
        return embeddings
