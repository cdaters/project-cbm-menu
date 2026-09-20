"""Short, unprivileged SDL2 cover process. MIT, Project CBM contributors.

Existing SDL2/SDL2_image libraries; Python stdlib only. Owns no persistent state.
The launcher bounds the entire subprocess and waits for exit before starting VICE.
"""
import array
import fcntl
import struct
import ctypes as C
import ctypes.util
import os
import json
import re
from pathlib import Path
import signal
import select
import sys
import time

DURATION_SECONDS = 0.75
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_DIMENSION = 4096


class Rect(C.Structure):
    _fields_ = [('x', C.c_int), ('y', C.c_int), ('w', C.c_int), ('h', C.c_int)]


class DisplayMode(C.Structure):
    _fields_ = [('format', C.c_uint32), ('w', C.c_int), ('h', C.c_int),
                ('refresh_rate', C.c_int), ('driverdata', C.c_void_p)]


class Event(C.Union):
    _fields_ = [('type', C.c_uint32), ('padding', C.c_uint64 * 8)]


class RendererInfo(C.Structure):
    _fields_ = [('name',C.c_char_p),('flags',C.c_uint32),('num_texture_formats',C.c_uint32),
                ('texture_formats',C.c_uint32*16),('max_texture_width',C.c_int),('max_texture_height',C.c_int)]


def telemetry(stage, **fields):
    # Fixed diagnostic fields only: never SDL error text, environment or asset paths.
    print('PCBM_COVER '+json.dumps({'stage':stage,**fields}),flush=True)


def label(value):
    value=value.decode('ascii',errors='replace') if isinstance(value,bytes) else ''
    return value if re.fullmatch(r'[A-Za-z0-9_-]{1,40}',value) else 'unknown'


