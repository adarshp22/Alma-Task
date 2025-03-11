async def process_file(file: UploadFile) -> str:
    """Handles PDF/DOCX/TXT parsing"""
    content = await file.read()
    
    if file.filename.endswith(".pdf"):
        from pdfminer.high_level import extract_text
        return extract_text(io.BytesIO(content))
    
    elif file.filename.endswith(".docx"):
        from docx2txt import process
        return process(io.BytesIO(content))
    
    return content.decode("utf-8")
