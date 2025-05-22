import io
from typing import Optional

def extract_text_from_file(file) -> Optional[str]:
    """Extract text from uploaded file based on its type."""
    if file is None:
        return None
    
    try:
        # Get file extension
        file_extension = '.' + file.name.split('.')[-1].lower()
        
        # Process TXT and MD files
        if file_extension in ['.txt', '.md']:
            return file.getvalue().decode('utf-8')
        
        # Process PDF files
        elif file_extension == '.pdf':
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                return "Error: PyPDF2 library not installed. Install with 'pip install PyPDF2'"
        
        # Process DOC/DOCX files
        elif file_extension in ['.doc', '.docx']:
            try:
                import docx
                doc = docx.Document(io.BytesIO(file.getvalue()))
                text = ""
                for para in doc.paragraphs:
                    text += para.text + "\n"
                return text
            except ImportError:
                return "Error: python-docx library not installed. Install with 'pip install python-docx'"
        else:
            return f"Unsupported file type: {file_extension}"
    
    except Exception as e:
        return f"Error processing file: {str(e)}"