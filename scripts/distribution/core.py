"""Content preparation and serialized execution with explicit consent."""
import copy
import re
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

CAPABILITIES = {'instagram': {'image','video'}, 'xiaohongshu': {'image','video'}, 'bilibili': {'video'}, 'youtube': {'video'}, 'publication': {'image','video','document'}}
def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def file_hash(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''): h.update(chunk)
    return h.hexdigest()
def save(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(value,f,ensure_ascii=False,indent=2); f.flush(); os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)
def validate(package,base):
    if not package.get('content_id') or not package.get('source_locale'): raise ValueError('Content ID and source locale required')
    if package.get('schedule'): raise ValueError('Scheduling is unsupported')
    assets=package.get('assets',[])
    if not assets or not package.get('destinations'): raise ValueError('Assets and destinations required')
    for a in assets:
        if not (base/a['path']).is_file(): raise ValueError('Missing asset')
        if a['type']=='video':
            with open(base/a['path'],'rb') as media: header=media.read(16)
            if not (header[4:8]==b'ftyp' or header[:4]==bytes.fromhex('1a45dfa3') or header[:4]==b'RIFF'): raise ValueError('Unsupported video container')
    seen=set()
    for d in package['destinations']:
        key=(d['channel'],d['account'],d['locale'])
        if key in seen: raise ValueError('Duplicate destination')
        seen.add(key)
        copy=package.get('localizations',{}).get(d['locale'])
        if not re.fullmatch(r'[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*',d['locale']): raise ValueError('Invalid locale tag')
        if not copy or not copy.get('title','').strip() or not copy.get('body','').strip(): raise ValueError('Complete localized title and body required')
        if not d['account']: raise ValueError('Account required')
        if d['channel'] not in CAPABILITIES: raise ValueError('Unknown channel')
        if any(a['type'] not in CAPABILITIES[d['channel']] for a in assets): raise ValueError('Unsupported media')
        allowed={'youtube':{'youtube'},'publication':{'smtp','browser'}}.get(d['channel'],{'browser'})
        if d['transport'] not in allowed: raise ValueError('Unsupported transport')
        if d['channel'] in {'youtube','bilibili'} and len(assets)!=1: raise ValueError('One video per destination required')
        if any(a.get('subtitles') for a in assets): raise ValueError('Subtitle upload is not supported; burn captions into supplied video or submit separately')
    return package

def prepare(source,output):
    source=Path(source).resolve(); package=validate(load(source),source.parent)
    output=Path(output).resolve(); output.mkdir(parents=True,exist_ok=True)
    folder=Path(tempfile.mkdtemp(prefix='package-',dir=output))
    for i,a in enumerate(package['assets']):
        original=source.parent/a['path']; target=folder/(str(i)+original.suffix)
        shutil.copyfile(original,target); a['path']=str(target); a['sha256']=file_hash(target)
    artifact=folder/'artifact.json'; save(artifact,package); return artifact

def verified(path):
    a=load(path); validate(a,Path(path).parent)
    if any(file_hash(x['path'])!=x['sha256'] for x in a['assets']): raise ValueError('Prepared asset changed; prepare and approve again')
    return a

