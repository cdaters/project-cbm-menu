import os
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

class ReleasePolish(unittest.TestCase):
 def test_content_discovery_and_narrow_metadata_policy(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp)
   keep=['.hidden/game.d64','c128/double.g71','c64/.demo.prg','normal/tape.tap','normal/cart.crt']
   omit=['._game.d64','.Trashes/trash.prg','.AppleDouble/fork.prg','__MACOSX/a.d64','.TemporaryItems/a.prg','System Volume Information/a.prg']
   for name in keep+omit:
    p=base/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('test')
   lib=(ROOT/'scripts/pcbm-dialog-lib.sh').read_text();start=lib.index('pcbm_filtered_find()');end=lib.index('pcbm_copy_clean()',start)
   env=dict(os.environ,CBM_TEST_ROOT=str(base))
   result=subprocess.check_output(['bash','-c',lib[start:end]+'\npcbm_find_content_files "$CBM_TEST_ROOT"'],env=env)
   actual={str(Path(x.decode()).relative_to(base)) for x in result.split(b'\0') if x}
   self.assertEqual(actual,set(keep))
 def test_password_guidance_and_artwork_scope(self):
  text=(ROOT/'scripts/pcbm-config').read_text()
  self.assertIn('12-128 printable characters; colon (:) is not accepted',text)
  copyright=(ROOT/'debian/copyright').read_text()
  for name in ('Project-CBM-Branding','Project-CBM-Covers'):self.assertIn('License: '+name,copyright)
  self.assertIn('License: MIT',copyright)
