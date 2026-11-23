"""TLS-only editorial email submission."""
import mimetypes
import os
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

def build_message(a,d):
    options=d['options']; copy=a['localizations'][d['locale']]
    message=EmailMessage()
    for key,value in {'From':options['sender'],'To':options['recipient'],'Subject':copy['title']}.items():
        if '\r' in value or '\n' in value: raise ValueError('Invalid email header')
        message[key]=value
    message['Message-ID']=make_msgid(); message.set_content(copy['body'])
    for asset in a['assets']:
        path=Path(asset['path']); mime=mimetypes.guess_type(path)[0] or 'application/octet-stream'
        major,minor=mime.split('/',1)
        message.add_attachment(path.read_bytes(),maintype=major,subtype=minor,filename=path.name)
    return message

def execute(a,d):
    options=d.get('options',{})
    try:
        host=options['host']; username=os.environ[options['username_env']]; password=os.environ[options['password_env']]
        message=build_message(a,d)
    except (KeyError,ValueError): return {'state':'blocked','reason':'SMTP configuration, credentials or headers invalid'}
    client=None
    sending=False
    try:
        client=smtplib.SMTP_SSL(host,int(options.get('port',465)),context=ssl.create_default_context(),timeout=30)
        client.login(username,password)
        sending=True
        refused=client.send_message(message)
        if refused: return {'state':'unknown','external_id':message['Message-ID'],'reason':'Recipient refusal; reconcile delivery'}
        return {'state':'submitted','external_id':message['Message-ID'],'evidence':'SMTP server accepted submission; editorial status unknown'}
    except Exception:
        return {'state':'unknown' if sending else 'blocked','external_id':message['Message-ID'],'reason':'Check SMTP delivery logs before retry' if sending else 'SMTP connection or authentication failed before sending'}
    finally:
        if client is not None:
            try: client.close()
            except Exception: pass
