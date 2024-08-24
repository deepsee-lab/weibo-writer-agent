from typing import List
from langchain_community import embeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOllama

class FileLoadFactory:
    @staticmethod
    def get_loader(filename: str):
        ext = get_file_extension(filename)
        if ext == "pdf":
            return PyPDFLoader(filename)
        elif ext == "docx" or ext == "doc":
            return UnstructuredWordDocumentLoader(filename)
        else:
            raise NotImplementedError(f"File extension {ext} not supported.")

def get_file_extension(filename: str) -> str:
    return filename.split(".")[-1]

def load_docs(filename: str) -> List[Document]:
    file_loader = FileLoadFactory.get_loader(filename)
    pages = file_loader.load_and_split()
    return pages

def ask_docment(
        filename: str,
        query: str,
) -> str:
    """根据一个PDF文档的内容，回答一个问题"""

    raw_docs = load_docs(filename)
    if len(raw_docs) == 0:
        return "抱歉，文档内容为空"
    #print(raw_docs)
    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=200,
                        chunk_overlap=60,
                        length_function=len,
                        add_start_index=True,
                    )
    documents = text_splitter.split_documents(raw_docs)
    if documents is None or len(documents) == 0:
        return "无法读取文档内容"
    db = Chroma.from_documents(documents, embeddings.OllamaEmbeddings(model='nomic-embed-text'),persist_directory='data')
    db.persist()
    qa_chain = RetrievalQA.from_chain_type(
        llm = ChatOllama(model="qwen2:7b"),  # 语言模型
        chain_type="stuff",  # prompt的组织方式，后面细讲
        retriever=db.as_retriever()  # 检索器
    )
    response = qa_chain.run(query)
    return response


if __name__ == "__main__":
    filename = "2023年10月份销售计划.pdf"
    #filename = "../data/G-02C-BCD18-1.8V_5V-1P6M-HV_P_SUB_GENERICIII-EDR_CHARACTERIZATION_REPORT-8N-Ver.0.2_P1.pdf"
    #query = "销售额达标的标准是多少？"G-02C-BCD18-1.8V_5V-1P6M-HV_P_SUB_GENERICIII-EDR_CHARACTERIZATION_REPORT-8N-Ver.0.2_P1.pdf
    query = "经营和财务能力的标准是什么？"
    #query = "当Vds=-6V 时  的IOFF是多少"
    response = ask_docment(filename, query)
    print(response)