"""Kernel-query fixtures, not physical Pi qualification."""
import contextlib,io,os,struct,unittest
from unittest.mock import patch
from test_covers import view
class Admission(unittest.TestCase):
 def run_guard(self,device=0x401,control_device=0x401,vt=1,foreground=50,terminal=True,error=False):
  calls=[]
  def ioctl(fd,op,value,mutate):
   calls.append((fd,op))
   if error:raise OSError('unavailable')
   if op==0x80045432:value[0]=device if fd==0 else control_device
   elif op==0x5603:value[:]=struct.pack('=HHH',vt,0,2)
   else:raise AssertionError('non-read-only ioctl')
  with patch.object(view.sys,'platform','linux'),patch.object(view.os,'geteuid',return_value=1000),patch.object(view.os,'isatty',return_value=terminal),patch.object(view.os,'open',return_value=42) as opened,patch.object(view.os,'close') as close,patch.object(view.os,'tcgetpgrp',return_value=foreground),patch.object(view.os,'getpgrp',return_value=50),patch.object(view.os,'ttyname',side_effect=AssertionError('pathname admission forbidden')),patch.object(view.fcntl,'ioctl',side_effect=ioctl):
   result=view.admission()
   if terminal:close.assert_called_once_with(42)
   else:opened.assert_not_called()
   return result,calls
 def test_direct_and_alias_use_underlying_tty1_without_pathnames(self):
  result,calls=self.run_guard();self.assertEqual(result,'admitted');self.assertEqual([v[1] for v in calls],[0x80045432,0x80045432,0x5603])
 def test_wrong_terminal_or_controlling_terminal_rejected(self):
  for values in [{'device':0x402},{'control_device':0x402},{'device':0x8800}]:self.assertEqual(self.run_guard(**values)[0],'skip_wrong_tty')
 def test_inactive_background_and_nonterminal_rejected(self):
  for values,expected in [({'vt':2},'skip_inactive_vt'),({'foreground':99},'skip_background'),({'terminal':False},'skip_nonterminal'),({'error':True},'skip_tty_unavailable')]:self.assertEqual(self.run_guard(**values)[0],expected)
 def test_root_and_non_linux_fail_open_stage(self):
  with patch.object(view.os,'geteuid',return_value=0):self.assertEqual(view.admission(),'skip_root')
  with patch.object(view.os,'geteuid',return_value=1000),patch.object(view.sys,'platform','darwin'):self.assertEqual(view.admission(),'skip_non_linux')
 def test_cli_fixed_admission_and_skip_diagnostics(self):
  for outcome in ['admitted','skip_wrong_tty']:
   output=io.StringIO()
   with patch.object(view,'admission',return_value=outcome),contextlib.redirect_stdout(output):status=view.main(['--admit'])
   self.assertEqual(status,0 if outcome=='admitted' else 2);self.assertIn('"stage": "'+outcome+'"',output.getvalue())
if __name__=='__main__':unittest.main()
