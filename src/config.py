import os

# Đường dẫn gốc của dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Đường dẫn dữ liệu
DATA_DIR = os.path.join(BASE_DIR, "data")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "faiss_index")

# Cấu hình model
EMBEDDING_MODEL_NAME = "keepitreal/vietnamese-sbert" 
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
LLM_MODEL_NAME = "qwen2.5:3b"
LLM_TEMPERATURE = 0.3