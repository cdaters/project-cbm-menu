from pathlib import Path
import subprocess,tempfile,os
src=(Path(__file__).resolve().parents[1]/'scripts/pcbm-run-vice').read_text()
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);home=root/'home/pi';(home/'pcbm').mkdir(parents=True);(root/'usr/bin').mkdir(parents=True)
 script=root/'run';script.write_text(src.replace('/home/pi',str(home)).replace('/usr/bin/',str(root/'usr/bin')+'/').replace('/usr/libexec/',str(root/'usr/libexec')+'/').replace('/etc/pcbm/',str(root/'etc/pcbm')+'/'))
 emu=root/'usr/bin/x64sc';emu.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$TEST_ARGS"\nexit "${TEST_STATUS:-0}"\n');emu.chmod(0o755)
 media=home/'pcbm/test content.prg';media.write_text('owned test')
 env=dict(os.environ,TEST_ARGS=str(root/'args'))
 for args in [['x64sc'],['x64sc',str(media)]]:
  p=subprocess.run(['bash',str(script),*args],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  assert p.returncode==0,p.stderr
  actual=(root/'args').read_text().splitlines();assert actual[:4]==['-sounddev','sdl','-menukey','291']
  if len(args)>1:assert actual[-2:]==['-autostart',str(media)]
 env['TEST_STATUS']='9';assert subprocess.run(['bash',str(script),'x64sc'],env=env,stdout=subprocess.DEVNULL).returncode==9
 assert subprocess.run(['bash',str(script),'arbitrary'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==2
print('Shared Bash launcher: RUN/content argv, spaces, failure status and invalid profile PASS')
