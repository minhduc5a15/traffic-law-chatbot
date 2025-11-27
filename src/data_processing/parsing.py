import re
from docx import Document as Docx
from langchain_core.documents import Document
from .cleaning import clean_text


def read_docx_to_text(file_path):
    """Đọc raw text từ file .docx"""
    doc = Docx(file_path)
    # Nối các đoạn văn lại, dùng \n để ngắt dòng
    return "\n".join(p.text for p in doc.paragraphs)


def create_document(source, chap, chap_title, art_id, art_title, content_lines):
    """Đóng gói thông tin thành đối tượng Document"""
    content_str = "\n".join(content_lines).strip()

    # Metadata
    metadata = {
        "source": source,  # Tên văn bản (VD: 36/2024/QH15)
        "chuong": chap,  # VD: Chương I
        "tieu_de_chuong": chap_title,
        "dieu": art_id,  # VD: Điều 1
        "tieu_de_dieu": art_title,  # VD: Phạm vi điều chỉnh
        # Field đặc biệt để Vector Search tìm kiếm hiệu quả hơn:
        # Gom Tiêu đề + Nội dung vào một chỗ để bot hiểu ngữ cảnh
        "search_content": f"{art_id}. {art_title}\n{content_str}"
    }

    # Ở đây ta dùng nội dung chi tiết của điều luật
    return Document(page_content=content_str, metadata=metadata)


def extract_metadata_and_chunk(file_path, source_name):
    """
    Hàm chính: Đọc file -> Làm sạch -> Cắt theo Chương/Điều
    """
    raw_text = read_docx_to_text(file_path)
    cleaned_text = clean_text(raw_text)

    documents = []

    # --- Biến trạng thái (State) ---
    # Vì đọc tuần tự từng dòng từ trên xuống dưới, ta cần nhớ mình đang ở Chương nào
    current_chapter = "Không có chương"
    current_chapter_title = ""
    current_article_id = None
    current_article_title = ""
    current_article_content = []

    # --- Regex (Biểu thức tìm kiếm) ---
    # Tìm dòng bắt đầu bằng "Chương I", "Chương II"...
    chapter_pattern = re.compile(r"^(Chương\s+[IVXLCDM0-9]+)[.:]?\s*(.*)$", re.IGNORECASE)
    # Tìm dòng bắt đầu bằng "Điều 1.", "Điều 2 "...
    article_pattern = re.compile(r"^(Điều\s+\d+)[.\s]+(.*)$", re.IGNORECASE)

    lines = cleaned_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line: continue

        # 1. Nếu gặp CHƯƠNG mới
        chapter_match = chapter_pattern.match(line)
        if chapter_match:
            # Nếu đang gom dở một Điều luật cũ, hãy lưu nó lại trước
            if current_article_id:
                doc = create_document(
                    source_name, current_chapter, current_chapter_title,
                    current_article_id, current_article_title, current_article_content
                )
                documents.append(doc)
                # Reset trạng thái để đón Điều mới
                current_article_id = None
                current_article_content = []

            # Cập nhật thông tin Chương mới
            current_chapter = chapter_match.group(1).strip()
            current_chapter_title = chapter_match.group(2).strip()
            continue

        # 2. Nếu gặp ĐIỀU mới
        article_match = article_pattern.match(line)
        if article_match:
            # Lưu Điều luật cũ (nếu có)
            if current_article_id:
                doc = create_document(
                    source_name, current_chapter, current_chapter_title,
                    current_article_id, current_article_title, current_article_content
                )
                documents.append(doc)

            # Bắt đầu Điều mới
            current_article_id = article_match.group(1).strip()  # Lấy "Điều 1"
            current_article_title = article_match.group(2).strip()  # Lấy tiêu đề
            current_article_content = [line]  # Dòng đầu tiên chứa cả tên Điều

        else:
            # 3. Nếu là nội dung bình thường (Khoản, Điểm...)
            # Chỉ lưu nếu ta đã xác định được mình đang ở trong một Điều nào đó
            if current_article_id:
                current_article_content.append(line)

    # Lưu Điều cuối cùng (khi hết file)
    if current_article_id:
        doc = create_document(
            source_name, current_chapter, current_chapter_title,
            current_article_id, current_article_title, current_article_content
        )
        documents.append(doc)

    return documents
