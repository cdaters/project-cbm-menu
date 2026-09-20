"""Real first-run Bash with fake dialog and validated, redacting backend fixtures."""
import json
import shutil
import subprocess
import sys
from pathlib import Path
import unittest
import test_information_machines as fixtures
ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT.parent/'project-cbm'


class FirstRunUI(fixtures.Consumers):
    def setUp(self):
        super().setUp()
        shutil.copyfile(ROOT/'lib/pcbm_config_bridge.py',self.libexec/'pcbm_config_bridge.py')
        self.write('pcbm-first-run',(ROOT/'scripts/pcbm-first-run').read_text())
        self.state=self.root/'setup.json';self.state.write_text('{"completed":[],"complete":false}')
        self.env['SETUP_STATE']=str(self.state);self.env['OPERATIONS']=str(self.root/'operations')
        self.write('pcbm-setup-state',f'''#!{sys.executable}
import json,os,sys
s=json.load(open(os.environ['SETUP_STATE']))
raise SystemExit(0 if (s['complete'] if sys.argv[1]=='complete' else sys.argv[1] in s['completed']) else 1)
''')
        self.write('pcbm-config-operation',f'''#!{sys.executable}
import json,os,sys
sys.path.insert(0,{str(PRODUCT/'runtime')!r})
from project_cbm.configuration import decode,result
r=decode(sys.stdin.buffer.read(4097));op=r['operation']
s=json.load(open(os.environ['SETUP_STATE']))
with open(os.environ['OPERATIONS'],'a') as f:f.write(op+'\\n')
from pathlib import Path
rejected=Path(os.environ['OPERATIONS']+'.rejected')
if os.environ.get('REJECT_ONCE')==op and not rejected.exists():
 rejected.touch();print(json.dumps(result('wifi_failed' if 'wifi' in op else 'invalid')));raise SystemExit(2)
assert '...' in Path(os.environ['DIALOG_ARGS']).read_text(), 'working state must precede backend'
if op=='setup-finish':s['complete']=True
elif not op.startswith('setup-wifi-') and op.removeprefix('setup-') not in s['completed']:s['completed'].append(op.removeprefix('setup-'))
with open(os.environ['SETUP_STATE'],'w') as f:json.dump(s,f)
print(json.dumps({{**result('ok'),'message':'untrusted-fixture-message'}}))
''')
    def test_offline_flow_no_secret_in_dialog_arguments_or_output(self):
        secret='synthetic-owner-only'
        self.assertIn('Username: pcbm.', (ROOT/'scripts/pcbm-first-run').read_text())
        p=self.run_ui('pcbm-first-run',['MESSAGE','en_US.UTF-8','us','UTC',secret,secret,'OFFLINE'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue(json.loads(self.state.read_text())['complete'])
        self.assertEqual((self.root/'operations').read_text().splitlines(),['setup-region','setup-owner','setup-network','setup-finish'])
        for text in [(self.root/'dialog-args').read_text(),(self.root/'operations').read_text(),self.state.read_text(),p.stdout,p.stderr]:
            self.assertNotIn(secret,text);self.assertNotIn('untrusted-fixture-message',text)

    def test_password_prompt_ranges_are_plain_ascii_without_formatting(self):
        secret='synthetic-password'
        p=self.run_ui('pcbm-first-run',['MESSAGE','en_US.UTF-8','us','UTC',secret,secret,'OFFLINE'])
        self.assertEqual(p.returncode,0,p.stderr)
        args=(self.root/'dialog-args').read_text()
        self.assertIn('12-128 printable characters',args)
        self.assertTrue(args.isascii())
        self.assertNotIn('\\Z',args);self.assertNotIn('\x1b',args)
        self.wifi_fixture()
        p=self.run_ui('pcbm-first-run',['MESSAGE','WIFI','US','0','synthetic wifi !'])
        self.assertEqual(p.returncode,0,p.stderr)
        args=(self.root/'dialog-args').read_text()
        self.assertIn('8-63 printable ASCII characters',args)
        self.assertTrue(args.isascii())
        self.assertNotIn('\\Z',args);self.assertNotIn('\x1b',args)

    def test_wifi_choice_stays_in_setup_until_connection_succeeds(self):
        self.state.write_text('{"completed":["region","owner"],"complete":false}')
        self.write('pcbm-wifi-list','#!/bin/bash\nprintf \'%s\\n\' \'{"schema_version":1,"status":"ok","networks":[{"ssid":"fixture","signal_percent":80,"security":"WPA2"}]}\'\n')
        p=self.run_ui('pcbm-first-run',['MESSAGE','WIFI','US','0','synthetic wifi !'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'operations').read_text().splitlines(),['setup-network','setup-wifi-country','setup-wifi-rescan','setup-wifi-enroll','setup-finish'])
        self.assertTrue(json.loads(self.state.read_text())['complete'])

    def test_cancel_does_not_initialize(self):
        p=self.run_ui('pcbm-first-run',['ESC'])
        self.assertEqual(p.returncode,1);self.assertFalse((self.root/'operations').exists())
    def test_password_mismatch_preserves_region_and_retry_skips_it(self):
        p=self.run_ui('pcbm-first-run',['MESSAGE','en_US.UTF-8','us','UTC','synthetic-password','different-password','MESSAGE','ESC'])
        self.assertEqual(p.returncode,1)
        self.assertEqual(json.loads(self.state.read_text())['completed'],['region'])
        p=self.run_ui('pcbm-first-run',['MESSAGE','synthetic-password','synthetic-password','OFFLINE'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'operations').read_text().count('setup-region'),1)
    def test_completed_setup_never_collects_password_again(self):
        self.state.write_text('{"completed":["region","owner","network"],"complete":true}')
        p=self.run_ui('pcbm-first-run',[])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('Saving configuration',(self.root/'dialog-args').read_text())
        self.assertEqual((self.root/'operations').read_text(),'setup-finish\n')
    def test_preference_failure_blocks_finish(self):
        self.state.write_text('{"completed":["region","owner","network"],"complete":false}')
        self.write('pcbm-profiles','#!/bin/bash\nexit 2\n')
        p=self.run_ui('pcbm-first-run',['MESSAGE','OFFLINE'])
        self.assertEqual(p.returncode,2);self.assertNotIn('setup-finish',(self.root/'operations').read_text())
    def test_sid_is_not_autostarted(self):
        media=self.home/'content'/'test.SID';media.write_bytes(b'synthetic-only')
        p=subprocess.run(['bash',str(self.bin/'pcbm-run-vice'),'x64sc',str(media)],env=self.env,capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertIn('PSID/RSID',p.stderr);self.assertFalse((self.root/'launch').exists())

    def wifi_fixture(self):
        self.state.write_text('{"completed":["region","owner"],"complete":false}')
        self.write('pcbm-wifi-list','#!/bin/bash\nprintf \'%s\\n\' \'{"schema_version":1,"status":"ok","networks":[{"ssid":"first","signal_percent":80,"security":"WPA2"},{"ssid":"second","signal_percent":70,"security":"WPA2"}]}\'\n')

    def test_back_revisits_then_changes_region_before_apply(self):
        p=self.run_ui('pcbm-first-run',['MESSAGE','ADVANCED','CANCEL','en_US.UTF-8','CANCEL','en_GB.UTF-8','gb','CANCEL','us','UTC','synthetic-password','synthetic-password','OFFLINE'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'operations').read_text().count('setup-region'),1)
        text=(self.root/'dialog-args').read_text()
        self.assertIn('United Kingdom',text);self.assertIn('masked with asterisks',text)
        self.assertIn('--no-tags',text)

    def test_invalid_region_retries_without_owner_commit(self):
        p=self.run_ui('pcbm-first-run',['MESSAGE','en_US.UTF-8','us','UTC','MESSAGE','en_GB.UTF-8','gb','UTC','synthetic-password','synthetic-password','OFFLINE'],REJECT_ONCE='setup-region')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'operations').read_text().splitlines()[:3],['setup-region','setup-region','setup-owner'])

    def test_wifi_failed_password_retry_and_alternate_network(self):
        for route,choices in [('RETRY',['RETRY','synthetic retry !']),('SCAN',['SCAN','1','synthetic second !'])]:
            with self.subTest(route=route):
                self.wifi_fixture()
                for path in ['operations','operations.rejected']:(self.root/path).unlink(missing_ok=True)
                p=self.run_ui('pcbm-first-run',['MESSAGE','WIFI','GB','0','synthetic first !','MESSAGE',*choices],REJECT_ONCE='setup-wifi-enroll')
                self.assertEqual(p.returncode,0,p.stderr)
                ops=(self.root/'operations').read_text().splitlines()
                self.assertEqual(ops.count('setup-wifi-enroll'),2);self.assertEqual(ops[-1],'setup-finish')
                self.assertNotIn('synthetic first !',(self.root/'dialog-args').read_text()+p.stdout+p.stderr)

    def test_wifi_offline_fallback_and_interrupted_resume(self):
        self.wifi_fixture()
        p=self.run_ui('pcbm-first-run',['MESSAGE','WIFI','US','0','synthetic fail !','MESSAGE','OFFLINE'],REJECT_ONCE='setup-wifi-enroll')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'operations').read_text().splitlines()[-2:],['setup-network','setup-finish'])
        self.wifi_fixture()
        p=self.run_ui('pcbm-first-run',['MESSAGE','WIFI','ESC'])
        self.assertEqual(p.returncode,1);self.assertFalse(json.loads(self.state.read_text())['complete'])
        p=self.run_ui('pcbm-first-run',['MESSAGE','OFFLINE'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue(json.loads(self.state.read_text())['complete'])


for name in list(fixtures.Consumers.__dict__):
    if name.startswith('test_') and name not in FirstRunUI.__dict__:setattr(FirstRunUI,name,None)
