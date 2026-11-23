#!/usr/bin/env python3
"""Command-line entry point for media distribution."""
import argparse
import json
import sys
from pathlib import Path
from distribution import core
from distribution.adapters import smtp, youtube

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir',type=Path,default=Path('.distribution-state'))
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ['validate','prepare','preview','approve','execute']:
        p=commands.add_parser(name); p.add_argument('path',type=Path)
        if name=='prepare': p.add_argument('--output',type=Path,required=True)
        if name=='execute': p.add_argument('--send',action='store_true')
    for name in ['grant','revoke']:
        p=commands.add_parser(name)
        if name=='grant': p.add_argument('--artifact',type=Path,required=True)
        for field in ['content-id','channel','account']: p.add_argument('--'+field,required=True)
    p=commands.add_parser('claim'); p.add_argument('path',type=Path); p.add_argument('--key',required=True)
    commands.add_parser('status')
    for name in ['record-receipt','reconcile']:
        p=commands.add_parser(name); p.add_argument('--key',required=True); p.add_argument('--state',required=True); p.add_argument('--evidence',required=True)
    args=parser.parse_args()
    try:
        if args.command=='validate':
            core.validate(core.load(args.path),args.path.resolve().parent); result={'valid':True}
        elif args.command=='prepare': result={'artifact':str(core.prepare(args.path,args.output))}
        elif args.command=='preview': result=core.execute(args.path,args.state_dir,{})
        elif args.command=='approve': result={'approval':core.approve(args.path,args.state_dir)}
        elif args.command in {'grant','revoke'}:
            core.grant({'content_id':args.content_id,'channel':args.channel,'account':args.account},args.state_dir,args.command=='revoke',getattr(args,'artifact',None)); result={'updated':True}
        elif args.command=='execute':
            result=core.execute(args.path,args.state_dir,{'smtp':smtp.execute,'youtube':youtube.execute},not args.send)
        elif args.command=='claim':
            core.claim(args.path,args.state_dir,args.key); result={'claimed':True}
        elif args.command=='status':
            with core.state(args.state_dir) as state: result=state['results']
        else:
            core.record(args.state_dir,args.key,args.state,args.evidence); result={'recorded':True}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if isinstance(result,list) and any(r.get('state') in {'blocked','failed','unknown'} for r in result): return 2
        return 0
    except (ValueError,KeyError,TypeError,OSError):
        print('Invalid input, missing prerequisite, or approval required. Validate the package and inspect local configuration.',file=sys.stderr)
        return 2
if __name__=='__main__': sys.exit(main())
