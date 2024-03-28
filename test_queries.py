import chromadb

from embeddings.embedding_functions import AWSEmbeddingFunction

# Initialize the chromadb directory, and client.
print("Initializing ChromaDB...")
client = chromadb.PersistentClient(path="./chromadb")
collection = client.get_collection(
    name="cheesecake-blog-aws", embedding_function=AWSEmbeddingFunction()
)
print("ChromaDB initialized.\n")

#### Query 1 ####

# Print results for a query searching by id.
# results = collection.get(
#     ids=["34210583", "34210874"],
#     include=["metadatas", "documents", "embeddings"]
# )
#
# for i in range(0, len(results["ids"])):
#     print("id: ", results["ids"][i])
#     print("metadatas: ", results["metadatas"][i])
#     print("documents: ", results["documents"][i])
#     print("embeddings: ", results["embeddings"][i])
#     print(f'embedding length: {len(results["embeddings"][i])} \n', )

#### Query 2 ####

print("Initializing embedding model")
embedding_model = AWSEmbeddingFunction()
print("Embedding model initialized. \n")

# query_texts = ["What is the meaning of life?"]
# query_texts = ["How to get started with vector databases?"]
query_texts = ["What is an interface builder?"]

embeddings = embedding_model.get_embedding(query_texts)

results = collection.query(
    query_embeddings=embeddings,
    n_results=5,
    include=["metadatas", "documents", "embeddings", "distances"],
)

print("##### Query Results #####")
print("Query text: ", query_texts, "\n")
for i in range(0, len(results["ids"][0])):
    print("documents: ", results["documents"][0][i])
    print("id: ", results["ids"][0][i])
    print("distance: ", results["distances"][0][i])
    print("metadata: ", results["metadatas"][0][i])
    print("embedding: ", results["embeddings"][0][i])
    print(
        f'embedding length: {len(results["embeddings"][0][i])} \n',
    )
