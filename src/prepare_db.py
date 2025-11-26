import os
import glob
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import (
    DATA_DIR,
    VECTOR_DB_DIR,
    EMBEDDING_MODEL_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def create_db():
    # 1. Load data
    print("dang tai du lieu tu file .doc...")
    doc_files = glob.glob(os.path.join(DATA_DIR, "*.doc"))
    documents = []

    if not doc_files:
        print("Khong tim thay file .doc nao trong thu muc data/")
        return

    for file_path in doc_files:
        try:
            print(f"Dang xu ly file: {os.path.basename(file_path)}")
            # Dùng UnstructuredWordDocumentLoader để đọc .doc
            loader = UnstructuredWordDocumentLoader(file_path)
            documents.extend(loader.load())
        except Exception as e:
            print(f"Loi khi doc file {file_path}: {e}")

    print(f"Da tai xong {len(documents)} tai lieu.")

    # 2. Split text (Chia nho van ban)
    print("Dang chia nho van ban (Chunking)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Da chia thanh {len(chunks)} chunks.")

    # 3. Embed & Vector Store (Tao vector va luu vao FAISS)
    print(f"Dang tai model embedding: {EMBEDDING_MODEL_NAME}...")
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    print("Dang tao Vector Database (co the mat vai phut)...")
    db = FAISS.from_documents(chunks, embedding_model)

    # 4. Save to disk
    db.save_local(VECTOR_DB_DIR)
    print(f"Thanh cong! Vector DB da duoc luu tai: {VECTOR_DB_DIR}")


if __name__ == "__main__":
    create_db()
