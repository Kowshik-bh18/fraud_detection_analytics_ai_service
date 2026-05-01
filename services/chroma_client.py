from chromadb.config import Settings
import chromadb
import os
import logging


class ChromaClient:
    def __init__(self):
        try:
            # ✅ Use Railway persistent storage
            persist_dir = os.getenv("CHROMA_DIR", "/data")

            self.client = chromadb.Client(
                Settings(persist_directory=persist_dir)
            )

            self.collection = self.client.get_or_create_collection(
                name="fraud_collection"
            )

            logging.info(f"✅ ChromaDB initialized at {persist_dir}")

        except Exception as e:
            logging.error(f"❌ ChromaDB init failed: {e}")
            self.client = None
            self.collection = None

    def add_data(self, texts):
        if not self.collection:
            return

        try:
            existing_count = self.collection.count()

            for i, text in enumerate(texts):
                self.collection.add(
                    documents=[text],
                    ids=[str(existing_count + i)]
                )

        except Exception as e:
            logging.error(f"Chroma add error: {e}")

    def query(self, query_text):
        if not self.collection:
            return []

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=3
            )
            return results.get("documents", [])

        except Exception as e:
            logging.error(f"Chroma query error: {e}")
            return []


# ✅ Singleton instance (correct)
chroma_instance = ChromaClient()


def query_documents(text):
    return chroma_instance.query(text)