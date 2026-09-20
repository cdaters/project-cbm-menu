"""Actual Bash configuration controller with fake dialogs/operations. No system changes."""
import importlib.util
import io
import contextlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lib'))
import pcbm_config_bridge as bridge
import test_information_machines as fixtures


class ConfigurationUI(fixtures.Consumers):
    # Reuse sandbox setup, not inherited test cases, by overriding discovery below.
    def setUp(self):
        super().setUp()
        self.write('pcbm-config',(ROOT/'scripts/pcbm-config').read_text())
        import shutil
        shutil.copyfile(ROOT/'lib/pcbm_config_bridge.py',self.libexec/'pcbm_config_bridge.py')
        shutil.copyfile(ROOT/'lib/pcbm_status_view.py',self.libexec/'pcbm_status_view.py')
        from test_status_view import fixture
        self.appliance=self.root/'appliance.json';self.appliance.write_text(json.dumps(fixture()))
        self.env['APPLIANCE_FIXTURE']=str(self.appliance)
        self.write('pcbm-info','#!/bin/bash\nif [[ ${2:-} == --appliance ]];then cat "$APPLIANCE_FIXTURE";else cat "$INFO_FIXTURE";fi\n')
        self.write('pcbm-config-operation','''#!/bin/bash
if [[ ${1:-} == --ready ]]; then exit "${READY_STATUS:-0}"; fi
cat >> "$REQUESTS"
printf '%s' '{"format":"project-cbm.config-result","schema_version":1,"status":"'"${OP_STATUS:-ok}"'","message":"untrusted-secret"}'
''')
        self.write('pcbm-admin','#!/bin/bash\nprintf "%s\\n" "$@" >> "$ADMIN_ARGS"\nexit "${ADMIN_STATUS:-0}"\n')
        self.env.update({'REQUESTS':str(self.root/'requests'),'ADMIN_ARGS':str(self.root/'admin-args')})

    def test_config_root_hierarchy_and_navigation(self):
        p=self.run_ui('pcbm-config',['REGION','BACK','NETWORK','BACK','SERVICES','BACK','STORAGE','BACK','PICTURE','BACK','MACHINE','BACK','ADVANCED','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        args=(self.root/'dialog-args').read_text()
        for label in ['Machine and Startup','About Project CBM','Language, Keyboard and Region','Content and Storage']:self.assertIn(label,args)
        self.assertFalse((self.root/'requests').exists());self.assertNotIn('RELEASE',args)

    def test_advanced_mixer_returns_without_privileged_requests(self):
        self.write('alsamixer','#!/bin/bash\nprintf "mixer\\n" >> "$ADMIN_ARGS"\nexit "${MIXER_STATUS:-0}"\n')
        for status in ('0','1'):
            p=self.run_ui('pcbm-config',['PICTURE','MIXER','BACK','BACK'],MIXER_STATUS=status)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertFalse((self.root/'requests').exists())
            self.assertIn('Advanced Mixer',(self.root/'dialog-args').read_text())
        self.assertEqual((self.root/'admin-args').read_text().splitlines(),['mixer','mixer'])
        raw=(ROOT/'scripts/pcbm-config').read_text()
        block=raw[raw.index('      MIXER)'):raw.index('      VIDEO)')]
        self.assertNotIn('sudo',block);self.assertNotIn('alsactl',block)
        (self.bin/'alsamixer').unlink()
        p=self.run_ui('pcbm-config',['PICTURE','MIXER','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('requires alsa-utils',(self.root/'dialog-args').read_text())

    def test_country_scan_select_and_join_without_ethernet_ui(self):
        self.write('pcbm-wifi-list',"#!/bin/bash\nprintf '%s' '{\"schema_version\":1,\"status\":\"ok\",\"networks\":[{\"ssid\":\"Synthetic WiFi\",\"signal_percent\":80,\"security\":\"WPA2\"}]}'\n")
        p=self.run_ui('pcbm-config',['NETWORK','SCAN','US','0','synthetic-wifi-pass','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        requests=[json.loads(line) for line in (self.root/'requests').read_text().splitlines()]
        self.assertEqual([r['operation'] for r in requests],['wifi-country','wifi-rescan','wifi-enroll'])
        self.assertEqual(requests[-1]['values']['ssid'],'Synthetic WiFi')
        self.assertNotIn('synthetic-wifi-pass',(self.root/'dialog-args').read_text()+p.stdout+p.stderr)

    def test_files_runs_normal_mc_and_returns_to_main_menu(self):
        self.write('pcbm-files',(ROOT/'scripts/pcbm-files').read_text())
        self.write('mc','#!/bin/bash\nprintf "mc:%s\\n" "$EUID" >> "$ADMIN_ARGS"\n')
        self.env['PATH']=str(self.bin)+os.pathsep+os.environ['PATH']
        p=self.run_ui('pcbm-menu',['FILES','LIBRARY','BACK','TEST_EXIT'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'admin-args').read_text().strip(),'mc:'+str(os.geteuid()))
        self.assertFalse((self.root/'requests').exists())
        block=(ROOT/'scripts/pcbm-menu').read_text().split('        FILES)')[1].split('        POWER)')[0]
        self.assertNotIn('sudo',block)

    def test_import_reports_selected_destination_and_music_exception(self):
        self.write('pcbm-import',(ROOT/'scripts/pcbm-import').read_text())
        self.write('pcbm-import-operation','''#!/bin/bash
request=$(cat)
if [[ $request == *'"operation":"list"'* ]]; then
 printf '%s' '{"schema_version":1,"status":"ok","devices":[{"token":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","label":"Synthetic USB partition"}]}'
else
 printf '%s' '{"schema_version":1,"status":"ok","copied":2,"skipped":1,"bytes":56}'
fi
''')
        p=self.run_ui('pcbm-import',['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','c64','demos','MESSAGE'])
        self.assertEqual(p.returncode,0,p.stderr)
        text=(self.root/'dialog-args').read_text()
        self.assertIn('/home/pcbm/content/demos/c64/Imported',text)
        self.assertIn('/home/pcbm/content/music/c64/Imported',text)
        self.assertIn('USB source unmounted',text)

    def test_import_failure_stays_visible_and_never_displays_raw_error(self):
        self.write('pcbm-import',(ROOT/'scripts/pcbm-import').read_text())
        self.write('pcbm-import-operation','''#!/bin/bash
request=$(cat)
if [[ $request == *'"operation":"list"'* ]]; then
 printf '%s' '{"schema_version":1,"status":"ok","devices":[{"token":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","label":"Synthetic USB"}]}'
else
 printf '%s' '{"schema_version":1,"status":"failed","error":"access_denied","source_unmounted":true,"message":"private-secret-path"}'
 exit 2
fi
''')
        p=self.run_ui('pcbm-import',['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','c64','demos','MESSAGE'])
        self.assertEqual(p.returncode,2,p.stderr)
        text=(self.root/'dialog-args').read_text()
        self.assertIn('Import incomplete',text)
        self.assertIn('could not be accessed',text)
        self.assertIn('safe to remove',text)
        self.assertNotIn('private-secret-path',text+p.stdout+p.stderr)
        self.assertIn('--infobox',text)

    def test_system_setting_apply_cancel_and_failure(self):
        p=self.run_ui('pcbm-config',['REGION','TIMEZONE','America.Phoenix','KEYBOARD','ESC','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        request=json.loads((self.root/'requests').read_text());self.assertEqual(request['values'],{'value':'America/Phoenix'})
        self.assertIn('Setting applied',(self.root/'dialog-args').read_text())
        p=self.run_ui('pcbm-config',['NETWORK','HOSTNAME','cbm-test','MESSAGE','BACK','BACK'],OP_STATUS='failed')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertNotIn('untrusted-secret',(self.root/'dialog-args').read_text())

    def test_pending_does_not_collect_password(self):
        p=self.run_ui('pcbm-config',['NETWORK','WIFI','MESSAGE','BACK','BACK'],READY_STATUS='2')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertNotIn('--passwordbox',(self.root/'dialog-args').read_text());self.assertFalse((self.root/'requests').exists())

    def test_wifi_secret_not_in_dialog_args_or_result(self):
        p=self.run_ui('pcbm-config',['NETWORK','WIFI','MESSAGE','CBM Test','fixture-private-pass','MESSAGE','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        request=json.loads((self.root/'requests').read_text());self.assertEqual(request['operation'],'wifi-enroll')
        self.assertEqual(request['values']['password'],'fixture-private-pass')
        self.assertNotIn('fixture-private-pass',(self.root/'dialog-args').read_text()+p.stdout+p.stderr)
        self.assertNotIn('untrusted-secret',(self.root/'dialog-args').read_text())

    def test_wifi_cancel_no_operation(self):
        p=self.run_ui('pcbm-config',['NETWORK','WIFI','MESSAGE','CBM Test','ESC','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr);self.assertFalse((self.root/'requests').exists())

    def test_service_confirmation_and_allowlisted_identifier(self):
        p=self.run_ui('pcbm-config',['SERVICES','SSH','ENABLE','CANCEL','ENABLE','MESSAGE','BACK','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        request=json.loads((self.root/'requests').read_text());self.assertEqual(request['values'],{'service':'ssh','enabled':True})

    def test_service_refresh_reflects_actual_transition_without_success_ack(self):
        # Fake Product applies a transition and changes its next authoritative snapshot.
        self.write('pcbm-config-operation', '#!'+sys.executable+'\n'+"""
import json,os,sys
if len(sys.argv)>1:raise SystemExit(0)
r=json.load(sys.stdin)
with open(os.environ['REQUESTS'],'a') as f:f.write(json.dumps(r)+'\\n')
p=os.environ['APPLIANCE_FIXTURE']
d=json.load(open(p));on=r['values']['enabled']
d['services'][r['values']['service']]={'state':'on' if on else 'off','enabled':on,'listening':on}
with open(p,'w') as f:json.dump(d,f)
print(json.dumps({'format':'project-cbm.config-result','schema_version':1,'status':'ok','message':'untrusted-secret'}))
""")
        p=self.run_ui('pcbm-config',['SERVICES','SSH','ENABLE','MESSAGE','DISABLE','BACK','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        requests=[json.loads(x) for x in (self.root/'requests').read_text().splitlines()]
        self.assertEqual([r['values']['enabled'] for r in requests],[True,False])
        text=(self.root/'dialog-args').read_text()
        self.assertIn('Status: On',text);self.assertIn('Status: Off',text)
        self.assertNotIn('Setting applied.',text);self.assertNotIn('untrusted-secret',text)

    def test_samba_password_confirmation(self):
        p=self.run_ui('pcbm-config',['SERVICES','SHARING','PASSWORD','fixture-samba-pass','mismatch','MESSAGE','BACK','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr);self.assertFalse((self.root/'requests').exists())
        p=self.run_ui('pcbm-config',['SERVICES','SHARING','PASSWORD','fixture-samba-pass','fixture-samba-pass','BACK','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads((self.root/'requests').read_text())['operation'],'sharing-password')

    def test_terminal_returns_and_raspi_requires_confirmation(self):
        p=self.run_ui('pcbm-config',['ADVANCED','TERMINAL','RASPI','CANCEL','RASPI','MESSAGE','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'admin-args').read_text().splitlines(),['terminal','raspi-config'])
        self.assertFalse((self.root/'requests').exists())

    def test_about_uses_json_no_runtime_probe_and_cleans_up(self):
        p=self.run_ui('pcbm-config',['ABOUT','MESSAGE','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        text=(self.root/'view').read_text();self.assertIn('ABOUT PROJECT CBM',text)
        self.assertIn('fixture-only',self.fixture.read_text());self.assertIn('MIT',text);self.assertNotIn('v-e',text)
        self.assertFalse(list(self.root.glob('pcbm-about.*')))

    def test_offline_confirmation_is_explicit(self):
        p=self.run_ui('pcbm-config',['NETWORK','OFFLINE','MESSAGE','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads((self.root/'requests').read_text())['values'],{'enabled':False})

    def test_boot_preference_is_user_owned_and_has_active_consumer(self):
        p=self.run_ui('pcbm-config',['MACHINE','BOOT','EMULATOR','BACK','BACK'])
        self.assertEqual(p.returncode,0,p.stderr)
        from project_cbm import preferences
        self.assertEqual(preferences.read(self.home/'.config/project-cbm')['values']['boot_preference'],'emulator')
        self.assertIn('Preference saved for the next login/boot.',(self.root/'dialog-args').read_text())

    def test_ui_error_does_not_loop_or_apply(self):
        p=self.run_ui('pcbm-config',['FAIL']);self.assertEqual(p.returncode,3)
        self.assertFalse((self.root/'requests').exists())


# Do not recount inherited tests: base suite runs them in its own module.
for name in list(fixtures.Consumers.__dict__):
    if name.startswith('test_') and name not in ConfigurationUI.__dict__:
        setattr(ConfigurationUI,name,None)


class StaticBoundaries(unittest.TestCase):
    def test_wifi_list_rejects_malformed_rows_atomically(self):
        valid={'ssid':'fixture','signal_percent':70,'security':'WPA2'}
        for row in [{**valid,'signal_percent':True},{**valid,'security':'WPA2\tESC'},{**valid,'ssid':'bad\nrow'},None]:
            payload={'schema_version':1,'status':'ok','networks':[valid,row]}
            p=subprocess.run([sys.executable,str(ROOT/'lib/pcbm_config_bridge.py'),'wifi-list'],input=json.dumps(payload),text=True,capture_output=True)
            self.assertNotEqual(p.returncode,0);self.assertEqual(p.stdout,'')
    def test_old_routes_and_dead_actions_removed(self):
        for name in ['pcbm-control','pcbm-network','pcbm-bbs','pcbm-system','pcbm-bootmode']:
            raw=(ROOT/'scripts'/name).read_text();self.assertIn('exec /usr/bin/pcbm-config',raw)
            self.assertNotIn('sudo',raw)
        raw=(ROOT/'scripts/pcbm-menu').read_text();self.assertNotIn('"QUIT"',raw)
        self.assertNotIn('sudo -n',raw)
        for name in ['pcbm-config','pcbm-dialog-lib.sh','pcbm-import','pcbm-roms','pcbm-start']:
            raw=(ROOT/'scripts'/name).read_text()
            for token in ['sudo -n mount','sudo -n tee','sudo -n systemctl','pcbm-release-prep --yes']:
                self.assertNotIn(token,raw)

    def test_request_bridge_bounds_and_secret_redaction(self):
        # Encoder outputs secrets only onto its intentional request pipe, never errors.
        with tempfile.TemporaryDirectory() as tmp:
            for raw in ['x\ny\nz\n','x\n'+'a'*65537]:
                p=subprocess.run([sys.executable,str(ROOT/'lib/pcbm_config_bridge.py'),'request','hostname'],input=raw,text=True,capture_output=True)
                self.assertNotEqual(p.returncode,0);self.assertNotIn('a'*100,p.stderr)
        self.assertNotIn('subprocess',(ROOT/'lib/pcbm_config_bridge.py').read_text())

    def test_audio_data_never_executed_and_atomic_save(self):
        raw=(ROOT/'scripts/pcbm-audio').read_text()
        methods=raw[raw.index('load_audio_conf()'):raw.index('card_for_vc4_index()')]
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);conf=p/'audio.conf';conf.write_text('MODE=$(touch '+str(p/'BAD')+')\nCARD=0\nDEVICE=0\n')
            env={**os.environ,'PCBM_AUDIO_CONF':str(conf)}
            script=methods+'\nensure_audio_dirs() { :; }\nload_audio_conf\nprintf "%s" "$MODE"\nsave_audio_conf hdmi1 0 0\n'
            result=subprocess.run(['bash','-c',script],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout,'auto');self.assertFalse((p/'BAD').exists())
            self.assertEqual(conf.read_text(),'MODE=hdmi1\nCARD=0\nDEVICE=0\n');self.assertEqual(conf.stat().st_mode&0o777,0o600)
            self.assertFalse(list(p.glob('audio.conf.????????')))

    def test_about_and_service_status_use_structured_authority(self):
        from pcbm_info_view import rows
        data={'built_as':{},'running_on':{},'current_state':{'services':{
            'samba':{'LoadState':'not-found'},'ssh':{'LoadState':'masked'},
            'tcpser':{'ActiveState':'inactive','UnitFileState':'enabled'},
            'avahi':{'ActiveState':'active'}}}}
        services=dict(rows(data))['Services']
        for expected in ['File Sharing: not installed','SSH: unavailable in this profile','BBS/Modem: enabled but stopped','mDNS: running']:self.assertIn(expected,services)
        data['built_as']['build_id']='x'*150
        for width in [40,80,120]:
            text=bridge.about(data,width)
            self.assertLessEqual(max(map(len,text.splitlines())),min(width,100)-6)
            self.assertNotIn('null',text);self.assertNotIn('Traceback',text)

    def test_result_saved_intent_and_malformed_response(self):
        for status in ['ok','saved_pending','saved_restart']:
            raw=json.dumps({'format':'project-cbm.config-result','schema_version':1,'status':status,'message':'fixture-secret'})
            p=subprocess.run([sys.executable,str(ROOT/'lib/pcbm_config_bridge.py'),'result'],input=raw,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr);self.assertNotIn('fixture-secret',p.stdout)
        p=subprocess.run([sys.executable,str(ROOT/'lib/pcbm_config_bridge.py'),'result'],input='["fixture-secret"]',text=True,capture_output=True)
        self.assertNotEqual(p.returncode,0);self.assertNotIn('fixture-secret',p.stdout+p.stderr);self.assertNotIn('Traceback',p.stderr)


if __name__=='__main__':unittest.main()
