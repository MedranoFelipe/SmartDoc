import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("ENDPOINT")
KEY = os.getenv("KEY")

client = DocumentAnalysisClient(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(KEY)
)

def analyze_bytes_document(document_bytes, model_id="prebuilt-read"):
    """
    Envía los bytes de un documento a Azure Document Intelligence
    y devuelve el resultado como dict.
    """
    poller = client.begin_analyze_document(
        model_id=model_id,
        document=document_bytes
    )
    result = poller.result()
    return result.to_dict()
