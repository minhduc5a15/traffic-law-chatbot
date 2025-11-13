import fitz 
from langchain_text_splitters import RecursiveCharacterTextSplitter 
import os

PDF_PATH = "data/luat_gtdb_hop_nhat.pdf"

def load_and_split_pdf(file_path):

    print(f"Bắt đầu đọc file: {file_path}")
    doc = fitz.open(file_path)

    full_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  
        full_text += page.get_text()

    print(f"Đã đọc xong {len(doc)} trang.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""] 
    )

    chunks = text_splitter.split_text(full_text)

    print(f"Đã chia văn bản thành {len(chunks)} chunks.")
    doc.close()

    return chunks

if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):
        print(f"Lỗi: Không tìm thấy file PDF tại '{PDF_PATH}'")
    else:
        chunks = load_and_split_pdf(PDF_PATH)

        print("\n--- 3 chunks đầu tiên (để kiểm tra) ---")
        for i, chunk in enumerate(chunks[:3]):
            print(f"--- CHUNK {i+1} ---")
            print(chunk)
            print("-" * 20)