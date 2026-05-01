from services.chroma_client import ChromaClient
import os


def load_data_to_chroma():
    chroma = ChromaClient()

    if chroma.collection.count() > 0:
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "data", "fraud_data.txt")

    with open(file_path, "r") as f:
        lines = f.readlines()

    texts = [line.strip() for line in lines if line.strip()]

    chroma.add_data(texts)