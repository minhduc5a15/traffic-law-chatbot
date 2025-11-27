import os
import glob
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    DATA_DIR,
    VECTOR_DB_DIR,
    EMBEDDING_MODEL_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

# Import module xử lý dữ liệu chúng ta vừa test thành công
from data_processing.parsing import extract_metadata_and_chunk

def clean_filename(file_path):
    """
    Lấy tên file làm mã nguồn (Source ID).
    VD: 'data/36_2024_QH15.docx' -> '36/2024/QH15'
    """
    basename = os.path.basename(file_path)
    name = os.path.splitext(basename)[0]
    # Thay dấu gạch dưới thành gạch chéo cho giống ký hiệu văn bản luật
    clean_name = name.replace("_", "/")

    # Loại bỏ các mã hash phía sau (nếu có) do quá trình upload file
    if "_m_" in clean_name:
        clean_name = clean_name.split("/m/")[0]

    return clean_name

def create_db():
    print(f"--> BẮT ĐẦU QUÁ TRÌNH NẠP DỮ LIỆU TỪ: {DATA_DIR}")

    # 1. Quét tất cả file .docx (Đảm bảo bạn đã convert hết .doc sang .docx)
    docx_files = glob.glob(os.path.join(DATA_DIR, "*.docx"))

    if not docx_files:
        print("CẢNH BÁO: Không tìm thấy file .docx nào! Hãy kiểm tra lại thư mục data.")
        return

    all_documents = []

    # 2. Xử lý từng file
    for file_path in docx_files:
        try:
            print(f"Đang xử lý: {os.path.basename(file_path)} ...")
            source_name = clean_filename(file_path)

            # --- parsing ---
            # trả về danh sách các Document đã được cắt theo Chương/Điều và có Metadata
            article_docs = extract_metadata_and_chunk(file_path, source_name)

            # --- check ---
            # cần cắt nhỏ tiếp những Điều luật rất dài
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )

            for doc in article_docs:
                if len(doc.page_content) > CHUNK_SIZE:
                    # NẾU PHẢI CẮT NHỎ:
                    sub_chunks = text_splitter.split_documents([doc])

                    article_header = f"{doc.metadata.get('dieu', '')}. {doc.metadata.get('tieu_de_dieu', '')}"

                    final_sub_chunks = []
                    for i, sub_doc in enumerate(sub_chunks):
                        if i > 0: # Mảnh thứ 2 trở đi
                            sub_doc.page_content = f"(Tiếp theo {article_header})\n{sub_doc.page_content}"

                        final_sub_chunks.append(sub_doc)

                    all_documents.extend(final_sub_chunks)
                else:
                    # Nếu điều luật ngắn, giữ nguyên
                    all_documents.append(doc)

        except Exception as e:
            print(f"!!! Lỗi khi đọc file {file_path}: {e}")

    # 3. Tổng kết và Lưu trữ
    print(f"\n--> TỔNG KẾT: Đã tạo ra {len(all_documents)} chunks dữ liệu.")

    if all_documents:
        print(f"--> Đang khởi tạo model Embedding ({EMBEDDING_MODEL_NAME})...")
        try:
            embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

            print("--> Đang tạo Vector Database (FAISS)...")
            db = FAISS.from_documents(all_documents, embedding_model)

            db.save_local(VECTOR_DB_DIR)
            print(f"--> THÀNH CÔNG! Database đã được lưu tại thư mục: '{VECTOR_DB_DIR}'")

        except Exception as e:
            print(f"Lỗi khi tạo Vector DB: {e}")
    else:
        print("Không có dữ liệu đầu ra. Vui lòng kiểm tra lại file nguồn.")

if __name__ == "__main__":
    create_db()