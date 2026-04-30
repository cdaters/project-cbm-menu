# Changelog

## Project CBM Menu v1.0.0

Initial public source release of the Project CBM menu system.

This release formalizes the menu source that was developed internally as the `v6.5` menu bundle for the Project CBM image v1.0.0 release. Earlier `v6.4` and `v6.5` names are preserved only as historical development lineage.

### Notable changes from the earlier internal v6.4 reference bundle

- Established public Project CBM Menu v1.0.0 versioning to align with the Project CBM image v1.0.0 release.
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
- Normalized bundle file names and removed live-machine artifacts from the clean source release.
- Added experimental `pcbm-screenshot` helper, while keeping polished screenshot support on the public roadmap for v1.1.0 until capture behavior is proven across framebuffer/SDL2/KMS cases.
