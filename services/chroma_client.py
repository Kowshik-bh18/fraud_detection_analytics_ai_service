from chromadb.config import Settings
import chromadb


class ChromaClient:
    def __init__(self):
        self.client = chromadb.Client(
            Settings(persist_directory="chroma_db")
        )

        self.collection = self.client.get_or_create_collection(
            name="fraud_collection"
        )

    def add_data(self, texts):
        existing_count = self.collection.count()

        for i, text in enumerate(texts):
            self.collection.add(
                documents=[text],
                ids=[str(existing_count + i)]
            )

    def query(self, query_text):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=3
        )
        return results["documents"]


# ✅ ADD THIS (IMPORTANT)
chroma_instance = ChromaClient()

def query_documents(text):
    return chroma_instance.query(text)