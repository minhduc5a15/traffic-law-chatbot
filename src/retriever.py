from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import VECTOR_DB_DIR, EMBEDDING_MODEL_NAME

class TrafficLawRetriever:
    def __init__(self):
        print("Dang tai model embedding va Vector DB...")
        try:
            self.embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

            # Load FAISS index tu disk
            self.db = FAISS.load_local(
                VECTOR_DB_DIR,
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
            print("Da tai Vector DB thanh cong!")
        except Exception as e:
            print(f"Loi khi tai Vector DB: {e}")
            self.db = None

    def search(self, query, k=10):
        """
        Tim kiem k doan van ban lien quan nhat voi query
        """
        if not self.db:
            return []

        results = self.db.similarity_search(query, k=k)

        return results