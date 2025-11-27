import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Chuẩn hóa và làm sạch văn bản thô.
    """
    if not text:
        return ""

    # 1. Chuẩn hóa Unicode (NFC) - Tránh lỗi font tiếng Việt
    text = unicodedata.normalize("NFC", text)

    # 2. Xóa các cụm từ tiêu đề/chân trang vô nghĩa thường gặp trong văn bản luật
    # Flag re.IGNORECASE để không phân biệt hoa thường
    patterns_to_remove = [
        r"CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\s*\n\s*Độc lập - Tự do - Hạnh phúc",
        r"QUỐC HỘI\s*\n\s*--------",
    ]

    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 3. Xử lý khoảng trắng và xuống dòng
    # Thay thế 3 dòng trống liên tiếp trở lên bằng 2 dòng (để tách đoạn)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Xóa khoảng trắng thừa ở đầu/cuối mỗi dòng
    lines = [line.strip() for line in text.split('\n')]

    # Nối lại: Bỏ qua các dòng trống vô nghĩa (nếu muốn giữ format đoạn thì cẩn thận chỗ này)
    # Ở đây ta giữ lại dòng trống để phân cách paragraph
    cleaned_text = '\n'.join(lines)

    return cleaned_text.strip()