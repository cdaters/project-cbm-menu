# Project CBM Public Image Release Workflow

This document explains how the private `project-cbm-menu` repository feeds the public `project-cbm` image release process.

## Repository Roles

```text
project-cbm
  Public repository.
  Contains public image releases, end-user documentation, checksums,
  release notes, screenshots, and the public roadmap.

project-cbm-menu
  Private repository.
  Contains menu source scripts, configuration examples, splash assets,
  build notes, audit notes, release-prep tooling, and menu bundle packaging.
```

## Version Model

```text
Project CBM public image version:  v1.0.0, v1.1.0, etc.
Project CBM menu source version:   v1.0.0, v1.0.1, v1.1.0, etc.
Legacy internal menu lineage:      formerly v6.5
```

The menu repo version does not have to match the public image version forever, but the first formal menu repo release is `v1.0.0` because it corresponds to the menu system included with the public Project CBM v1.0.0 image.

## Build the Menu Bundle

From this repo:

```bash
make clean
make bundle
```

Expected output:

```text
dist/Project-CBM-v1.0.0-Bundle.zip
```

This bundle contains the menu scripts, configs, covers, packaging helpers, and build documentation needed to reproduce or update the Project CBM menu system on the source Pi.

## Install or Update the Source Pi

Copy the bundle to the source Pi, extract it, and install the menu files according to the main build notes.

Core install pattern:

```bash
sudo cp scripts/pcbm-* /usr/local/bin/
sudo cp scripts/pcbm-dialog-lib.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/pcbm-*
sudo chmod +x /usr/local/bin/pcbm-dialog-lib.sh

sudo mkdir -p /etc/pcbm
sudo cp configs/version.conf /etc/pcbm/version.conf
sudo cp configs/default-machine.conf.example /etc/pcbm/default-machine.conf
sudo cp configs/boot-mode.conf.example /etc/pcbm/boot-mode.conf
```

Then validate menu behavior, VICE launches, audio, Samba, imports, splash screens, boot mode, and TCPser if installed.

## Final Source Pi Validation

Before imaging, verify:

```text
Project CBM menu starts on tty1
RUN launches the saved default machine
MACHINES launches supported emulator profiles
CONTENT scans nested folders
IMPORT handles folders and filters macOS junk
CONTROL -> AUDIO works
CONTROL -> NETWORK shows Samba status
CONTROL -> BBS controls TCPser if installed
CONTROL -> SYSTEM -> BOOTMODE works
Samba connects at smb://pcbm.local/Project%20CBM
Splash behavior works at menu entry, launch, and emulator return
```

Static checks:

```bash
bash -n /usr/local/bin/pcbm-*
bash -n /usr/local/bin/pcbm-dialog-lib.sh
/usr/local/bin/pcbm-audio status
systemctl is-active smbd || true
systemctl is-active avahi-daemon || true
```

## Prepare the Source Pi for Imaging

Only do this after the build is stable:

```bash
sudo pcbm-release-prep --yes --poweroff
```

Fast test mode:

```bash
sudo pcbm-release-prep --yes --no-zero-fill
```

## Image the SD Card on macOS

After the Pi powers off, remove the SD card and insert it into the Mac.

```bash
diskutil list
diskutil unmountDisk /dev/diskX
sudo dd if=/dev/rdiskX of=Project-CBM-v1.0.0-source.img bs=4m status=progress
sync
```

Use `rdisk` for speed. Be absolutely certain the disk number is correct.

## Shrink the Image with PiShrink

On Linux:

```bash
sudo pishrink.sh -a -z Project-CBM-v1.0.0-source.img Project-CBM-v1.0.0.img
```

Do not use `-s`, because that disables first-boot filesystem expansion.

## Generate Checksums

```bash
sha256sum Project-CBM-v1.0.0.img.gz > Project-CBM-v1.0.0.img.gz.sha256
```

## Test the Public Release Image

Flash the compressed image to a fresh SD card and verify:

```text
Filesystem expands on first boot
Project CBM menu appears
VICE launches
Audio works
Samba share works as Project CBM
pcbm.local resolves
Boot Mode works
TCPser works if installed
```

Check filesystem size:

```bash
df -h /
```

## Public Release Repo Layout

The public `project-cbm` release should contain or link to:

```text
Project-CBM-v1.0.0.img.gz
Project-CBM-v1.0.0.img.gz.sha256
README.md
docs/
release-notes/
```

The private `project-cbm-menu` release should attach:

```text
Project-CBM-v1.0.0-Bundle.zip
```

## Rule of Thumb

The public repo serves users.

The private repo serves the builder.