@contextlib.contextmanager
def state(directory):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    with open(directory/'lock','a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        p=directory/'state.json'; data=load(p) if p.exists() else {'approvals':[], 'grants':[], 'results':{}}
        yield data
        save(p,data)

def approve(path,directory):
    token=digest(verified(path))
    with state(directory) as s:
        if token not in s['approvals']: s['approvals'].append(token)
    return token

def grant(scope,directory,revoke=False,artifact=None):
    if set(scope)!={'content_id','channel','account'} or not all(scope.values()): raise ValueError('Exact task, channel and account required')
    with state(directory) as s:
        if revoke: s['grants']=[g for g in s['grants'] if not all(g.get(k)==v for k,v in scope.items())]
        else:
            if artifact is None: raise ValueError('Artifact required to bind grant configuration')
            a=verified(artifact)
            matches=[d for d in a['destinations'] if d['account']==scope['account'] and d['channel']==scope['channel'] and a['content_id']==scope['content_id']]
            if not matches: raise ValueError('Grant scope not in artifact')
            s['grants'].append(dict(scope,bindings=[digest(d) for d in matches]))

def execute(path,directory,adapters,dry_run=True):
    a=verified(path); token=digest(a)
    if dry_run: return [{'state':'prepared','destination':d,'copy':a['localizations'][d['locale']],'assets':a['assets']} for d in a['destinations']]
    results=[]
    with state(directory) as s:
        for d in a['destinations']:
            scope={'content_id':a['content_id'],'channel':d['channel'],'account':d['account']}
            if token not in s['approvals'] and not any(all(g.get(k)==v for k,v in scope.items()) and digest(d) in g.get('bindings',[]) for g in s['grants']): raise ValueError('Explicit approval or scoped grant required')
        for d in a['destinations']:
            key=delivery_key(a,d)
            old=s['results'].get(key)
            if old and old['state'] not in {'blocked','failed'}:
                if old['state']=='executing': old['state']='unknown'
                results.append(dict(old,key=key)); continue
            adapter=adapters.get(d['transport'])
            if adapter is None: result={'state':'blocked','reason':'Required adapter unavailable'}
            else:
                s['results'][key]={'state':'executing','channel':d['channel']}; save(Path(directory)/'state.json',s)
                try:
                    with tempfile.TemporaryDirectory(prefix='distribution-send-') as temp:
                        snapshot=copy.deepcopy(a)
                        for index,asset in enumerate(snapshot['assets']):
                            target=Path(temp)/(str(index)+Path(asset['path']).suffix)
                            shutil.copyfile(asset['path'],target)
                            if file_hash(target)!=asset['sha256']: raise ValueError('Asset changed')
                            asset['path']=str(target)
                        result=adapter(snapshot,d)
                except Exception: result={'state':'unknown','reason':'Execution outcome uncertain; reconcile before retry'}
                if result.get('state') not in {'published','submitted','blocked','failed','unknown'}: result={'state':'unknown','reason':'Invalid adapter receipt'}
            result['channel']=d['channel']
            s['results'][key]=result; results.append(dict(result,key=key))
    return results

def delivery_key(a,d):
    assets=[{k:v for k,v in asset.items() if k!='path'} for asset in a['assets']]
    return digest([a['content_id'],d,a['localizations'][d['locale']],assets])

def claim(path,directory,key):
    a=verified(path)
    with state(directory) as s:
        destinations=[d for d in a['destinations'] if delivery_key(a,d)==key and d['transport']=='browser']
        if not destinations: raise ValueError('Browser destination not found')
        d=destinations[0]
        scope={'content_id':a['content_id'],'channel':d['channel'],'account':d['account']}
        authorized=digest(a) in s['approvals'] or any(all(g.get(k)==v for k,v in scope.items()) and digest(d) in g.get('bindings',[]) for g in s['grants'])
        if not authorized: raise ValueError('Approval required')
        old=s['results'].get(key,{})
        if old.get('state') not in {'blocked','failed'}: raise ValueError('Destination already claimed or completed')
        s['results'][key]={'state':'unknown','channel':d['channel'],'evidence':'Browser operation claimed; reconcile if interrupted'}

def record(directory,key,new_state,evidence):
    if not evidence or new_state not in {'published','submitted','accepted','rejected','failed','unknown'}: raise ValueError('State and evidence required')
    with state(directory) as s:
        old=s['results'].get(key)
        if not old: raise ValueError('Unknown execution key')
        if old['state'] in {'published','accepted','rejected'}: raise ValueError('Completed delivery cannot reopen')
        if old['state']=='submitted' and new_state not in {'accepted','rejected'}: raise ValueError('Submission cannot reopen')
        if new_state in {'accepted','rejected'} and old['state']!='submitted': raise ValueError('Editorial decision requires submission')
        if old.get('channel')=='publication' and new_state=='published': raise ValueError('Publication receipt is submitted')
        if old.get('channel')!='publication' and new_state in {'submitted','accepted','rejected'}: raise ValueError('Not an editorial destination')
        s['results'][key]={'state':new_state,'channel':old.get('channel'),'evidence':evidence,'previous':old}
