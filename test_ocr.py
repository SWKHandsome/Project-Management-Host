"""Test OCR extraction from PNG file"""
import sys
sys.path.append('backend')

from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
from services.extraction import DataExtractor

# Google Drive setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'config/credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

# Find the JPG file
folder_id = '15TRPlXKqJH0YrqBZe-gDkBXNF6Hn-h4v2kIBNV8DrtQXftFgL7whtWBrZabdyoyZ89mK6CB9'
results = service.files().list(
    q=f"'{folder_id}' in parents and name contains '.jpg'",
    fields="files(id, name)").execute()

files = results.get('files', [])

if files:
    file = files[0]
    print(f"Testing OCR on: {file['name']}")
    
    # Download file
    request = service.files().get_media(fileId=file['id'])
    file_content = request.execute()
    
    # Extract text using OCR
    extractor = DataExtractor()
    
    # Save image temporarily to check it
    from PIL import Image
    img = Image.open(io.BytesIO(file_content))
    print(f"\nImage info:")
    print(f"  Size: {img.size}")
    print(f"  Mode: {img.mode}")
    print(f"  Format: {img.format}")
    
    text = extractor.extract_assignment_content(file_content, file['name'])
    
    print("\n" + "="*60)
    print("EXTRACTED TEXT:")
    print("="*60)
    print(text)
    print("="*60)
    print(f"\nTotal characters: {len(text)}")
    print(f"Total words: {len(text.split())}")
else:
    print("No PNG file found")
