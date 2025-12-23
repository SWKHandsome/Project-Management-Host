from pymongo import MongoClient

db = MongoClient('mongodb+srv://autoassess_user:xx05310705@autoassess.cop7vie.mongodb.net/?appName=AutoAssess')['autoassess']
sub = db.submissions.find_one({'file_name': 'swk_b111222b - teo Calvin.jpg'})

if sub:
    content = sub.get('file_content', '')
    print('='*60)
    print('EXTRACTED CONTENT:')
    print('='*60)
    print(content)
    print('='*60)
    print(f'\nLength: {len(content)} characters')
    print(f'Words: {len(content.split())} words')
    print(f'\nAssessment score: {sub.get("assessment", {}).get("total_score", 0)}/100')
else:
    print('File not found in database')
