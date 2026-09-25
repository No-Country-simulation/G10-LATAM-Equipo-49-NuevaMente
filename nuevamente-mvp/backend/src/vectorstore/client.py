import chromadb
from src.core.config import settings

COLLECTION_NAME = "nuevamente_documents"  # una sola colección, filtrada por doc_id


def get_chroma_client():
    return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)
