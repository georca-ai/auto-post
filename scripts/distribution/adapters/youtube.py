"""Optional official-client YouTube upload adapter."""
import os

def metadata(a,d):
    copy=a['localizations'][d['locale']]; privacy=d.get('options',{}).get('privacy','private')
    if privacy not in {'private','unlisted','public'}: raise ValueError('Invalid privacy')
    return {'snippet':{'title':copy['title'],'description':copy['body'],'defaultLanguage':d['locale']},'status':{'privacyStatus':privacy}}

def execute(a,d):
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        credential_path=os.environ[d['options']['credentials_env']]
        credentials=Credentials.from_authorized_user_file(credential_path,scopes=['https://www.googleapis.com/auth/youtube.upload'])
        body=metadata(a,d)
    except (ImportError,KeyError,ValueError,OSError): return {'state':'blocked','reason':'Install YouTube extras and configure authorized OAuth credentials'}
    try:
        client=build('youtube','v3',credentials=credentials,cache_discovery=False)
        upload=client.videos().insert(part='snippet,status',body=body,media_body=MediaFileUpload(a['assets'][0]['path'],resumable=True))
        response=None
        while response is None:
            _,response=upload.next_chunk(num_retries=0)
        identifier=response['id']
        return {'state':'published','external_id':identifier,'url':'https://www.youtube.com/watch?v='+identifier,'evidence':'Upload receipt; visibility and processing must be checked separately'}
    except Exception: return {'state':'unknown','reason':'Upload outcome uncertain; inspect account before retry'}
