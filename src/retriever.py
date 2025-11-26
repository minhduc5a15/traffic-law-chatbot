from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import VECTOR_DB_DIR, EMBEDDING_MODEL_NAME

class TrafficLawRetriever:
    def __init__(self):
        print("Dang tai model embedding va Vector DB...")
        self.embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

        # Load FAISS index tu disk
        try:
            self.db = FAISS.load_local(
                VECTOR_DB_DIR,
                self.embedding_model,
                allow_dangerous_deserialization=True # Can thiet khi load file pickle
            )
            print("Da tai Vector DB thanh cong!")
        except Exception as e:
            print(f"Loi khi tai Vector DB: {e}")
            self.db = None

    def search(self, query, k=3):
        """
        Tim kiem k doan van ban lien quan nhat voi query
        """
        if not self.db:
            return []

        # Search similarity
        results = self.db.similarity_search_with_score(query, k=k)

        # Format ket qua tra ve
        relevant_docs = []
        for doc, score in results:
            relevant_docs.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "score": score
            })
        return relevant_docs