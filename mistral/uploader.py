import os
from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.models import File

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


#This is the first step 

def upload_pdf(filename, purpose="ocr"):
    """
    Upload a PDF to Mistral for OCR purposes and return the signed document URL.
    """
    with open(filename, "rb") as f:
        uploaded_pdf = client.files.upload(
            file={"file_name": os.path.basename(filename), "content": f.read()},
            purpose=purpose
        )
    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
    return signed_url.url

def list_uploaded_files():
    """
    List files already uploaded to Mistral.
    """
    return client.files.list()

# Dev-only / legacy function
def sdk_uploadpdf(filename="test.pdf", purpose="ocr"):
    """
    Upload a hardcoded file (for quick testing).
    """
    with open(filename, "rb") as f:
        created_file = client.files.upload(
            file=File(file_name=filename, content=f.read()),
            purpose=purpose
        )
    print(created_file)
