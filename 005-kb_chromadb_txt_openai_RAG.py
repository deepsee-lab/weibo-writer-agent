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
import chromadb
from chromadb.config import Settings
import gc
# 加载环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # 读取本地 .env 文件，里面定义了 OPENAI_API_KEY
client = OpenAI()




class MyPersistentVectorDBConnector:
    def __init__(self, collection_name, embedding_fn, persist_dir="./chroma_db"):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.embedding_fn = embedding_fn

        # Ensure the persistence directory exists
        os.makedirs(persist_dir, exist_ok=True)

        # Initialize the Chroma client with persistence settings
        self.chroma_client = chromadb.Client(Settings(
            allow_reset=True,
            persist_directory=persist_dir
        ))

        # Reset if needed (useful for development)
        # self.chroma_client.reset()  # Be careful with this in production

        # Load or create the collection
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

    def add_documents(self, documents):
        '''向 collection 中添加文档与向量'''
        embeddings = self.embedding_fn(documents)
        ids = [f"id{i}" for i in range(len(documents))]
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids
        )

    def search(self, query, top_n):
        '''检索向量数据库'''
        results = self.collection.query(
            query_embeddings=self.embedding_fn([query]),
            n_results=top_n
        )
        return results

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

class MyVectorDBConnector_save:
    def __init__(self, collection_name, embedding_fn, persist_dir):
        # 设置持久化数据的目录
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)

        # 初始化ChromaDB客户端，设置持久化存储配置
        self.chroma_client = chromadb.PersistentClient(path=persist_dir)

        # 获取或创建一个集合
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name
        )

        self.embedding_fn = embedding_fn

    def add_documents(self, documents):
        ''' 向集合中添加文档和对应的向量 '''
        embeddings = self.embedding_fn(documents)
        ids = [f"id{i}" for i in range(len(documents))]
        self.collection.add(
            embeddings=embeddings,  # 文档的向量表示
            documents=documents,    # 文档的原文
            ids=ids                 # 文档的唯一标识符
        )

    def batch_add_documents(self, documents, batch_size=10):
        ''' 分批向集合中添加文档和对应的向量 '''
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
        ''' 检索和查询最相似的前N个文档 '''
        query_embeddings = self.embedding_fn([query])
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=top_n
        )
        return results
# 实例化向量数据库连接器
persist_dir = "./demo-laws-db"
vector_db = MyVectorDBConnector_save("demo", get_embeddings, persist_dir)

# 向向量数据库中添加文档


# 查询
queries = ["中国民法典施行日期", "什么是知识产权相关", "侵犯知识产权受什么处罚"]
for user_query in queries:
    results = vector_db.search(user_query, top_n=20)
    print(f"Query: {user_query}")
    if results and 'documents' in results:
        for para in results['documents'][0]:
            print(para + "\n")
    else:
        print("查询失败或没有结果\n")



#查询大模型
def get_completion(prompt, model="gpt-4-turbo"):    #model="claude-3-5-sonnet-20240620"
    #封装 openai 接口
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

def build_prompt(prompt_template, **kwargs):
    #将 Prompt 模板赋值
    inputs = {}
    for k, v in kwargs.items():
        if isinstance(v, list) and all(isinstance(elem, str) for elem in v):
            val = '\n\n'.join(v)
        else:
            val = v
        inputs[k] = val
    return prompt_template.format(**inputs)

prompt_template = """
你是一位法律顾问。
你的任务是根据下述给定的已知信息回答用户问题。

已知信息:
{context}

用户问：
{query}

如果已知信息不包含用户问题的答案，或者已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。
请不要输出已知信息中不包含的信息或答案。
请用中文回答用户问题。
指出回答的来源。
"""

# user_query = "民法典是哪年颁布的？"
# user_query = "什么是知识产权"
user_query = "婚姻相关条款"
search_results = vector_db.search(user_query, 30)
search_results=search_results["documents"]

# 2. 构建 Prompt
prompt = build_prompt(prompt_template, context=search_results, query=user_query)
print("===Prompt===")
print(prompt)

# 3. 调用 LLM
response = get_completion(prompt)

print("===回复===")
print(response)
