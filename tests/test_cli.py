import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CLITests(unittest.TestCase):
    def test_outside_repository(self):
        result=subprocess.run([sys.executable,str(ROOT/'scripts/media_distribution.py'),'validate',str(ROOT/'examples/image-package.json')],cwd='/tmp',capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['valid'])
    def test_no_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            command=[sys.executable,str(ROOT/'scripts/media_distribution.py')]
            p=subprocess.run(command+['prepare',str(ROOT/'examples/image-package.json'),'--output',directory],capture_output=True,text=True)
            artifact=json.loads(p.stdout)['artifact']
            result=subprocess.run(command+['--state-dir',directory+'/state','execute',artifact,'--send'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
