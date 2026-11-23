import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from distribution.adapters.smtp import build_message
from distribution.adapters.youtube import metadata
class AdapterTests(unittest.TestCase):
    def test_unicode(self):
        a={'localizations':{'ja':{'title':'作品','body':'説明'}},'assets':[]}
        d={'locale':'ja','options':{'sender':'a@example.com','recipient':'b@example.com'}}
        m=build_message(a,d)
        self.assertEqual(str(m['Subject']),'作品')
        self.assertIn('説明',m.get_content())
    def test_injection(self):
        a={'localizations':{'en':{'title':'Hello','body':'text'}},'assets':[]}
        d={'locale':'en','options':{'sender':'a@example.com','recipient':'b@example.com\r\nBcc: c@example.com'}}
        with self.assertRaises(ValueError): build_message(a,d)
    def test_private(self):
        a={'localizations':{'en':{'title':'Title','body':'Body'}}}
        self.assertEqual(metadata(a,{'locale':'en','options':{}})['status']['privacyStatus'],'private')
    def test_smtp_auth_failure_is_blocked(self):
        from unittest.mock import patch, MagicMock
        import smtplib
        from distribution.adapters.smtp import execute
        a={'localizations':{'en':{'title':'Title','body':'Body'}},'assets':[]}
        d={'locale':'en','options':{'host':'smtp.example.com','sender':'a@example.com','recipient':'b@example.com','username_env':'TEST_USER','password_env':'TEST_PASS'}}
        client=MagicMock(); client.login.side_effect=smtplib.SMTPAuthenticationError(535,b'no')
        with patch.dict('os.environ',{'TEST_USER':'user','TEST_PASS':'password'}), patch('smtplib.SMTP_SSL',return_value=client):
            self.assertEqual(execute(a,d)['state'],'blocked')
