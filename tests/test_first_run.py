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
if op=='setup-finish':s['complete']=True
else:s['completed'].append(op.removeprefix('setup-'))
with open(os.environ['SETUP_STATE'],'w') as f:json.dump(s,f)
print(json.dumps({{**result('ok'),'message':'untrusted-fixture-message'}}))
''')
    def test_offline_flow_no_secret_in_dialog_arguments_or_output(self):
        secret='synthetic-owner-only'
        p=self.run_ui('pcbm-first-run',['MESSAGE','en_US.UTF-8','us','UTC',secret,secret,'OFFLINE'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue(json.loads(self.state.read_text())['complete'])
        self.assertEqual((self.root/'operations').read_text().splitlines(),['setup-region','setup-owner','setup-network','setup-finish'])
        for text in [(self.root/'dialog-args').read_text(),(self.root/'operations').read_text(),self.state.read_text(),p.stdout,p.stderr]:
            self.assertNotIn(secret,text);self.assertNotIn('untrusted-fixture-message',text)
    def test_wifi_choice_finishes_setup_then_opens_network_without_ethernet(self):
        self.state.write_text('{"completed":["region","owner"],"complete":false}')
        self.write('pcbm-config','#!/bin/bash\nprintf "%s\\n" "$@" >> "$OPERATIONS"\n')
        p=self.run_ui('pcbm-first-run',['MESSAGE','WIFI'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'operations').read_text().splitlines(),['setup-network','setup-finish','network'])
        self.assertTrue(json.loads(self.state.read_text())['complete'])

    def test_cancel_does_not_initialize(self):
        p=self.run_ui('pcbm-first-run',['ESC'])
        self.assertEqual(p.returncode,1);self.assertFalse((self.root/'operations').exists())
    def test_password_mismatch_preserves_region_and_retry_skips_it(self):
        p=self.run_ui('pcbm-first-run',['MESSAGE','en_US.UTF-8','us','UTC','synthetic-password','different-password','MESSAGE'])
        self.assertEqual(p.returncode,1)
        self.assertEqual(json.loads(self.state.read_text())['completed'],['region'])
        p=self.run_ui('pcbm-first-run',['MESSAGE','synthetic-password','synthetic-password','OFFLINE'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'operations').read_text().count('setup-region'),1)
    def test_completed_setup_never_collects_password_again(self):
        self.state.write_text('{"completed":["region","owner","network"],"complete":true}')
        p=self.run_ui('pcbm-first-run',[])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertFalse((self.root/'dialog-args').exists())
        self.assertEqual((self.root/'operations').read_text(),'setup-finish\n')
    def test_preference_failure_blocks_finish(self):
        self.state.write_text('{"completed":["region","owner","network"],"complete":false}')
        self.write('pcbm-profiles','#!/bin/bash\nexit 2\n')
        p=self.run_ui('pcbm-first-run',['MESSAGE'])
        self.assertEqual(p.returncode,2);self.assertFalse((self.root/'operations').exists())
    def test_sid_is_not_autostarted(self):
        media=self.home/'pcbm'/'test.SID';media.write_bytes(b'synthetic-only')
        p=subprocess.run(['bash',str(self.bin/'pcbm-run-vice'),'x64sc',str(media)],env=self.env,capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertIn('PSID/RSID',p.stderr);self.assertFalse((self.root/'launch').exists())


for name in list(fixtures.Consumers.__dict__):
    if name.startswith('test_') and name not in FirstRunUI.__dict__:setattr(FirstRunUI,name,None)
