import os
import glob
import subprocess

# Đường dẫn đến thư mục chứa data
DATA_DIR = "data"

def check_libreoffice():
    try:
        subprocess.run(["libreoffice", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def convert_to_docx():
    if not check_libreoffice():
        print("LỖI: Chưa cài đặt LibreOffice. Vui lòng chạy lệnh:")
        print("sudo apt install libreoffice -y")
        return

    # Tìm tất cả file .doc
    doc_files = glob.glob(os.path.join(DATA_DIR, "*.doc"))

    if not doc_files:
        print(f"Không tìm thấy file .doc nào trong thư mục {DATA_DIR}")
        return

    print(f"--> Tìm thấy {len(doc_files)} file .doc. Đang bắt đầu chuyển đổi...")

    success_count = 0

    for file_path in doc_files:
        filename = os.path.basename(file_path)
        docx_name = filename + "x" # .doc -> .docx
        docx_path = file_path + "x"

        # Kiểm tra nếu file docx đã tồn tại thì bỏ qua
        if os.path.exists(docx_path):
            print(f"[Bỏ qua] {filename} (Đã có file .docx)")
            continue

        print(f"Đang convert: {filename} ...")

        try:
            # Lệnh chạy LibreOffice headless để convert
            # --convert-to docx: định dạng đích
            # --outdir: thư mục xuất file (lưu ngay tại chỗ)
            cmd = [
                "libreoffice",
                "--headless",
                "--convert-to", "docx",
                file_path,
                "--outdir", DATA_DIR
            ]

            # Chạy lệnh hệ thống
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                print(f"  OK -> {docx_name}")
                success_count += 1

                os.remove(file_path)
            else:
                print(f"  LỖI: Không thể convert {filename}")
                print(result.stderr.decode())

        except Exception as e:
            print(f"  LỖI Exception: {e}")

    print("\n" + "="*30)
    print(f"Hoàn tất! Đã chuyển đổi thành công {success_count}/{len(doc_files)} file.")

if __name__ == "__main__":
    convert_to_docx()