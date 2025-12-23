from google.oauth2 import service_account
from googleapiclient.discovery import build

# Initialize credentials
creds = service_account.Credentials.from_service_account_file(
    'config/credentials.json',
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)

service = build('drive', 'v3', credentials=creds)

# Test folder access
folder_id = '15TRPlXKqJH0YrqBZe-gDkBXNF6Hn-h4v2kIBNV8DrtQXftFgL7whtWBrZabdyoyZ89mK6CB9'

try:
    result = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields='files(id, name, mimeType, size, createdTime)'
    ).execute()
    
    files = result.get('files', [])
    print(f'\n✓ Successfully connected to Google Drive')
    print(f'✓ Files found in folder: {len(files)}')
    
    if files:
        print('\nFiles:')
        for f in files:
            print(f"  - {f['name']} ({f.get('mimeType', 'unknown')})")
    else:
        print('\n⚠ No files found in the folder')
        print('  Possible reasons:')
        print('  1. The folder is empty')
        print('  2. The service account does not have access to the folder')
        print(f'  3. The folder ID is incorrect')
        
except Exception as e:
    print(f'\n✗ Error accessing Google Drive: {e}')
