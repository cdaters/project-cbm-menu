# Project CBM v6.5 Static Audit Notes

This audit was performed against the uploaded `proposed-pcbm-v6.5-bundle.zip`, using the uploaded v6.4 bundle/document as the packaging and documentation style reference.

## Static checks performed

- Extracted and compared the v6.4 and proposed v6.5 bundle layouts.
- Ran Bash syntax checks against every `scripts/pcbm-*` file.
- Removed macOS `.DS_Store` and live-machine dotfile artifacts from the clean bundle.
- Normalized config files back into examples where appropriate.
- Kept the v6.4 documentation pattern: purpose, changes, philosophy, boot model, folder layout, phases, validation, release engineering, bundle inventory, and appendices.

## Issues corrected in this deliverable

1. `pcbm-system` listed a RELEASE menu item but did not handle the `RELEASE)` case. The corrected script now invokes `sudo -n /usr/local/bin/pcbm-release-prep --yes` after confirmation.
2. `pcbm-network` still started/stopped both `smbd` and `nmbd`, which conflicted with the v6.5 SMB-only/NetBIOS-disabled model. The corrected script controls `smbd` only.
3. `pcbm-network` reported the share name as `pcbm`; it now reports `Project CBM` and shows the macOS `smb://pcbm.local/Project%20CBM` path.
4. `pcbm-release-prep` documentation referenced `--yes --poweroff`, but the script did not implement argument handling or poweroff. The corrected script supports `--yes`, `--poweroff`, and `--no-zero-fill`.
5. `pcbm-start` used `/etc/pcbm/.firstboot_done` as a marker even though the script runs as the `pi` user during autologin. The corrected marker path is `/home/pi/.config/pcbm/.firstboot_done`.
6. `pcbm-cover` had a duplicated shebang line in the proposed source. The clean bundle removes it.
7. The proposed bundle carried live-machine files such as `.profile`, `.asoundrc`, `.hushlogin`, `.firstboot_done`, and nested `.config` paths. The clean bundle turns these into explicit examples instead.
8. The proposed pre-Codex release workflow still contained stale v6.4 image names in a few places. The new documentation uses v6.5 menu-bundle names and Project CBM v1.0.0 image-version language.

## Items intentionally preserved

- The importer's folder-browse/import behavior and macOS metadata filtering.
- The menu-first boot model with optional direct-machine boot.
- The `pcbm-cover` framebuffer/fbi splash approach.
- TCPser service/menu integration.
- Experimental `pcbm-screenshot`, with documentation warning that it is not yet a polished public v1.0.0 feature.

## Scripts in clean v6.5 bundle

- `scripts/pcbm-audio`
- `scripts/pcbm-bbs`
- `scripts/pcbm-boot`
- `scripts/pcbm-bootmode`
- `scripts/pcbm-content`
- `scripts/pcbm-control`
- `scripts/pcbm-cover`
- `scripts/pcbm-dialog-lib.sh`
- `scripts/pcbm-firstboot-check`
- `scripts/pcbm-import`
- `scripts/pcbm-machines`
- `scripts/pcbm-menu`
- `scripts/pcbm-network`
- `scripts/pcbm-release-prep`
- `scripts/pcbm-roms`
- `scripts/pcbm-screenshot`
- `scripts/pcbm-start`
- `scripts/pcbm-system`

## Config examples in clean v6.5 bundle

- `configs/99-pcbm`
- `configs/audio.conf.example`
- `configs/boot-mode.conf.example`
- `configs/cmdline.txt.pcbm.appliance.example`
- `configs/config.txt.pcbm.example`
- `configs/default-machine.conf.example`
- `configs/hushlogin.example`
- `configs/pcbm-script-header.example`
- `configs/pcbm-sudoers.example`
- `configs/profile.pcbm.example`
- `configs/sdl-vicerc.example`
- `configs/smb.conf`
- `configs/tcpser.service.example`
- `configs/version.conf`
