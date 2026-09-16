"""Actual content-browser routing with controlled UI/backend; no VICE or root."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

class OptionalContent(unittest.TestCase):
    def test_application_resolver_and_return_are_used(self):
        for failed in (False,True):
            with self.subTest(failed=failed),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);media=root/'content/music/Creation/SID-Wizard/test disk.d64'
                media.parent.mkdir(parents=True);media.write_bytes(b'fixture; backend mocked')
                resolver=root/'profiles';resolver.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$RESOLVED"\n'+('exit 2\n' if failed else 'echo x64sc\n'));resolver.chmod(0o755)
                src=(ROOT/'scripts/pcbm-content').read_text().replace('/usr/bin/pcbm-profiles',str(resolver))
                (root/'pcbm-content').write_text(src)
                (root/'pcbm-dialog-lib.sh').write_text(r'''pcbm_trap_cleanup() { :; }
pcbm_default_machine_label() { echo 'Commodore VIC-20'; }
pcbm_find_content_files() { printf '%s\0' "$MEDIA"; }
pcbm_show_msg() { printf '%s\n' "$@" >> "$MESSAGES"; }
pcbm_infobox() { :; }
pcbm_launch_content() { printf '%s\n' "$@" > "$LAUNCHED"; }
sleep() { :; }
count=0
pcbm_show_menu() {
 count=$((count+1));PCBM_STATUS=0
 case $count in 1) PCBM_CHOICE=MUSIC;; 2) PCBM_CHOICE=0;; 3) PCBM_CHOICE=RETURN;; *) exit 0;; esac
}
''')
                env={**os.environ,'PCBM_CONTENT_BASE':str(root/'content'),'MEDIA':str(media),
                     'RESOLVED':str(root/'resolved'),'LAUNCHED':str(root/'launched'),'MESSAGES':str(root/'messages')}
                result=subprocess.run(['bash',str(root/'pcbm-content')],env=env,capture_output=True,text=True,timeout=5)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual((root/'resolved').read_text().splitlines(),['content-profile',str(media)])
                if failed:
                    self.assertFalse((root/'launched').exists());self.assertIn('unavailable',(root/'messages').read_text())
                else:self.assertEqual((root/'launched').read_text().splitlines(),['x64sc',str(media)])
