import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""

        for page in doc:
            text += page.get_text()

        return text.strip()

    except Exception as e:
        print("PDF Parsing Error:", e)
        return ""