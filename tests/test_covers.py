"""Cover mapping/launcher/SDL lifetime fixtures; no physical graphics claim."""
import hashlib
import ctypes as C
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT.parent/'project-cbm'
spec=importlib.util.spec_from_file_location('cover_view',ROOT/'lib/pcbm_cover_view.py')
view=importlib.util.module_from_spec(spec);spec.loader.exec_module(view)
sys.path.insert(0,str(PRODUCT/'runtime'))
from project_cbm.data import registry
from project_cbm import preferences
from project_cbm.applications import application_profile

class SDL:
    def __init__(self,fail=False):self.calls=[];self.fail=fail
    def __getattr__(self,name):
        def call(*args):
            self.calls.append(name)
            if name=='SDL_GetCurrentDisplayMode':args[1]._obj.w=1920;args[1]._obj.h=1080
            if name=='SDL_QueryTexture':args[3]._obj.value=600;args[4]._obj.value=600
            if name=='SDL_GetRendererOutputSize':args[1]._obj.value=1920;args[2]._obj.value=1080
            if name in ('SDL_CreateWindow','SDL_CreateRenderer'):return 1
            if name=='IMG_LoadTexture':return 0 if self.fail else 1
            return 0
        return call

class CoverRenderer(unittest.TestCase):
    def test_exact_asset_manifest_and_package_payload(self):
        manifest=json.loads((ROOT/'docs/cover-artwork.json').read_text())
        entries=manifest['files'];self.assertEqual(len(entries),7)
        install=(ROOT/'debian/install').read_text()
        for entry in entries:
            payload=(ROOT/entry['path']).read_bytes()
            self.assertEqual(len(payload),entry['size_bytes'])
            self.assertEqual(hashlib.sha256(payload).hexdigest(),entry['sha256'])
            self.assertIn(entry['path']+' usr/share/project-cbm-menu/covers',install)
        self.assertNotIn('covers/*',install)
        self.assertIn('third-party',manifest['license_evidence'])
    def test_primary_is_exact_existing_private_art_and_separate_dwell(self):
        manifest=json.loads((ROOT/'docs/primary-artwork.json').read_text())
        entry=manifest['file'];payload=(ROOT/entry['path']).read_bytes()
        self.assertEqual(len(payload),entry['size_bytes'])
        self.assertEqual(hashlib.sha256(payload).hexdigest(),entry['sha256'])
        self.assertIn(entry['path']+' usr/share/project-cbm-menu/covers',(ROOT/'debian/install').read_text())
        for primary,duration in ((False,.75),(True,1.5)):
            clock=[0.0];sdl=SDL()
            with patch.object(view.time,'monotonic',side_effect=lambda:clock[0]),patch.object(view.time,'sleep',side_effect=lambda t:clock.__setitem__(0,clock[0]+t)),patch.object(view,'telemetry'):
                self.assertEqual(view.display(Path('fixture.jpg'),sdl,sdl,primary=primary),0)
            self.assertGreaterEqual(clock[0],duration)
            self.assertLess(clock[0],duration+.05)
        self.assertNotIn('/usr/bin/pcbm-cover\n',(ROOT/'scripts/pcbm-menu').read_text())
    def test_boot_holds_until_ready_and_minimum_visible_time(self):
        for ready_time in (0,5):
            clock=[0.0];sdl=SDL();readfd,writefd=os.pipe();sent=[False]
            def pause(seconds):
                clock[0]+=seconds
                if not sent[0] and clock[0]>=ready_time:
                    os.write(writefd,b'1');sent[0]=True
            try:
                with patch.object(view.time,'monotonic',side_effect=lambda:clock[0]),patch.object(view.time,'sleep',side_effect=pause),patch.object(view,'telemetry'):
                    self.assertEqual(view.display(Path('fixture.jpg'),sdl,sdl,primary=True,control_fd=readfd),0)
                self.assertGreaterEqual(clock[0],max(3,ready_time))
                self.assertLess(clock[0],max(3,ready_time)+.05)
                self.assertEqual(sdl.calls[-1],'SDL_Quit')
            finally:os.close(readfd);os.close(writefd)

    def test_fit_does_not_stretch_artwork(self):
        for dw,dh,iw,ih in [(1920,1080,600,600),(640,480,1200,600),(320,240,600,1200)]:
            r=view.fit(dw,dh,iw,ih)
            self.assertLessEqual(r.w,dw);self.assertLessEqual(r.h,dh)
            self.assertAlmostEqual(r.w/r.h,iw/ih,delta=.02)
            self.assertGreaterEqual(r.x,0);self.assertGreaterEqual(r.y,0)
    def test_success_and_failure_release_every_created_resource(self):
        for failed in (False,True):
            sdl=SDL(failed)
            with patch.object(view,'DURATION_SECONDS',.001),patch.object(view.time,'sleep'):
                result=view.display(Path('synthetic.jpg'),sdl,sdl)
            self.assertEqual(result,int(failed))
            self.assertEqual(sdl.calls[-4:],['SDL_DestroyRenderer','SDL_DestroyWindow','IMG_Quit','SDL_Quit'])
            if not failed:self.assertIn('SDL_DestroyTexture',sdl.calls)
    def test_first_present_delay_does_not_consume_visible_dwell(self):
        now=[0.0];frames=[];events=[]
        sdl=SDL();original=sdl.SDL_RenderPresent
        def present(renderer):
            if not frames:now[0]+=1.0
            frames.append(now[0]);return original(renderer)
        sdl.SDL_RenderPresent=present
        def pause(seconds):now[0]+=seconds
        with patch.object(view.time,'monotonic',side_effect=lambda:now[0]),patch.object(view.time,'sleep',side_effect=pause),patch.object(view,'telemetry',side_effect=lambda stage,**fields:events.append({'stage':stage,**fields})):
            self.assertEqual(view.display(Path('synthetic.jpg'),sdl,sdl),0)
        self.assertGreaterEqual(now[0]-frames[0],.75)
        self.assertGreater(len(frames),1)
        stages=[x['stage'] for x in events]
        self.assertEqual(stages,['initializing','video','decoder_init','window_create','renderer_create','renderer','texture_load','present_begin','presented','releasing','released'])
        self.assertTrue(all(type(x['elapsed_ms']) is int for x in events))
        self.assertEqual(events[8]['elapsed_ms'],1000)
    def test_no_root_framebuffer_vt_or_mode_change_commands(self):
        text=(ROOT/'lib/pcbm_cover_view.py').read_text()+(ROOT/'scripts/pcbm-cover').read_text()
        for forbidden in ('sudo','fbset','fbi ', 'convert ', 'chvt','SDL_SetDisplayMode','/dev/fb0'):
            self.assertNotIn(forbidden,text)
        self.assertIn('0x1001',text)
        self.assertIn('os.geteuid() == 0',text)
    def test_registry_maps_to_existing_exact_machine_art(self):
        rows=registry();self.assertEqual(len(rows),11)
        for row in rows:self.assertTrue((ROOT/'covers'/('pcbmcover-'+row['cover_asset']+'.jpg')).is_file())
        by_id={r['id']:r['cover_asset'] for r in rows}
        self.assertEqual(by_id['x128-80col'],'c128');self.assertEqual(by_id['x64sc'],'c64');self.assertEqual(by_id['xvic'],'vic20')

