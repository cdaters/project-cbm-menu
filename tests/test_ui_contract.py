"""New UI contract only; fake dialog never operates the real terminal."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class UI(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.fake=Path(self.tmp.name)/'dialog'
        self.fake.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$ARGUMENTS"\nprintf "%s" "$CHOICE"\nexit "$RESULT"\n')
        self.fake.chmod(0o755)

    def invoke(self,rc=0,choice='RUN',call='pcbm_ui_menu Title Prompt RUN Run INFO Information',cols='80',lines='24'):
        args=Path(self.tmp.name)/'args'
        env={**os.environ,'PCBM_DIALOG_BIN':str(self.fake),'ARGUMENTS':str(args),'RESULT':str(rc),'CHOICE':choice,'COLUMNS':cols,'LINES':lines}
        code='set -euo pipefail\nsource "$1"\nif '+call+'; then result=0; else result=$?; fi\nprintf "%s|%s|%s" "$result" "$PCBM_UI_STATUS" "$PCBM_UI_CHOICE"'
        result=subprocess.run(['/bin/bash','-c',code,'test',str(ROOT/'lib/pcbm-ui.sh')],env=env,text=True,capture_output=True,check=True)
        return result.stdout,args.read_text() if args.exists() else ''

    def test_selection(self):
        s,args=self.invoke();self.assertEqual(s,'0|success|RUN');self.assertIn('--no-mouse',args)

    def test_cancel_escape_failure(self):
        for rc,status in [(1,'1|cancel|'),(255,'2|back|'),(2,'3|failure|'),(127,'3|failure|'),(254,'3|failure|')]:
            with self.subTest(rc):self.assertEqual(self.invoke(rc)[0],status)

    def test_unexpected_selection_rejected(self):
        self.assertEqual(self.invoke(choice='not-listed')[0],'3|failure|')

    def test_bad_arguments(self):
        for cmd in ['pcbm_ui_menu Title Prompt ONE','pcbm_ui_menu Title Prompt A A A Again','pcbm_ui_result 42']:
            self.assertIn(self.invoke(call=cmd)[0],('4|validation_error|','3|failure|'))

    def test_small_terminal_and_malicious_dimensions(self):
        self.assertEqual(self.invoke(cols='30')[0],'5|unavailable|')
        self.assertEqual(self.invoke(cols='$(touch bad)')[0],'4|validation_error|')

    def test_confirmation_safe_default(self):
        result,args=self.invoke(choice='',call='pcbm_ui_confirm Confirm Proceed')
        self.assertEqual(result,'0|success|');self.assertIn('--defaultno',args)

    def test_information_message(self):
        self.assertEqual(self.invoke(choice='',call='pcbm_ui_message Info Ready')[0],'0|success|')

    def test_no_domain_operation_on_cancel(self):
        for rc,expected in [(0,'0|success|RUN'),(1,'1|cancel|')]:
            marker=Path(self.tmp.name)/'domain'
            cmd='pcbm_ui_menu Title Prompt RUN Run && printf applied > "'+str(marker)+'"'
            self.assertEqual(self.invoke(rc,call=cmd)[0],expected)
            self.assertEqual(marker.exists(),rc==0)
            if marker.exists():marker.unlink()

    def test_no_output_or_probe_when_sourced(self):
        result=subprocess.run(['/bin/bash','-c','source "$1"','test',str(ROOT/'lib/pcbm-ui.sh')],capture_output=True,check=True)
        self.assertEqual(result.stdout,b'');self.assertEqual(result.stderr,b'')

    def test_escape_payload_and_missing_dialog(self):
        self.assertEqual(self.invoke(call="pcbm_ui_message Info $'bad\\e[31m'")[0],'4|validation_error|')
        self.assertEqual(self.invoke(call="pcbm_ui_message Info $'bad\\a'")[0],'4|validation_error|')
        self.fake.unlink()
        self.assertEqual(self.invoke()[0],'5|unavailable|')


if __name__=='__main__':unittest.main()
