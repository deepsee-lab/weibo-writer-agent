from pymilvus import MilvusClient
from apps.vector.api import get_embeddings

client = MilvusClient(
    uri="http://localhost:19530",
    token="root:Milvus"
)


class MilvusClass:
    def __init__(self, kb_id: str):
        self.kb_id = kb_id

    def create_collection(self, dim: int):
        if not client.has_collection(self.kb_id):
            client.create_collection(
                collection_name=self.kb_id,
                dimension=dim
            )

    def insert_data(self, data):
        client.insert(collection_name=self.kb_id, data=data)

    def search_vectors(self, query_vectors, top_k, filter, output_fields):
        results = client.search(
            collection_name=self.kb_id,
            data=query_vectors,
            filter=filter,
            limit=top_k,
            output_fields=output_fields,
        )
        return results


def run():
    # init
    kb_id = 'uuid0000000000000000000000000000'
    dim = 1024
    milvus_class = MilvusClass(kb_id)
    print('init ok')
    # create_collection
    milvus_class.create_collection(dim=dim)
    # insert_data
    sentences = [
        '你好',
        '好的',
        '谢谢',
    ]
    vectors = get_embeddings(sentences)
    data = [
        {"id": i, "vector": vectors[i], "text": sentences[i], "subject": "biology"}
        for i in range(len(vectors))
    ]
    milvus_class.insert_data(data)
    print('insert_data ok')
    # search
    query = '五星、天安门'
    query_vectors = get_embeddings([query])
    res = client.search(
        collection_name=kb_id,
        data=query_vectors,
        # filter="subject == 'biology'",
        limit=2,
        output_fields=["text", "subject"],
    )
    print('search res: {}'.format(res))


if __name__ == "__main__":
    run()
