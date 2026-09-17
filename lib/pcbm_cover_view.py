"""Short, unprivileged SDL2 cover process. MIT, Project CBM contributors.

Existing SDL2/SDL2_image libraries; Python stdlib only. Owns no persistent state.
The launcher bounds the entire subprocess and waits for exit before starting VICE.
"""
import ctypes as C
import ctypes.util
import os
from pathlib import Path
import signal
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


def display(path, sdl, img):
    window = renderer = texture = None
    stopping = False
    def stop(signum, frame):
        nonlocal stopping
        stopping = True
    previous = {s: signal.signal(s, stop) for s in (signal.SIGTERM, signal.SIGINT)}
    try:
        if sdl.SDL_Init(0x20) != 0: return 1  # VIDEO only, no audio initialization.
        img.IMG_Init(3)  # JPG / PNG; load failure remains a non-blocking fallback.
        mode = DisplayMode()
        if sdl.SDL_GetCurrentDisplayMode(0, C.byref(mode)) != 0: return 1
        window = sdl.SDL_CreateWindow(b'Project CBM cover', 0x1fff0000, 0x1fff0000,
                                      mode.w, mode.h, 0x1001)  # FULLSCREEN_DESKTOP
        if not window: return 1
        renderer = sdl.SDL_CreateRenderer(window, -1, 2) or sdl.SDL_CreateRenderer(window, -1, 1)
        if not renderer: return 1
        texture = img.IMG_LoadTexture(renderer, os.fsencode(path))
        if not texture: return 1
        iw, ih, width, height = (C.c_int() for _ in range(4))
        if sdl.SDL_QueryTexture(texture, None, None, C.byref(iw), C.byref(ih)) != 0: return 1
        if min(iw.value, ih.value) <= 0 or max(iw.value, ih.value) > MAX_DIMENSION: return 1
        if sdl.SDL_GetRendererOutputSize(renderer, C.byref(width), C.byref(height)) != 0: return 1
        rect = fit(width.value, height.value, iw.value, ih.value)
        sdl.SDL_ShowCursor(0)
        if sdl.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255) != 0: return 1
        event = Event(); deadline = time.monotonic() + DURATION_SECONDS
        while not stopping and time.monotonic() < deadline:
            while sdl.SDL_PollEvent(C.byref(event)):
                if event.type in (0x100, 0x300): stopping = True  # Quit / any key skips.
            if sdl.SDL_RenderClear(renderer) != 0: return 1
            if sdl.SDL_RenderCopy(renderer, texture, None, C.byref(rect)) != 0: return 1
            sdl.SDL_RenderPresent(renderer)
            time.sleep(0.02)
        return 0
    finally:
        if texture: sdl.SDL_DestroyTexture(texture)
        if renderer: sdl.SDL_DestroyRenderer(renderer)
        if window: sdl.SDL_DestroyWindow(window)
        img.IMG_Quit(); sdl.SDL_Quit()
        for sig, handler in previous.items(): signal.signal(sig, handler)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if os.geteuid() == 0 or len(argv) != 1: return 1
    path = Path(argv[0]); base = Path('/usr/share/project-cbm-menu/covers')
    try:
        if path.parent != base or path.is_symlink() or not path.is_file(): return 1
        if path.resolve().parent != base.resolve(): return 1
        if path.suffix not in ('.jpg', '.png') or not 0 < path.stat().st_size <= MAX_FILE_BYTES: return 1
        return display(path, *libraries())
    except (OSError, ValueError, AttributeError):
        return 1  # Caller always proceeds to VICE; no display/terminal repair commands.


if __name__ == '__main__':
    raise SystemExit(main())
