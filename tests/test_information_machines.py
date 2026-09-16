"""Presentation/consumer fixtures. Never launches VICE, touches a Pi, or invokes sudo."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT.parent / 'project-cbm'
spec=importlib.util.spec_from_file_location('view',ROOT/'lib/pcbm_info_view.py')
view=importlib.util.module_from_spec(spec);spec.loader.exec_module(view)
sys.path.insert(0,str(PRODUCT/'runtime'))
sys.path.insert(0,str(PRODUCT/'tests'))
from project_cbm import info, preferences
from test_runtime_foundation import Fixture


class InformationView(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.prefs=Path(self.tmp.name)/'preferences'
        self.data=info.collect(Fixture(),self.prefs)

    def test_complete_report_and_live_package_distinction(self):
        result=view.render(view.parse(json.dumps(self.data)))
        for value in ['PROJECT CBM','HARDWARE','SYSTEM','CONFIGURATION','Raspberry Pi 3','Debian GNU/Linux','3.10-1+pcbm3','Commodore 64']:
            self.assertIn(value,result)
        self.assertIn('SYNTHETIC',result)
        self.assertNotIn('null',result)

    def test_partial_unknown_future_headless_disabled(self):
        f=Fixture('Future Pi 999');f.files['/sys/class/drm/card1-HDMI-A-1/status']='disconnected'
        for k in ['/proc/meminfo','/usr/share/project-cbm/identity.json']:f.files.pop(k)
        d=info.collect(f,self.prefs);text=view.render(d)
        self.assertIn('Future Pi 999',text);self.assertIn('None connected',text)
        self.assertIn('Network management disabled',text);self.assertIn('Unavailable',text)
        self.assertNotIn('null',text);self.assertNotIn('Traceback',text)

    def test_collector_failures_preserve_useful_fields(self):
        d=copy.deepcopy(self.data);d['built_as']=None;d['current_state']['packages']=None
        d['running_on']['displays']=None;d['running_on']['memory']=None
        d['issues']=[{'collector':'packages','code':'unavailable_or_invalid'}]
        text=view.render(d);self.assertIn('Raspberry Pi 3',text);self.assertIn('Some information',text)

    def test_missing_optional_package(self):
        self.data['current_state']['packages']['tcpser']={'installed':False,'version':None}
        self.assertIn('Not installed',view.render(self.data))

    def test_terminal_sizes_and_full_long_values(self):
        self.data['built_as']['build_id']='a'*64
        self.data['running_on']['model']='Future Pi '+ '界'*40
        for width in [20,40,60,80,120,200]:
            text=view.render(self.data,width)
            self.assertTrue(all(view.cell_width(line)<=max(14,min(width,100)-6) for line in text.splitlines()))
            self.assertIn('a'*64,text.replace('\n',''))

    def test_contract_failure_duplicate_keys_and_controls(self):
        for raw in ['{}','{"format":"project-cbm.info","schema_version":2}', '{"format":"project-cbm.info","schema_version":1,"schema_version":1}', '['*2000, 'x'*65537]:
            with self.assertRaises((ValueError,RecursionError)):view.parse(raw)
        d=copy.deepcopy(self.data);d['builder_secret']='do-not-export';d['current_state']['password']='do-not-export'
        d['running_on']['model']='\x1b[31m';d['built_as']['build_id']='/private/build/location'
        text=view.render(d);self.assertNotIn('do-not-export',text);self.assertNotIn('\x1b',text);self.assertNotIn('/private',text)


class Consumers(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.bin=self.root/'usr/bin';self.bin.mkdir(parents=True)
        self.home=self.root/'home/pi';(self.home/'pcbm').mkdir(parents=True)
        self.share=self.root/'usr/share/project-cbm-menu';self.share.mkdir(parents=True)
        shutil.copyfile(ROOT/'lib/pcbm-ui.sh',self.share/'pcbm-ui.sh')
        self.libexec=self.root/'usr/libexec/project-cbm-menu';self.libexec.mkdir(parents=True)
        shutil.copyfile(ROOT/'lib/pcbm_info_view.py',self.libexec/'pcbm_info_view.py')
        for name in ['pcbm-profiles','pcbm-preferences']:
            self.write(name,'#!/bin/bash\nexec '+sys.executable+' '+str(PRODUCT/'runtime/bin'/name)+' "$@"\n')
        (self.bin/'python3').symlink_to(sys.executable)
        # An inert stand-in for the non-migrated library; migrated real helper functions
        # are copied below so the test covers the actual registry reader and launcher.
        lib=(ROOT/'scripts/pcbm-dialog-lib.sh').read_text()
        a=lib.index('pcbm_load_default_machine()');b=lib.index('pcbm_filtered_find()',a)
        self.write('pcbm-dialog-lib.sh',lib[a:b]+'\npcbm_trap_cleanup() { :; }\npcbm_launch_machine() { /usr/bin/pcbm-run-vice "$1"; }\n')
        helpers=self.bin/'pcbm-dialog-lib.sh'
        extra=lib[lib.index('pcbm_launch_machine()'):lib.index('pcbm_launch_content()')]
        extra=extra.replace('/usr/bin/',str(self.bin)+'/')
        with helpers.open('a') as stream:
            stream.write(extra)
            stream.write('\npcbm_cleanup_terminal() { :; }\npcbm_show_msg() { printf "%s\\n" "$@" >> "$DIALOG_ARGS"; }\npcbm_show_menu() { PCBM_CHOICE=$("$PCBM_DIALOG_BIN" "$@"); PCBM_STATUS=$?; [[ $PCBM_CHOICE != TEST_EXIT ]] || exit 0; }\n')
        self.write('pcbm-cover','#!/bin/bash\nexit 0\n')
        for name in ['pcbm-machines','pcbm-system-info','pcbm-run-vice','pcbm-boot','pcbm-menu']:
            self.write(name,(ROOT/'scripts'/name).read_text())
        for name in ['x64sc','xvic','x128']:
            self.write(name,'#!/bin/bash\nprintf "%s\\n" "'+name+'" "$@" >> "$LAUNCH"\nexit "${VICE_STATUS:-0}"\n')
        self.fixture=self.root/'info.json';self.fixture.write_text(json.dumps(info.collect(Fixture(),self.root/'none')))
        self.write('pcbm-info','#!/bin/bash\n[[ $1 == --json ]] || exit 2\ncat "$INFO_FIXTURE"\nexit "${INFO_STATUS:-0}"\n')
        self.write('dialog','''#!/bin/bash
printf '%s\\n' "$@" >> "$DIALOG_ARGS"
if [[ " $* " == *" --textbox "* ]]; then
  previous=; for arg in "$@"; do [[ $previous != --textbox ]] || cat "$arg" >> "$VIEW"; previous=$arg; done
fi
choice=$(head -n 1 "$QUEUE"); tail -n +2 "$QUEUE" > "$QUEUE.next"; mv "$QUEUE.next" "$QUEUE"
case "$choice" in
  CANCEL) exit 1 ;; ESC) exit 255 ;; FAIL) exit 2 ;; MESSAGE) exit 0 ;; *) printf '%s' "$choice" ;;
esac
''')
        self.env={**os.environ,'XDG_CONFIG_HOME':str(self.home/'.config'),'PCBM_DIALOG_BIN':str(self.bin/'dialog'),
                  'QUEUE':str(self.root/'queue'),'DIALOG_ARGS':str(self.root/'dialog-args'),'VIEW':str(self.root/'view'),
                  'LAUNCH':str(self.root/'launch'),'INFO_FIXTURE':str(self.fixture),'COLUMNS':'80','LINES':'24','TMPDIR':str(self.root)}

    def write(self,name,raw):
        # Redirect absolute deployment paths only in disposable test copies.
        for prefix in ['/usr/bin/','/usr/share/project-cbm-menu/','/usr/libexec/','/etc/pcbm/','/home/pi']:
            raw=raw.replace(prefix,str(self.root)+prefix)
        p=self.bin/name;p.write_text(raw);p.chmod(0o755)

    def run_ui(self,name,choices,**env):
        (self.root/'queue').write_text('\n'.join(choices)+'\n')
        return subprocess.run(['bash',str(self.bin/name)],env={**self.env,**env},capture_output=True,text=True,timeout=8)

    def test_machine_listing_default_save_and_run(self):
        p=self.run_ui('pcbm-machines',['DEFAULT','xvic']);self.assertEqual(p.returncode,0,p.stderr)
        saved=json.loads((self.home/'.config/project-cbm/preferences.json').read_text());self.assertEqual(saved['default_machine'],'xvic')
        args=(self.root/'dialog-args').read_text();self.assertIn('current default',args);self.assertIn('x128-80col',args)
        p=subprocess.run(['bash',str(self.bin/'pcbm-boot')],env=self.env,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual((self.root/'launch').read_text().splitlines()[:5],['xvic','-sounddev','sdl','-menukey','291'])

    def test_actual_main_run_and_return_uses_saved_preference(self):
        preferences.update({'default_machine':'xvic'},self.home/'.config/project-cbm')
        p=self.run_ui('pcbm-menu',['RUN','TEST_EXIT'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual((self.root/'launch').read_text().splitlines()[0],'xvic')
        self.assertGreaterEqual((self.root/'dialog-args').read_text().count('Commodore VIC-20'),2)

    def test_main_failed_launch_reports_then_returns(self):
        p=self.run_ui('pcbm-menu',['RUN','TEST_EXIT'],VICE_STATUS='9')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('VICE Launch Failed',(self.root/'dialog-args').read_text())

    def test_save_failure_does_not_claim_success(self):
        self.write('pcbm-preferences','#!/bin/bash\nexit 2\n')
        p=self.run_ui('pcbm-machines',['DEFAULT','xvic','MESSAGE','RETURN','RETURN'])
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('Default not saved',(self.root/'dialog-args').read_text())
        self.assertEqual(preferences.read(self.home/'.config/project-cbm')['values']['default_machine'],'x64sc')

    def test_launcher_refuses_injection_before_emulator(self):
        for profile in ['xevil','/bin/sh','x64sc;touch BAD','$(touch BAD)']:
            p=subprocess.run(['bash',str(self.bin/'pcbm-run-vice'),profile],env=self.env,capture_output=True)
            self.assertEqual(p.returncode,2);self.assertFalse((self.root/'launch').exists())

    def test_cancel_back_invalid_selection_never_launches(self):
        for choices in [['ESC'],['CANCEL'],['DEFAULT','ESC','RETURN'],['not-a-profile']]:
            p=self.run_ui('pcbm-machines',choices)
            self.assertIn(p.returncode,[0,3],p.stderr);self.assertFalse((self.root/'launch').exists())
        state=preferences.read(self.home/'.config/project-cbm');self.assertEqual(state['values']['default_machine'],'x64sc')

    def test_failed_launch_returns_and_does_not_change_default(self):
        p=self.run_ui('pcbm-machines',['x128-80col','MESSAGE','RETURN'],VICE_STATUS='9')
        self.assertEqual(p.returncode,0,p.stderr)
        args=(self.root/'launch').read_text().splitlines();self.assertEqual(args[:2],['x128','-80col'])
        self.assertEqual(preferences.read(self.home/'.config/project-cbm')['values']['default_machine'],'x64sc')

    def test_malformed_recovery_cancel_then_confirm(self):
        target=self.home/'.config/project-cbm';target.mkdir(parents=True,mode=0o700)
        f=target/'preferences.json';f.write_text('{bad');f.chmod(0o600)
        p=self.run_ui('pcbm-machines',['DEFAULT','xvic','CANCEL','RETURN','RETURN'])
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(f.read_text(),'{bad')
        p=self.run_ui('pcbm-machines',['DEFAULT','xvic','MESSAGE'])
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(f.read_text())['default_machine'],'xvic')
        self.assertEqual(next(target.glob('preferences.invalid.*')).read_text(),'{bad')

    def test_information_view_textbox_back_and_cleanup(self):
        for choice in ['MESSAGE','ESC','CANCEL']:
            p=self.run_ui('pcbm-system-info',[choice]);self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('HARDWARE',(self.root/'view').read_text())
        self.assertFalse(list(self.root.glob('pcbm-information.*')))

    def test_information_invocation_failure_and_small_terminal(self):
        p=self.run_ui('pcbm-system-info',['MESSAGE'],INFO_STATUS='2');self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('Information is unavailable',(self.root/'dialog-args').read_text())
        p=self.run_ui('pcbm-system-info',[],COLUMNS='30');self.assertEqual(p.returncode,5)
        self.assertNotIn('Traceback',p.stderr);self.assertFalse(list(self.root.glob('pcbm-information.*')))


if __name__=='__main__':unittest.main()
