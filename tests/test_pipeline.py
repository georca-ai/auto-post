import sys, unittest, tempfile, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from distribution.core import prepare, approve, execute, load

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'image.jpg').write_bytes(b'example')
        self.package = {'content_id':'sample','source_locale':'en','localizations':{'en':{'title':'Hello','body':'Design'}},'assets':[{'path':'image.jpg','type':'image'}],'destinations':[{'channel':'instagram','account':'studio','locale':'en','transport':'browser','options':{}}]}
        self.source = self.root/'package.json'
    def prepared(self):
        self.source.write_text(json.dumps(self.package))
        return prepare(self.source,self.root/'prepared')
    def test_missing_locale(self):
        self.package['destinations'][0]['locale']='ja'
        with self.assertRaises(ValueError): self.prepared()
    def test_unsupported_media(self):
        self.package['destinations'][0]['channel']='youtube'
        with self.assertRaises(ValueError): self.prepared()
    def test_dry_run_and_approval(self):
        artifact=self.prepared(); calls=[]
        adapter=lambda a,d: calls.append(d) or {'state':'published','external_id':'1'}
        self.assertEqual(execute(artifact,self.root/'state',{'browser':adapter})[0]['state'],'prepared')
        self.assertFalse(calls)
        with self.assertRaises(ValueError): execute(artifact,self.root/'state',{'browser':adapter},False)
        approve(artifact,self.root/'state')
        execute(artifact,self.root/'state',{'browser':adapter},False)
        execute(artifact,self.root/'state',{'browser':adapter},False)
        self.assertEqual(len(calls),1)
    def test_changed_asset_invalidates(self):
        artifact=self.prepared(); approve(artifact,self.root/'state')
        data=load(artifact); Path(data['assets'][0]['path']).write_bytes(b'changed')
        with self.assertRaises(ValueError): execute(artifact,self.root/'state',{},False)
    def test_unknown_not_retried(self):
        artifact=self.prepared(); approve(artifact,self.root/'state'); calls=[]
        def adapter(a,d):
            calls.append(d)
            raise TimeoutError('secret must not escape')
        result=execute(artifact,self.root/'state',{'browser':adapter},False)
        self.assertEqual(result[0]['state'],'unknown')
        execute(artifact,self.root/'state',{'browser':adapter},False)
        self.assertEqual(len(calls),1)
        self.assertNotIn('secret',json.dumps(result))
    def test_reprepare_does_not_duplicate(self):
        calls=[]
        for _ in range(2):
            a=self.prepared(); approve(a,self.root/'state')
            execute(a,self.root/'state',{'browser':lambda a,d: calls.append(1) or {'state':'published'}},False)
        self.assertEqual(len(calls),1)
    def test_completed_receipt_cannot_reopen(self):
        from distribution.core import record
        a=self.prepared(); approve(a,self.root/'state')
        result=execute(a,self.root/'state',{'browser':lambda a,d:{'state':'published'}},False)
        with self.assertRaises(ValueError): record(self.root/'state',result[0]['key'],'failed','operator claim')
    def test_browser_claim_once(self):
        from distribution.core import claim
        a=self.prepared(); approve(a,self.root/'state')
        key=execute(a,self.root/'state',{},False)[0]['key']
        claim(a,self.root/'state',key)
        with self.assertRaises(ValueError): claim(a,self.root/'state',key)
    def test_grant_binds_recipient_configuration(self):
        from distribution.core import grant
        a=self.prepared()
        grant({'content_id':'sample','channel':'instagram','account':'studio'},self.root/'state',artifact=a)
        modified=load(a); modified['destinations'][0]['options']['url']='https://other.example'
        a.write_text(json.dumps(modified))
        with self.assertRaises(ValueError): execute(a,self.root/'state',{},False)
    def test_two_concurrent_sends(self):
        from concurrent.futures import ThreadPoolExecutor
        import time
        a=self.prepared(); approve(a,self.root/'state'); calls=[]
        def adapter(a,d):
            calls.append(1); time.sleep(0.02); return {'state':'published'}
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(execute,a,self.root/'state',{'browser':adapter},False) for _ in range(2)]
            for f in futures: f.result()
        self.assertEqual(len(calls),1)
    def test_unknown_browser_receipt(self):
        from distribution.core import record,claim
        a=self.prepared(); approve(a,self.root/'state')
        key=execute(a,self.root/'state',{},False)[0]['key']; claim(a,self.root/'state',key)
        record(self.root/'state',key,'unknown','Timed out after click')
        with self.assertRaises(ValueError): claim(a,self.root/'state',key)