class CoverLaunch(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.bin=self.root/'usr/bin';self.bin.mkdir(parents=True)
        self.home=self.root/'home/pcbm';(self.home/'content').mkdir(parents=True)
        self.covers=self.root/'usr/share/project-cbm-menu/covers';self.covers.mkdir(parents=True)
        self.lib=self.root/'usr/libexec/project-cbm-menu';self.lib.mkdir(parents=True)
        lifecycle=self.root/'usr/libexec/project-cbm/engineering.py';lifecycle.parent.mkdir(parents=True)
        lifecycle.write_text('#!/bin/bash\n[[ $1 == run-with-cover ]] || exit 2\nprofile=$2;shift 2\n'+str(self.bin)+'/pcbm-cover --profile "$profile" || true\nexec "$@"\n');lifecycle.chmod(0o755)
        for name in ('pcbm-run-vice','pcbm-boot','pcbm-cover'):
            text=(ROOT/'scripts'/name).read_text()
            for prefix in ('/usr/bin/','/usr/libexec/','/usr/share/','/etc/pcbm/','/home/pcbm'):
                text=text.replace(prefix,str(self.root)+prefix)
            self.write(name,text)
        self.write('pcbm-profiles','#!/bin/bash\nexec '+sys.executable+' '+str(PRODUCT/'runtime/bin/pcbm-profiles')+' "$@"\n')
        # Timeout mechanics tested separately with actual GNU timeout in Linux staging.
        self.write('timeout','#!/bin/bash\n[[ $1 == --signal=TERM && $2 == --kill-after=0.5s && $3 == 2s ]] || exit 1\nshift 3\nexec "$@"\n')
        self.write('tty','#!/bin/bash\necho /dev/tty1\n')
        (self.bin/'python3').symlink_to(sys.executable)
        (self.lib/'pcbm_cover_view.py').write_text('import os,sys\nif sys.argv[1:] == ["--admit"]: raise SystemExit(0)\nwith open(os.environ["TRACE"],"a") as f:f.write("cover:"+sys.argv[1]+"\\n")\nraise SystemExit(int(os.environ.get("COVER_FAIL","0")))\n')
        for n in ('x64sc','xvic','x128'):
            self.write(n,'#!/bin/bash\nprintf "%s\\n" "vice:'+n+'" "$@" >> "$TRACE"\nexit "${VICE_FAIL:-0}"\n')
        self.env={**os.environ,'PATH':str(self.bin)+':'+os.environ['PATH'],'XDG_CONFIG_HOME':str(self.home/'.config'),'TRACE':str(self.root/'trace')}
        for name in ('c64','vic20','c128'):(self.covers/('pcbmcover-'+name+'.jpg')).write_bytes(b'fixture renderer is mocked')
    def write(self,n,t):
        p=self.bin/n;p.write_text(t);p.chmod(0o755)
    def run_launch(self,*args,command='pcbm-run-vice',**env):
        return subprocess.run(['bash',str(self.bin/command),*args],env={**self.env,**env},capture_output=True,text=True,timeout=5)
    def trace(self):return (self.root/'trace').read_text().splitlines()
    def test_default_and_explicit_use_selected_profile_cover(self):
        preferences.update({'default_machine':'xvic'},self.home/'.config/project-cbm')
        self.assertEqual(self.run_launch(command='pcbm-boot').returncode,0)
        self.assertTrue(self.trace()[0].endswith('pcbmcover-vic20.jpg'))
        (self.root/'trace').unlink()
        self.assertEqual(self.run_launch('x128-80col').returncode,0)
        self.assertTrue(self.trace()[0].endswith('pcbmcover-c128.jpg'))
        self.assertEqual(self.trace()[1:3],['vice:x128','-80col'])
    def test_content_profile_wins_over_user_default_and_retains_return(self):
        preferences.update({'default_machine':'xvic'},self.home/'.config/project-cbm')
        media=self.home/'content/music/Creation/SID-Wizard/test disk.d64';media.parent.mkdir(parents=True); disk=bytearray(174848);disk[357*256:357*256+3]=bytes([18,1,65]);disk[358*256+2]=2;media.write_bytes(disk);media=media.resolve()
        resolved=application_profile(media,registry(),self.home/'content')
        p=self.run_launch(resolved,str(media),VICE_FAIL='9')
        self.assertEqual(p.returncode,9);self.assertTrue(self.trace()[0].endswith('pcbmcover-c64.jpg'))
        self.assertIn('-menukey',self.trace());self.assertIn('291',self.trace());self.assertIn(str(media),self.trace())
        self.assertEqual(preferences.read(self.home/'.config/project-cbm')['values']['default_machine'],'xvic')
    def test_missing_or_failed_cover_still_launches_once(self):
        for failed in ('missing','renderer'):
            with self.subTest(failed=failed):
                (self.root/'trace').unlink(missing_ok=True)
                asset=self.covers/'pcbmcover-c64.jpg'
                if failed=='missing':asset.unlink()
                else:asset.write_bytes(b'fixture')
                p=self.run_launch('x64sc',COVER_FAIL='1');self.assertEqual(p.returncode,0)
                self.assertEqual(self.trace().count('vice:x64sc'),1)
                if failed=='missing':self.assertFalse(any(x.startswith('cover:') for x in self.trace()))
    def test_invalid_profile_or_SID_never_renders(self):
        sid=self.home/'content/test.sid';sid.write_bytes(b'synthetic')
        for args in [('bad;id',),('x64sc',str(sid))]:
            self.assertEqual(self.run_launch(*args).returncode,2)
            self.assertFalse((self.root/'trace').exists())
    def test_single_owner_and_no_random_cover_fallback(self):
        lib=(ROOT/'scripts/pcbm-dialog-lib.sh').read_text()
        block=lib[lib.index('pcbm_launch_machine()'):lib.index('pcbm_launch_content()')]
        self.assertNotIn('pcbm-cover',block)
        self.assertNotIn('RANDOM',(ROOT/'scripts/pcbm-cover').read_text())

if __name__=='__main__':unittest.main()
