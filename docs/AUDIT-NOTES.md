# Project CBM Menu v1.0.0 Static Audit Notes

This audit was performed against the pre-public Project CBM menu bundle that became the Project CBM Menu v1.0.0 source release.

During development, this internal working bundle was referred to as `v6.5`. For the public repository and release documentation, this work is now tracked as:

```text
Project CBM image: v1.0.0
Project CBM menu:  v1.0.0
```

The earlier v6.4 bundle/document was used only as a packaging and documentation style reference.

## Static checks performed

- Extracted and compared the earlier v6.4 reference bundle layout against the pre-public menu source bundle.
- Ran Bash syntax checks against every `scripts/pcbm-*` file.
- Removed macOS `.DS_Store` files and live-machine dotfile artifacts from the clean source bundle.
- Normalized configuration files back into examples where appropriate.
- Preserved the established documentation pattern: purpose, changes, philosophy, boot model, folder layout, phases, validation, release engineering, bundle inventory, and appendices.
- Aligned public-facing version language with Project CBM image v1.0.0 and Project CBM Menu v1.0.0.

## Issues corrected in this source release

1. `pcbm-system` listed a RELEASE menu item but did not handle the `RELEASE)` case. The corrected script now invokes `sudo -n /usr/local/bin/pcbm-release-prep --yes` after confirmation.
2. `pcbm-network` still started/stopped both `smbd` and `nmbd`, which conflicted with the SMB-only/NetBIOS-disabled model. The corrected script controls `smbd` only.
3. `pcbm-network` reported the share name as `pcbm`; it now reports `Project CBM` and shows the macOS `smb://pcbm.local/Project%20CBM` path.
4. `pcbm-release-prep` documentation referenced `--yes --poweroff`, but the script did not implement argument handling or poweroff. The corrected script supports `--yes`, `--poweroff`, and `--no-zero-fill`.
5. `pcbm-start` used `/etc/pcbm/.firstboot_done` as a marker even though the script runs as the `pi` user during autologin. The corrected marker path is `/home/pi/.config/pcbm/.firstboot_done`.
6. `pcbm-cover` had a duplicated shebang line in the proposed source. The clean source release removes it.
7. The pre-public bundle carried live-machine files such as `.profile`, `.asoundrc`, `.hushlogin`, `.firstboot_done`, and nested `.config` paths. The clean source release turns these into explicit examples instead.
8. The pre-public release workflow still contained older internal version names in a few places. The documentation now uses Project CBM Menu v1.0.0 source-release language and Project CBM image v1.0.0 public-release language.

## Items intentionally preserved

- The importer's folder-browse/import behavior and macOS metadata filtering.
- The menu-first boot model with optional direct-machine boot.
- The `pcbm-cover` framebuffer/fbi splash approach.
- TCPser service/menu integration.
- Experimental `pcbm-screenshot`, with documentation warning that it is not yet a polished public v1.0.0 feature.

## Scripts in Project CBM Menu v1.0.0 source

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

## Config examples in Project CBM Menu v1.0.0 source

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
