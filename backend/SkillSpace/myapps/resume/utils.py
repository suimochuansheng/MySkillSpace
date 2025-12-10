# backend/myapps/resume/utils.py
import pdfplumber


def extract_text_from_file(uploaded_file):
    """
    从上传的文件中提取文本
    支持 .txt, .pdf
    """
    filename = uploaded_file.name.lower()
    text = ""

    try:
        if filename.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        elif filename.endswith(".txt") or filename.endswith(".md"):
            text = uploaded_file.read().decode("utf-8")
        else:
            return None  # 暂不支持的格式

        return text.strip()
    except Exception as e:
        print(f"解析出错: {e}")
        return ""