def admission(fd=0):
    """Read kernel tty identity, never change a VT, foreground group or tty mode."""
    if os.geteuid() == 0: return 'skip_root'
    if not sys.platform.startswith('linux'): return 'skip_non_linux'
    control = None
    try:
        if not os.isatty(fd): return 'skip_nonterminal'
        control = os.open('/dev/tty', os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
        def device(handle):
            value = array.array('I', [0])
            fcntl.ioctl(handle, 0x80045432, value, True)  # Linux TIOCGDEV: new_encode_dev
            return value[0]
        # Linux console tty1 is major 4, minor 1 (encoded 0x401). This works
        # for both a direct tty1 descriptor and the controlling /dev/tty alias.
        if device(fd) != 0x401 or device(control) != 0x401: return 'skip_wrong_tty'
        state = bytearray(6)
        fcntl.ioctl(control, 0x5603, state, True)  # VT_GETSTATE, three unsigned shorts
        if struct.unpack('=HHH', state)[0] != 1: return 'skip_inactive_vt'
        if os.tcgetpgrp(control) != os.getpgrp(): return 'skip_background'
        return 'admitted'
    except OSError:
        return 'skip_tty_unavailable'
    finally:
        if control is not None: os.close(control)


def fit(width, height, image_width, image_height):
    if min(width, height, image_width, image_height) <= 0:
        raise ValueError('invalid dimensions')
    # Preserve the existing artwork's proportions and approximately half-screen height.
    scale = min(width * 0.9 / image_width, height * 0.5 / image_height)
    w, h = max(1, int(image_width * scale)), max(1, int(image_height * scale))
    return Rect((width-w)//2, (height-h)//2, w, h)


def bind(lib, name, result, args):
    function = getattr(lib, name); function.restype = result; function.argtypes = args
    return function


def libraries():
    sdl = C.CDLL('libSDL2-2.0.so.0' if sys.platform.startswith('linux') else ctypes.util.find_library('SDL2'))
    img = C.CDLL('libSDL2_image-2.0.so.0' if sys.platform.startswith('linux') else ctypes.util.find_library('SDL2_image'))
    p, i, u = C.c_void_p, C.c_int, C.c_uint32
    for name, result, args in [
        ('SDL_Init', i, [u]), ('SDL_Quit', None, []),
        ('SDL_GetCurrentVideoDriver', C.c_char_p, []),
        ('SDL_GetRendererInfo', i, [p,C.POINTER(RendererInfo)]),
        ('SDL_GetCurrentDisplayMode', i, [i, C.POINTER(DisplayMode)]),
        ('SDL_CreateWindow', p, [C.c_char_p, i, i, i, i, u]),
        ('SDL_DestroyWindow', None, [p]), ('SDL_CreateRenderer', p, [p, i, u]),
        ('SDL_DestroyRenderer', None, [p]), ('SDL_DestroyTexture', None, [p]),
        ('SDL_QueryTexture', i, [p, C.POINTER(u), C.POINTER(i), C.POINTER(i), C.POINTER(i)]),
        ('SDL_GetRendererOutputSize', i, [p, C.POINTER(i), C.POINTER(i)]),
        ('SDL_SetRenderDrawColor', i, [p, C.c_uint8, C.c_uint8, C.c_uint8, C.c_uint8]),
        ('SDL_RenderClear', i, [p]), ('SDL_RenderCopy', i, [p, p, C.POINTER(Rect), C.POINTER(Rect)]),
        ('SDL_RenderPresent', None, [p]), ('SDL_PollEvent', i, [C.POINTER(Event)]),
        ('SDL_ShowCursor', i, [i])]:
        bind(sdl, name, result, args)
    bind(img, 'IMG_Init', i, [i]); bind(img, 'IMG_Quit', None, [])
    bind(img, 'IMG_LoadTexture', p, [p, C.c_char_p])
    return sdl, img


def display(path, sdl, img, primary=False, control_fd=None):
    window = renderer = texture = None
    stopping = False
    def stop(signum, frame):
        nonlocal stopping
        stopping = True
    previous = {s: signal.signal(s, stop) for s in (signal.SIGTERM, signal.SIGINT)}
    started=time.monotonic()
    def stage(name, **fields):
        telemetry(name, elapsed_ms=int((time.monotonic()-started)*1000), **fields)
    try:
        stage('initializing')
        if sdl.SDL_Init(0x20) != 0: return 1  # VIDEO only, no audio initialization.
        stage('video',driver=label(sdl.SDL_GetCurrentVideoDriver()))
        stage('decoder_init')
        img.IMG_Init(3)  # JPG / PNG; load failure remains a non-blocking fallback.
        mode = DisplayMode()
        if sdl.SDL_GetCurrentDisplayMode(0, C.byref(mode)) != 0: return 1
        stage('window_create')
        window = sdl.SDL_CreateWindow(b'Project CBM cover', 0x1fff0000, 0x1fff0000,
                                      mode.w, mode.h, 0x1001)  # FULLSCREEN_DESKTOP
        if not window: return 1
        stage('renderer_create')
        renderer = sdl.SDL_CreateRenderer(window, -1, 2) or sdl.SDL_CreateRenderer(window, -1, 1)
        if not renderer: return 1
        info=RendererInfo()
        if sdl.SDL_GetRendererInfo(renderer,C.byref(info))==0:
            stage('renderer',renderer=label(info.name))
        stage('texture_load')
        texture = img.IMG_LoadTexture(renderer, os.fsencode(path))
        if not texture: return 1
        iw, ih, width, height = (C.c_int() for _ in range(4))
        if sdl.SDL_QueryTexture(texture, None, None, C.byref(iw), C.byref(ih)) != 0: return 1
        if min(iw.value, ih.value) <= 0 or max(iw.value, ih.value) > MAX_DIMENSION: return 1
        if sdl.SDL_GetRendererOutputSize(renderer, C.byref(width), C.byref(height)) != 0: return 1
        rect = fit(width.value, height.value, iw.value, ih.value)
        sdl.SDL_ShowCursor(0)
        if sdl.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255) != 0: return 1
        # First present may block during KMS/driver setup. Start visible dwell
        # only after it returns; initialization must not consume presentation.
        event = Event(); deadline = None;presented=False;release_requested=False
        stage('present_begin')
        while not stopping:
            if control_fd is not None and not release_requested and select.select([control_fd],[],[],0)[0]:
                os.read(control_fd,1);release_requested=True
            if deadline is not None and time.monotonic() >= deadline:
                if control_fd is None or release_requested:break
            # Parent also bounds/reaps us; this protects loss of the coordinator.
            if time.monotonic()-started>=28:break
            while sdl.SDL_PollEvent(C.byref(event)):
                if event.type == 0x100: stopping = True  # Window quit, not a held RUN key.
            if sdl.SDL_RenderClear(renderer) != 0: return 1
            if sdl.SDL_RenderCopy(renderer, texture, None, C.byref(rect)) != 0: return 1
            sdl.SDL_RenderPresent(renderer)
            if not presented:
                deadline = time.monotonic() + (3.0 if control_fd is not None else 1.5 if primary else DURATION_SECONDS)
                stage('presented',width=width.value,height=height.value);presented=True
            time.sleep(0.02)
        return 0
    finally:
        stage('releasing')
        try:
            try:
                if texture: sdl.SDL_DestroyTexture(texture)
            finally:
                try:
                    if renderer: sdl.SDL_DestroyRenderer(renderer)
                finally:
                    try:
                        if window: sdl.SDL_DestroyWindow(window)
                    finally:
                        try:img.IMG_Quit()
                        finally:sdl.SDL_Quit()
        finally:
            for sig, handler in previous.items(): signal.signal(sig, handler)
            stage('released')


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ['--admit']:
        result = admission()
        telemetry(result)
        return 0 if result == 'admitted' else 2
    boot = len(argv)==2 and argv[0]=='--boot'
    primary = boot or len(argv)==2 and argv[0]=='--primary'
    if primary: argv=argv[1:]
    if os.geteuid() == 0 or len(argv) != 1: return 1
    path = Path(argv[0]); base = Path('/usr/share/project-cbm-menu/covers')
    try:
        if path.parent != base or path.is_symlink() or not path.is_file(): return 1
        if path.resolve().parent != base.resolve(): return 1
        if path.suffix not in ('.jpg', '.png') or not 0 < path.stat().st_size <= MAX_FILE_BYTES: return 1
        if primary and path.name!='pcbmcover1.jpg': return 1
        control_fd=None
        if boot:
            value=os.environ.get('PCBM_BOOT_CONTROL_FD','')
            if not value.isdecimal() or not 3<=int(value)<=1024:return 1
            control_fd=int(value);os.fstat(control_fd)
        return display(path, *libraries(), primary=primary,control_fd=control_fd)
    except (OSError, ValueError, AttributeError):
        return 1  # Caller always proceeds to VICE; no display/terminal repair commands.


if __name__ == '__main__':
    raise SystemExit(main())
