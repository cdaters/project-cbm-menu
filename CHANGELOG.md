# Changelog

## Project CBM Menu v6.5

Changes from v6.4:
- Added menu-version separation: public Project CBM image v1.0.0 can ship with Project CBM Menu v6.5.
- Added machine-family splash system and family cover naming.
- Added `pcbm_emu_to_cover_tag()` for emulator-to-cover-family mapping.
- Added splash session guard to prevent startup double-splashing.
- Fixed importer recursive folder copy behavior.
- Fixed importer folder selection behavior: SPACE selects, ENTER/OK proceeds.
- Hardened macOS import junk filtering (`._*`, `.DS_Store`, `.Trashes`, `__MACOSX`, and related folders/files).
- Standardized Samba as SMB-only on TCP 445 with NetBIOS disabled.
- Updated network menu to control `smbd` only instead of requiring `nmbd`.
- Preserved `.local` access through Avahi daemon without requiring a custom Avahi Samba service file.
- Fixed Project CBM System menu RELEASE item so it actually calls `pcbm-release-prep`.
- Updated `pcbm-release-prep` to support `--yes`, `--poweroff`, and `--no-zero-fill`.
- Moved first-boot marker to `/home/pi/.config/pcbm/.firstboot_done` so the `pi` user can write it.
- Normalized bundle file names and removed live-machine artifacts from the clean release bundle.
- Added experimental `pcbm-screenshot` helper, but kept screenshot support on the public roadmap for v1.1.0 until capture behavior is proven across framebuffer/SDL2/KMS cases.
