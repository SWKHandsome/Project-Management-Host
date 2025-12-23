"""Manual file import script to test the system"""
import sys
sys.path.append('backend')

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from backend.config import Config
from backend.utils.db_connection import db
from backend.services.evaluator import AssignmentEvaluator
from backend.services.extraction import DataExtractor
from backend.utils.helpers import parse_student_info_from_filename, create_submission_record

# Initialize
creds = service_account.Credentials.from_service_account_file(
    'config/credentials.json',
    scopes=['https://www.googleapis.com/auth/drive.readonly']
)
service = build('drive', 'v3', credentials=creds)
evaluator = AssignmentEvaluator()
extractor = DataExtractor()

# Get files from Drive
folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
print(f"Checking folder: {folder_id}")

result = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields='files(id, name, mimeType, size, createdTime, modifiedTime)'
).execute()

files = result.get('files', [])
print(f"\nFound {len(files)} file(s)")

for file_info in files:
    print(f"\nProcessing: {file_info['name']}")
    
    # Parse student info
    student_info = parse_student_info_from_filename(file_info['name'])
    print(f"  Student ID: {student_info['student_id']}")
    print(f"  Student Name: {student_info['student_name']}")
    
    # Create submission record
    submission_data = create_submission_record(file_info, student_info)
    submission_data['file_content'] = "Sample content for testing"
    
    # Check if already exists
    existing = db.submissions.find_one({'file_id': file_info['id']})
    if existing:
        print(f"  ⚠ Already in database, skipping")
        continue
    
    # Insert into database
    result = db.submissions.insert_one(submission_data)
    submission_data['_id'] = result.inserted_id
    print(f"  ✓ Saved to database")
    
    # Evaluate
    print(f"  ⚙ Evaluating...")
    assessment = evaluator.evaluate(submission_data)
    
    # Update with assessment
    db.submissions.update_one(
        {'_id': result.inserted_id},
        {
            '$set': {
                'assessment': assessment,
                'status': 'evaluated',
                'evaluated_at': datetime.utcnow()
            }
        }
    )
    
    print(f"  ✓ Evaluation complete - Score: {assessment['total_score']}/100")

print("\n✓ Import complete!")
