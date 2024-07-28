from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import re
import os, time
from openai import OpenAI
import json
from utils import *
import os
# 加载环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # 读取本地 .env 文件，里面定义了 OPENAI_API_KEY
client = OpenAI()


#导入json文件,
file_path='./txt/中华人民共和国民法典_2020_05_28.txt'


def read_and_split_file(file_path, chunk_size=3000, overlap_size=200):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read().replace('\u3000', '')
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        # 更新起始位置，考虑重叠部分
        start = end - overlap_size
    return chunks
chunks = read_and_split_file(file_path, 500,20)
print("length of chunks",len(chunks))
first_50_texts=chunks
# 输出结果
# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i + 1}:\n{chunk}\n")
# print("first_50_texts",first_50_texts)
#向量化
def get_embeddings(texts, model="text-embedding-ada-002", dimensions=None):
    '''封装 OpenAI 的 Embedding 模型接口'''
    if model == "text-embedding-ada-002":
        dimensions = None
    if dimensions:
        data = client.embeddings.create(
            input=texts, model=model, dimensions=dimensions).data
    else:
        data = client.embeddings.create(input=texts, model=model).data
    return [x.embedding for x in data]

model = "text-embedding-3-large"
# from sentence_transformers import SentenceTransformer
#
#
# model = SentenceTransformer('bge-large-zh-v1.5')
# print(model)
# dimensions = 128
#
# if model == "text-embedding-ada-002" or model == "text-embedding-3-large":
#     try:
#         doc_vecs = get_embeddings(first_50_texts, model=model, dimensions=dimensions)
#         print("向量化成功，使用 " + model + " 模型")
#     except Exception as e:
#         print(f"向量化时出错: {e}")
# else:
#     try:
#         doc_vecs = [model.encode(doc, normalize_embeddings=True) for doc in first_50_texts]
#         print("向量化成功，使用bge-large-zh-v1.5模型")
#     except Exception as e:
#         print(f"向量化时出错: {e}")


# 灌入 chromadb 数据库
import chromadb
from chromadb.config import Settings


class MyVectorDBConnector:
    def __init__(self, collection_name, embedding_fn):
        chroma_client = chromadb.Client(Settings(allow_reset=True))

        # 为了演示，实际不需要每次 reset()
        chroma_client.reset()

        # 创建一个 collection
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name)
        self.embedding_fn = embedding_fn

    def add_documents(self, documents):
        '''向 collection 中添加文档与向量'''
        self.collection.add(
            embeddings=self.embedding_fn(documents),  # 每个文档的向量
            documents=documents,  # 文档的原文
            ids=[f"id{i}" for i in range(len(documents))]  # 每个文档的 id
        )

    def search(self, query, top_n):
        '''检索向量数据库'''
        results = self.collection.query(
            query_embeddings=self.embedding_fn([query]),
            n_results=top_n
        )
        return results

import gc

class MyVectorDBConnector2:
    def __init__(self, collection_name, embedding_fn):
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        # 为了演示，实际不需要每次 reset()
        self.chroma_client.reset()
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        self.embedding_fn = embedding_fn

    def batch_add_documents(self, documents, batch_size=10):
        '''分批向 collection 中添加文档与向量'''
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            try:
                embeddings = self.embedding_fn(batch_docs)
                ids = [f"id{j}" for j in range(i, i + len(batch_docs))]
                self.collection.add(
                    embeddings=embeddings,
                    documents=batch_docs,
                    ids=ids
                )
                print(f"Batch {i // batch_size + 1} added successfully")
            except Exception as e:
                print(f"Error adding batch {i // batch_size + 1}: {e}")
            finally:
                # 清理不再需要的资源
                del batch_docs
                del embeddings
                del ids
                gc.collect()

    def search(self, query, top_n):
        '''检索向量数据库'''
        query_embeddings = self.embedding_fn([query])
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=top_n
        )
        # 清除查询向量提前释放内存
        del query_embeddings
        gc.collect()

        return results

# 实例化向量数据库连接器
vector_db = MyVectorDBConnector("demo", get_embeddings)

# 向向量数据库中添加文档
vector_db.add_documents(first_50_texts)

# 查询

queries = ["民法典颁布时间？", "知识产权相关", "marriage"]
for user_query in queries:
    results = vector_db.search(user_query, top_n=3)
    print(f"Query: {user_query}")
    if results and 'documents' in results:
        for para in results['documents'][0]:
            print(para + "\n")
    else:
        print("查询失败或没有结果\n")

#查询大模型
def get_completion(prompt, model="gpt-4-turbo"):
    '''封装 openai 接口'''
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

def build_prompt(prompt_template, **kwargs):
    '''将 Prompt 模板赋值'''
    inputs = {}
    for k, v in kwargs.items():
        if isinstance(v, list) and all(isinstance(elem, str) for elem in v):
            val = '\n\n'.join(v)
        else:
            val = v
        inputs[k] = val
    return prompt_template.format(**inputs)

prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。

已知信息:
{context}

用户问：
{query}

如果已知信息不包含用户问题的答案，或者已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。
请不要输出已知信息中不包含的信息或答案。
请用中文回答用户问题。
"""

user_query = "民法典是哪年颁布的？"
user_query = "什么是知识产权？"
user_query = "婚姻相关条款"
search_results = vector_db.search(user_query, 5)

# 2. 构建 Prompt
prompt = build_prompt(prompt_template, context=search_results, query=user_query)
print("===Prompt===")
print(prompt)

# 3. 调用 LLM
response = get_completion(prompt)

print("===回复===")
print(response)