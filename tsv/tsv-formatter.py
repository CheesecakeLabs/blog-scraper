import chromadb
import csv

client = chromadb.PersistentClient(path="../chromadb")
collection = client.get_collection(name=f"cheesecake-blog")
results = collection.get(include=["documents", "embeddings", "metadatas"])

metadata = [
    {"id": id, "document": doc, **meta}
    for id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"])
]

with open("embeddings.tsv", "w", encoding="utf-8") as f:
    for embedding in results["embeddings"]:
        f.write("\t".join(map(str, embedding)) + "\n")

# Extracting keys from the first item of combined_metadata as headers
headers = metadata[0].keys()

with open("metadata.tsv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers, delimiter="\t")
    writer.writeheader()
    for data in metadata:
        writer.writerow(data)
