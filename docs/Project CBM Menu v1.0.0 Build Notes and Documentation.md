# Project CBM v6.5 Build Notes and Documentation

## Purpose

Project CBM v6.5 is the menu-system and build-diary reference for the Project CBM v1.0.0 public Raspberry Pi image.

It follows the v6.4 documentation style: build philosophy first, then repeatable phases, then folder/config/script inventories, then appendices with source listings.

The image currently published as Project CBM v1.0.0 can remain v1.0.0 while this private menu system repository tracks the menu as v6.5. That separation is intentional.

```text
Project CBM public image/build version: 1.0.0
Project CBM menu system version:       6.5
```

v6.5 rolls forward the v6.4 foundation and formally adds:

- Machine-family splash routing: C64, C128, VIC-20, PET, Plus/4, CBM-II, and CBM 5x0 families.
- `pcbm_emu_to_cover_tag()` for emulator-to-cover-family mapping.
- Splash session guard through `PCBM_SPLASH_SHOWN` to prevent double-splashing at menu startup.
- USB importer folder-selection and recursive-copy fixes.
- Hardened macOS junk filtering during imports.
- Samba cleanup for SMB-only operation on port 445 with NetBIOS disabled.
- Stable `.local` hostname access through `pcbm.local`.
- Menu/image version separation through `PCBM_MENU_VERSION`.
- Corrected release-prep menu handling.
- TCPser integration retained.
- Experimental screenshot helper retained for future v1.1.0 work.

The design goal remains simple: Project CBM should feel like a dedicated Commodore appliance, not like a Linux desktop wearing a plastic breadbin mask.

---

## What Changed from v6.4

- Added `PCBM_MENU_VERSION="6.5"` while keeping `PCBM_VERSION="1.0.0"` for the public image.
- Added machine-family cover naming and normalized emulator-to-cover routing.
- Added generic splash-on-menu-entry and machine-family splash-on-launch behavior.
- Added fallback random cover handling when a machine-family cover is missing.
- Fixed importer behavior for recursive folder imports.
- Hardened import filtering for `.DS_Store`, `._*`, `.Trashes`, `.Spotlight-V100`, `.fseventsd`, `__MACOSX`, `Thumbs.db`, and `desktop.ini`.
- Updated Samba to an SMB-only model: `disable netbios = yes` and `smb ports = 445`.
- Removed the requirement for `nmbd` from the Project CBM network menu.
- Kept Avahi daemon for `.local` hostname resolution, but does not require a custom Avahi `_smb._tcp` service file.
- Fixed the System menu's `RELEASE` item.
- Expanded `pcbm-release-prep` so the documented `--yes --poweroff` path works.
- Moved the first-boot marker into the `pi` user's config path.
- Added `pcbm-screenshot` as an experimental helper while leaving screenshot capture on the public v1.1.0 roadmap.
- Cleaned the bundle shape so it again resembles the v6.4 package structure.

---

## Design Philosophy

Project CBM is meant to feel like a dedicated Commodore appliance powered by Raspberry Pi OS Lite and VICE.

The design priorities are:

1. Boot fast and land somewhere friendly.
2. Hide as much Linux noise as practical.
3. Keep the Project CBM menu as the normal front panel.
4. Allow optional direct-machine startup for kiosk/living-room builds.
5. Keep common actions inside a text UI.
6. Let content be organized sanely without fighting the launcher.
7. Expose file transfer over Samba so the box is easy to feed.
8. Keep `.local` access simple for macOS/Linux users.
9. Auto-handle common Pi hardware weirdness, especially dual-HDMI audio.
10. Clearly identify the project, author, version, license, credits, and warranty/distribution limits.
11. Treat TCPser as optional but properly integrated.
12. Keep experimental features visible in the private repo but conservative in the public release.
13. Provide a repeatable release workflow suitable for public image distribution.

---

## Versioning Model

Do not make the public image version and menu version chase each other like two cats tied to the same string.

Use this model:

```text
PCBM_VERSION      = public image/build version
PCBM_MENU_VERSION = menu system version
PCBM_BUILD        = build date or build identifier
```

Current v6.5 baseline:

```bash
PCBM_VERSION="1.0.0"
PCBM_MENU_VERSION="6.5"
PCBM_BUILD="2026.04.29"
```

Recommended release naming:

```text
Project CBM v1.0.0 image
Project CBM Menu v6.5
```

Future example:

```text
Project CBM v1.1.0 image
Project CBM Menu v6.6 or v7.0
```

This lets you revise the menu/build machinery privately without implying that every internal menu iteration is a new public SD-card image release.

---

## Boot Behavior Model

Project CBM separates two ideas that should stay separate:

```text
Default Machine = the emulator profile launched by RUN
Boot Mode       = what Project CBM does when tty1 auto-login starts
```

Valid boot modes:

```text
menu    -> boot to Project CBM main menu
machine -> boot directly into the saved default machine, then return to menu when VICE exits
```

Recommended default:

```text
menu
```

The menu is Project CBM's front panel. Direct-machine boot is an advanced option for users who want a power-on-and-go C64/C128/VIC-20 style appliance.

---

## Recommended Project CBM Layout

The top-level content root stays:

```text
/home/pi/pcbm
```

Recommended structure:

```text
/home/pi/pcbm/
├── games/
│   ├── c64/
│   ├── c128/
│   ├── vic20/
│   ├── plus4/
│   ├── pet/
│   ├── cbm2/
│   ├── cbm5x0/
│   └── shared/
├── demos/
│   ├── c64/
│   ├── c128/
│   │   ├── 40col/
│   │   └── 80col-vdc/
│   └── shared/
├── music/
│   ├── c64/
│   ├── c128/
│   └── shared/
├── programs/
│   ├── c64/
│   ├── c128/
│   ├── vic20/
│   ├── plus4/
│   ├── pet/
│   └── shared/
└── roms/
```

The content browser scans recursively, so machine-specific subfolders are fine.

---

## Build Overview

The cleanest build order is:

1. Flash Raspberry Pi OS Lite.
2. First boot, update, and basic localization.
3. Install the minimal package set required by Project CBM.
4. Create Project CBM version metadata and login banner.
5. Configure audio baseline and HDMI auto-detection.
6. Build and verify VICE manually.
7. Create the Project CBM directory structure.
8. Install the Project CBM scripts and configs.
9. Configure Samba and Avahi hostname resolution.
10. Configure splash screens.
11. Configure console autologin and Project CBM startup dispatcher.
12. Configure appliance boot polish.
13. Build and integrate TCPser.
14. Validate menu boot, direct-machine boot, networking, audio, imports, splash, and TCPser.
15. Prepare the image for release.
16. Commit the clean menu system to the private `project-cbm-menu` repository.

---

# Phase 1 - Base Raspberry Pi OS Lite Setup

## 1. Start with Raspberry Pi OS Lite 64-bit

Use Raspberry Pi OS Lite 64-bit.

The current work is Pi 5 / Pi 500 focused, but the layout should still be sensible for Pi 4 / 400, Pi 3, Pi Zero 2, and Pi Zero 2 W as long as the selected Raspberry Pi OS image, kernel, firmware, SDL, framebuffer behavior, and VICE build cooperate.

## 2. Raspberry Pi Imager settings

Recommended:

- Hostname: `pcbm`
- Username: `pi`
- Password: your choice
- Locale / timezone: user preference
- SSH: enabled
- Wi-Fi: optional

## 3. First boot

```bash
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

After reboot:

```bash
sudo apt autoremove -y
sudo apt clean
```

---

# Phase 2 - Core Packages

Install:

```bash
sudo apt install -y \
  build-essential \
  dialog \
  alsa-utils \
  libsdl2-2.0-0 \
  libsdl2-image-2.0-0 \
  libasound2 \
  libegl1 \
  libgles2 \
  libgl1-mesa-dri \
  libpulse0 \
  unzip \
  mc \
  rsync \
  pkg-config \
  autoconf automake libtool \
  libpng-dev libjpeg-dev libtiff-dev \
  libsdl2-dev libsdl2-image-dev \
  libgtk-3-dev libcurl4-openssl-dev \
  git \
  flex bison \
  xa65 \
  fbi \
  fbset \
  imagemagick \
  samba samba-common-bin \
  avahi-daemon \
  userconf-pi
```

Optional experimental screenshot packages:

```bash
sudo apt install -y fbgrab ffmpeg
```

Do not promote screenshot capture as a polished public feature until `pcbm-screenshot` is tested across the menu framebuffer and VICE SDL2/KMS cases.

Lock runtime pieces you know you want to keep:

```bash
sudo apt-mark manual \
  libsdl2-2.0-0 \
  libsdl2-image-2.0-0 \
  libasound2 \
  libegl1 \
  libgles2 \
  libgl1-mesa-dri \
  libpulse0 \
  dialog \
  alsa-utils \
  mc \
  rsync \
  fbi \
  fbset \
  imagemagick \
  avahi-daemon
```

---

# Phase 3 - Project Identity, Versioning, and Login Banner

## 1. Create `/etc/pcbm`

```bash
sudo mkdir -p /etc/pcbm
```

## 2. Install the central version file

Copy from the bundle:

```bash
sudo cp configs/version.conf /etc/pcbm/version.conf
sudo chmod 644 /etc/pcbm/version.conf
```

Example contents:

```bash
PCBM_PROJECT_NAME="Project CBM"
PCBM_INTERNAL_NAME="pcbm"
PCBM_VERSION="1.0.0"
PCBM_MENU_VERSION="6.5"
PCBM_BUILD="2026.04.29"
PCBM_AUTHOR="Craig Daters"
PCBM_REPO="https://github.com/cdaters/project-cbm"
PCBM_MENU_REPO="https://github.com/cdaters/project-cbm-menu"
PCBM_TAGLINE="Power on. Boot fast. No nonsense. Just Commodore."
```

## 3. Add Project CBM to login/MOTD without replacing Debian's message

Copy the included script:

```bash
sudo cp configs/99-pcbm /etc/update-motd.d/99-pcbm
sudo chmod +x /etc/update-motd.d/99-pcbm
```

Test it directly:

```bash
/etc/update-motd.d/99-pcbm
```

This appends a Project CBM block showing image version, menu version, build information, and the no-ROM/distribution disclaimer.

---

# Phase 4 - Audio Baseline and HDMI Auto-Detection

Do this before VICE. It saves a whole lot of ghost-hunting later.

## 1. Basic audio tests

```bash
aplay -l
speaker-test -D plug:default -c 2 -twav
speaker-test -D plughw:0,0 -c 2 -twav
speaker-test -D plughw:1,0 -c 2 -twav
```

## 2. Project CBM audio helper

After installing scripts:

```bash
/usr/local/bin/pcbm-audio set-auto
/usr/local/bin/pcbm-audio status
/usr/local/bin/pcbm-audio test
```

Menu path:

```text
CONTROL -> AUDIO
```

`pcbm-audio` writes `/home/pi/.asoundrc` using ALSA `type plug` so VICE/SDL audio can be converted to the HDMI device's supported format.

---

# Phase 5 - Build and Verify VICE

## 1. Download and unpack

```bash
cd ~
wget https://sourceforge.net/projects/vice-emu/files/releases/vice-3.10.tar.gz
tar -xvf vice-3.10.tar.gz
cd vice-3.10
```

## 2. Configure

```bash
./configure \
  --enable-sdl2ui \
  --disable-gtk3ui \
  --disable-pdf-docs \
  --enable-x64 \
  --without-pulse
```

## 3. Build and install

```bash
make -j"$(nproc)"
sudo make install
```

## 4. Verify

```bash
which x64sc
ldd "$(command -v x64sc)" | grep 'not found' || echo "No missing libs"
```

## 5. Known-good launch test

```bash
SDL_AUDIODRIVER=alsa x64sc -sounddev sdl
```

That command is the north star. Project CBM stays close to it.

---

# Phase 6 - Create the Project CBM Content Layout

```bash
mkdir -p /home/pi/pcbm/{games,demos,music,programs,roms}
mkdir -p \
  /home/pi/pcbm/games/{c64,c128,vic20,plus4,pet,cbm2,cbm5x0,shared} \
  /home/pi/pcbm/demos/{c64,shared} \
  /home/pi/pcbm/demos/c128/{40col,80col-vdc} \
  /home/pi/pcbm/music/{c64,c128,shared} \
  /home/pi/pcbm/programs/{c64,c128,vic20,plus4,pet,shared}
sudo chown -R pi:pi /home/pi/pcbm
```

---

# Phase 7 - Install the Project CBM Scripts and Configs

From the clean v6.5 bundle:

```bash
sudo cp scripts/pcbm-* /usr/local/bin/
sudo cp scripts/pcbm-dialog-lib.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/pcbm-*
sudo chmod +x /usr/local/bin/pcbm-dialog-lib.sh
```

Create config directory and install defaults:

```bash
sudo mkdir -p /etc/pcbm
sudo cp configs/version.conf /etc/pcbm/version.conf
sudo cp configs/default-machine.conf.example /etc/pcbm/default-machine.conf
sudo cp configs/boot-mode.conf.example /etc/pcbm/boot-mode.conf
```

Initialize audio:

```bash
/usr/local/bin/pcbm-audio set-auto
```

---

# Phase 8 - Limited Sudo Policy

```bash
sudo cp configs/pcbm-sudoers.example /etc/sudoers.d/pcbm
sudo chmod 440 /etc/sudoers.d/pcbm
sudo visudo -cf /etc/sudoers.d/pcbm
```

If `visudo` reports a syntax problem, stop and fix it before continuing.

---

# Phase 9 - Samba and Avahi Hostname Integration

Recommended naming model:

```text
Hostname:       pcbm
NetBIOS name:   PROJECT-CBM, retained only as a Samba identity string
Server string:  Project CBM
Share name:     Project CBM
mDNS name:      pcbm.local
```

v6.5 uses SMB-only operation:

```text
disable netbios = yes
smb ports = 445
```

## 1. Install Samba config

```bash
sudo cp configs/smb.conf /etc/samba/smb.conf
sudo smbpasswd -a pi
testparm
sudo systemctl enable smbd
sudo systemctl restart smbd
```

Do not require `nmbd` for v6.5. NetBIOS browsing is intentionally disabled to avoid duplicate or stale discovery behavior.

## 2. Enable Avahi daemon for `.local` hostname resolution

```bash
sudo systemctl enable avahi-daemon
sudo systemctl restart avahi-daemon
```

Do not install a custom `/etc/avahi/services/samba.service` file by default in v6.5. The reliable connection path is direct SMB over the mDNS hostname:

```text
smb://pcbm.local/Project%20CBM
```

Windows direct UNC path:

```text
\\pcbm\Project CBM
```

If Windows name resolution is stubborn, use the Pi's IP address:

```text
\\<Pi-IP-address>\Project CBM
```

---

# Phase 10 - Splash Screen System

```bash
sudo mkdir -p /opt/pcbm/covers
sudo chown -R pi:pi /opt/pcbm
cp covers/* /opt/pcbm/covers/
```

Splash architecture:

- Boot/menu entry: random Project CBM cover.
- Machine launch: machine-family cover.
- Exit emulator: random Project CBM cover.
- Missing machine-family cover: fallback to random generic cover.
- Startup double-splash prevention: `PCBM_SPLASH_SHOWN` session guard.

Generic random cover names:

```text
pcbmcover0.jpg
pcbmcover1.jpg
pcbmcover2.jpg
```

Machine-family cover names:

```text
pcbmcover-c64.jpg
pcbmcover-c128.jpg
pcbmcover-vic20.jpg
pcbmcover-pet.jpg
pcbmcover-plus4.jpg
pcbmcover-cbm2.jpg
pcbmcover-cbm5.jpg
```

Cover mapping:

```text
x64, x64sc, xscpu64, x64dtv -> c64
x128, x128-80col             -> c128
xvic                         -> vic20
xpet                         -> pet
xplus4                       -> plus4
xcbm2                        -> cbm2
xcbm5x0                      -> cbm5
```

---

# Phase 11 - Boot Integration and Boot Mode

Enable console autologin:

```bash
sudo raspi-config
```

Path:

```text
System Options -> Boot / Auto Login -> Console Autologin
```

Append to `/home/pi/.profile`:

```bash
if [ "$(tty)" = "/dev/tty1" ]; then
    clear
    /usr/local/bin/pcbm-start
fi
```

Boot mode config:

```text
/etc/pcbm/boot-mode.conf
```

Recommended:

```bash
echo "menu" | sudo tee /etc/pcbm/boot-mode.conf
```

Direct-machine mode:

```bash
echo "machine" | sudo tee /etc/pcbm/boot-mode.conf
```

Menu path:

```text
CONTROL -> SYSTEM -> BOOTMODE
```

---

# Phase 12 - Appliance Boot Polish

Project CBM lives on `tty1`, so the appliance boot line should keep the visible console there.

## 1. Backup current cmdline

```bash
sudo cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.bak
```

## 2. Find root PARTUUID

```bash
sudo blkid /dev/mmcblk0p2
```

Example:

```text
/dev/mmcblk0p2: LABEL="rootfs" UUID="..." TYPE="ext4" PARTUUID="45240a73-02"
```

## 3. Edit cmdline.txt

```bash
sudo nano /boot/firmware/cmdline.txt
```

Use one single line:

```text
console=serial0,115200 console=tty1 root=PARTUUID=<your-root-partuuid> rootfstype=ext4 fsck.repair=yes rootwait quiet loglevel=0 systemd.show_status=false rd.udev.log_level=0 logo.nologo vt.global_cursor_default=0
```

Do not copy a live Pi's `PARTUUID` into the docs. Keep the placeholder in the example and use the value from the target image.

## 4. config.txt polish

Add to `/boot/firmware/config.txt`:

```text
disable_splash=1
# avoid_warnings=1
```

`avoid_warnings=1` is optional. It hides warnings that may be useful during troubleshooting.

---

# Phase 13 - TCPser Build and Integration

TCPser remains optional but integrated.

## 1. Build TCPser

```bash
cd ~
git clone https://github.com/go4retro/tcpser.git
cd tcpser
make
sudo install -m 755 tcpser /usr/local/bin/tcpser
```

## 2. Install service

```bash
sudo cp configs/tcpser.service.example /etc/systemd/system/tcpser.service
sudo systemctl daemon-reload
sudo systemctl enable tcpser
```

Start/stop from the menu:

```text
CONTROL -> BBS
```

Or manually:

```bash
sudo systemctl start tcpser
sudo systemctl status tcpser --no-pager
```

---

# Phase 14 - Validation Checklist

Run this before imaging.

```text
Project CBM menu starts on tty1
RUN launches the saved default machine
MACHINES launches each supported machine profile
MACHINES -> DEFAULT saves /etc/pcbm/default-machine.conf
CONTENT scans nested folders recursively
IMPORT can browse folders, import a folder recursively, and filter macOS junk
CONTROL -> NETWORK shows host, IP, gateway, DNS, and Samba status
CONTROL -> AUDIO can auto-detect HDMI and run speaker test
CONTROL -> BBS can start/stop/restart TCPser if installed
CONTROL -> ROMS imports ROM files without treating top-level folders as ROMs
CONTROL -> SYSTEM -> BOOTMODE can switch menu/machine mode
CONTROL -> SYSTEM -> RELEASE calls release prep
Samba share connects at smb://pcbm.local/Project%20CBM
Splash shows at menu entry, machine launch, and return from emulator
```

Static sanity checks:

```bash
bash -n /usr/local/bin/pcbm-*
bash -n /usr/local/bin/pcbm-dialog-lib.sh
/usr/local/bin/pcbm-audio status
systemctl is-active smbd || true
systemctl is-active avahi-daemon || true
```

---

# Phase 15 - Release Engineering and Image Prep

Do this only after the build is stable.

## 1. Finalize source Pi

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y
sudo apt clean
```

Run final validation:

```bash
/usr/local/bin/pcbm-audio status
/usr/local/bin/pcbm-menu
```

## 2. Run release prep

```bash
sudo pcbm-release-prep --yes --poweroff
```

This cleans caches, logs, shell history, runtime files, first-boot markers, zero-fills free space, syncs, and powers off.

Optional fast mode while testing:

```bash
sudo pcbm-release-prep --yes --no-zero-fill
```

## 3. Image the SD card on macOS

```bash
diskutil list
diskutil unmountDisk /dev/diskX
sudo dd if=/dev/rdiskX of=Project-CBM-v1.0.0-menu-v6.5-source.img bs=4m status=progress
sync
```

Use `rdisk` for speed. Be absolutely certain you picked the right disk.

## 4. Shrink with PiShrink

On Linux:

```bash
sudo apt update
sudo apt install -y wget parted gzip pigz xz-utils udev e2fsprogs
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh
sudo mv pishrink.sh /usr/local/bin
sudo pishrink.sh -a -z Project-CBM-v1.0.0-menu-v6.5-source.img Project-CBM-v1.0.0.img
```

Do not use `-s`, because that disables first-boot filesystem expansion.

## 5. Generate checksum

```bash
sha256sum Project-CBM-v1.0.0.img.gz > Project-CBM-v1.0.0.img.gz.sha256
```

## 6. Test release image

Before sharing it, flash the compressed image to a fresh SD card and verify:

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

## 7. Release folder layout

```text
Project-CBM-v1.0.0-release/
├── Project-CBM-v1.0.0.img.gz
├── Project-CBM-v1.0.0.img.gz.sha256
├── README.md
├── docs/
│   ├── README.md
│   ├── QUICK-START.md
│   └── CHECKSUMS-AND-VERIFICATION.md
└── release-notes/
    └── v1.0.0.md
```

The private menu repo produces this companion artifact:

```text
Project-CBM-v6.5-Bundle.zip
```

---

# Phase 16 - Private Menu Repository Model

Recommended private repository:

```text
https://github.com/cdaters/project-cbm-menu
```

Recommended purpose:

```text
Private build notes, menu source, configuration examples, cover assets, and packaging tools for Project CBM's menu system.
```

Keep this private repo separate from the public image/end-user repo:

```text
project-cbm       -> public image releases, public docs, checksums, user-facing roadmap
project-cbm-menu  -> private menu scripts, build diary, source bundles, internal release tooling
```

Recommended repo layout:

```text
project-cbm-menu/
├── README.md
├── LICENSE
├── VERSION
├── CHANGELOG.md
├── ROADMAP.md
├── configs/
├── covers/
├── docs/
│   ├── Project CBM v6.5 Build Notes and Documentation.md
│   ├── AUDIT-NOTES.md
│   └── VERSIONING.md
├── packaging/
│   ├── build-menu-bundle.sh
│   └── install-menu-bundle.sh
├── scripts/
├── .github/
│   └── workflows/
│       └── build-menu-bundle.yml
├── .gitattributes
├── .gitignore
└── Makefile
```

Build the bundle locally:

```bash
make bundle
```

Or directly:

```bash
./packaging/build-menu-bundle.sh
```

---

# Bundle Inventory

## Scripts

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

## Configs

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

## Covers

- `covers/pcbmcover-c128.jpg`
- `covers/pcbmcover-c64.jpg`
- `covers/pcbmcover-cbm2.jpg`
- `covers/pcbmcover-cbm5.jpg`
- `covers/pcbmcover-pet.jpg`
- `covers/pcbmcover-plus4.jpg`
- `covers/pcbmcover-vic20.jpg`
- `covers/pcbmcover0.jpg`
- `covers/pcbmcover1.jpg`

---

# README-FIRST.txt Suggested Content

```text
Project CBM v6.5 Menu Bundle
=============================

This bundle contains the Project CBM v6.5 menu system, helper scripts, and configuration examples used to produce the Project CBM v1.0.0 public Raspberry Pi image.

Start with:

1. Project CBM v6.5 Build Notes and Documentation.md
2. configs/version.conf
3. configs/cmdline.txt.pcbm.appliance.example
4. scripts/pcbm-release-prep
5. scripts/pcbm-firstboot-check

Important version note:
- Project CBM image/build version: 1.0.0
- Project CBM menu system version: 6.5

v6.5 adds machine-family splash routing, improved USB importer behavior, SMB-only Samba cleanup, menu/image version separation, and a more complete release-prep path.

Important:
- Project CBM does not include or distribute copyrighted Commodore ROMs, commercial software, disk images, demos, games, or other protected content.
- Users are responsible for supplying their own legally obtained content.
- Keep PCBM_REPO pointed at the public image/docs repo and PCBM_MENU_REPO pointed at the private menu repo.
```

---

# Revision Notes

```text
Project CBM v6.5 Revision Notes
===============================

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
```

---

# Appendix A - Audit Notes

```text
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
```

---

# Appendix B - Config Source Reference

## configs/99-pcbm

```bash
#!/bin/sh

# Project CBM dynamic MOTD add-on.
# Debian/Raspberry Pi OS will continue to show its normal login text.
# This script only appends Project CBM build information below it.

if [ -f /etc/pcbm/version.conf ]; then
    # shellcheck disable=SC1091
    . /etc/pcbm/version.conf
else
    PCBM_PROJECT_NAME="Project CBM"
    PCBM_VERSION="dev"
    PCBM_MENU_VERSION="dev"
    PCBM_BUILD="local"
    PCBM_TAGLINE="Raspberry Pi Commodore System"
fi

cat <<EOF

========================================
 $PCBM_PROJECT_NAME
 Raspberry Pi Commodore System

 Image Version: $PCBM_VERSION
 Menu Version:  ${PCBM_MENU_VERSION:-unknown}
 Build:         $PCBM_BUILD

 ${PCBM_TAGLINE:-Powered by Raspberry Pi OS and VICE.}
 Powered by Raspberry Pi OS and VICE.

 No ROMs, games, disk images, demos, or
 commercial software are included with
 this build.
========================================
EOF
```

## configs/audio.conf.example

```bash
MODE=auto
CARD=0
DEVICE=0
```

## configs/boot-mode.conf.example

```bash
menu
```

## configs/cmdline.txt.pcbm.appliance.example

```bash
console=serial0,115200 console=tty1 root=PARTUUID=<your-root-partuuid> rootfstype=ext4 fsck.repair=yes rootwait quiet loglevel=0 systemd.show_status=false rd.udev.log_level=0 logo.nologo vt.global_cursor_default=0
```

## configs/config.txt.pcbm.example

```bash
# Project CBM boot polish additions for /boot/firmware/config.txt
# Keep the stock Raspberry Pi OS file and add only the lines you need.

disable_splash=1

# Optional: hides low-voltage and similar warning icons from the display.
# Leave commented while troubleshooting hardware/power problems.
# avoid_warnings=1
```

## configs/default-machine.conf.example

```bash
x64sc
```

## configs/hushlogin.example

```bash
# Copy to /home/pi/.hushlogin if you want to suppress normal login MOTD for appliance images.
```

## configs/pcbm-script-header.example

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: <script-name>
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, demos, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
```

## configs/pcbm-sudoers.example

```bash
# Example sudoers fragment for Project CBM
# Save as: /etc/sudoers.d/pcbm
# Edit with: sudo visudo -f /etc/sudoers.d/pcbm
# Verify command paths on your Pi with:
# command -v mount umount mkdir rm systemctl raspi-config tee poweroff reboot

pi ALL=(root) NOPASSWD:   /usr/sbin/poweroff,   /usr/sbin/reboot,   /usr/bin/raspi-config,   /usr/local/bin/pcbm-release-prep,   /usr/bin/systemctl start tcpser,   /usr/bin/systemctl stop tcpser,   /usr/bin/systemctl restart tcpser,   /usr/bin/systemctl status tcpser,   /usr/bin/systemctl is-active tcpser,   /usr/bin/systemctl start smbd,   /usr/bin/systemctl stop smbd,   /usr/bin/systemctl restart smbd,   /usr/bin/systemctl is-active smbd,   /usr/bin/systemctl restart avahi-daemon,   /usr/bin/systemctl is-active avahi-daemon,   /usr/bin/systemctl restart dhcpcd,   /usr/bin/systemctl is-active dhcpcd,   /usr/bin/systemctl restart NetworkManager,   /usr/bin/systemctl is-active NetworkManager,   /usr/bin/mount,   /usr/bin/umount,   /usr/bin/tee,   /usr/bin/mkdir,   /usr/bin/rm
```

## configs/profile.pcbm.example

```bash
# Append to /home/pi/.profile
# Project CBM starts only on the local auto-login console.
# SSH sessions remain normal.
if [ "$(tty)" = "/dev/tty1" ]; then
    clear
    /usr/local/bin/pcbm-start
fi
```

## configs/sdl-vicerc.example

```bash
[Version]
ConfigVersion=3.10

[C64]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=720
Window0Height=576
Window0Xpos=-40
Window0Ypos=-48
VICIIGLFilter=1

[C64SC]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=720
Window0Height=576
Window0Xpos=-40
Window0Ypos=-48
VICIIGLFilter=1

[SCPU64]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=720
Window0Height=576
Window0Xpos=-40
Window0Ypos=-48
VICIIGLFilter=1

[C64DTV]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=720
Window0Height=576
Window0Xpos=-40
Window0Ypos=-48
VICIIGLFilter=1

[C128]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=800
Window0Height=600
Window0Xpos=-80
Window0Ypos=-60
VICIIGLFilter=1
VDCGLFilter=1

[CBM-II]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=720
Window0Height=576
Window0Xpos=-40
Window0Ypos=-48
CrtcGLFilter=1

[CBM-II-5x0]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=720
Window0Height=576
Window0Xpos=-40
Window0Ypos=-48
VICIIGLFilter=1

[VIC20]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=800
Window0Height=600
Window0Xpos=-80
Window0Ypos=-60
VICGLFilter=1

[PLUS4]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=800
Window0Height=600
Window0Xpos=-80
Window0Ypos=-60
TEDGLFilter=1

[PET]
MenuKey=291
SoundDeviceName="sdl"
Window0Width=720
Window0Height=576
Window0Xpos=-40
Window0Ypos=-48
CrtcGLFilter=1
```

## configs/smb.conf

```bash
[global]
   workgroup = WORKGROUP
   log file = /var/log/samba/log.%m
   max log size = 1000
   logging = file
   panic action = /usr/share/samba/panic-action %d
   server role = standalone server
   obey pam restrictions = yes
   unix password sync = yes
   passwd program = /usr/bin/passwd %u
   passwd chat = *Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .
   pam password change = yes
   map to guest = never
   usershare allow guests = yes
   netbios name = PROJECT-CBM
   disable netbios = yes
   smb ports = 445
   server string = Project CBM

[Project CBM]
   comment = Project CBM Folders
   path = /home/pi/pcbm
   browseable = yes
   read only = no
   guest ok = no
   valid users = pi
   force user = pi
   create mask = 0664
   directory mask = 0775
```

## configs/tcpser.service.example

```bash
[Unit]
Description=Project CBM TCPser modem bridge
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi
# Edit ExecStart for your final serial/pty strategy.
# Example placeholder for a listen-only modem bridge:
ExecStart=/usr/local/bin/tcpser -s 2400 -l 7 -p 0 -v 6400
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## configs/version.conf

```bash
PCBM_PROJECT_NAME="Project CBM"
PCBM_INTERNAL_NAME="pcbm"
PCBM_VERSION="1.0.0"
PCBM_MENU_VERSION="6.5"
PCBM_BUILD="2026.04.29"
PCBM_AUTHOR="Craig Daters"
PCBM_REPO="https://github.com/cdaters/project-cbm"
PCBM_MENU_REPO="https://github.com/cdaters/project-cbm-menu"
PCBM_TAGLINE="Power on. Boot fast. No nonsense. Just Commodore."
```

---

# Appendix C - Script Source Reference

## scripts/pcbm-audio

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-audio
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
# Project CBM audio helper
# Handles HDMI/ALSA detection, ~/.asoundrc generation, manual HDMI selection,
# and user-facing audio tests from the Project CBM dialog menu.

set -u

PCBM_VERSION_CONF="/etc/pcbm/version.conf"

if [[ -f "$PCBM_VERSION_CONF" ]]; then
  # shellcheck source=/etc/pcbm/version.conf
  source "$PCBM_VERSION_CONF"
else
  PCBM_PROJECT_NAME="Project CBM"
  PCBM_INTERNAL_NAME="pcbm"
  PCBM_VERSION="dev"
  PCBM_BUILD="local"
  PCBM_AUTHOR="Craig Daters"
  PCBM_REPO="https://github.com/<your-username>/project-cbm"
  PCBM_TAGLINE="Power on. Boot fast. No nonsense. Just Commodore."
fi

PCBM_AUDIO_CONF="${PCBM_AUDIO_CONF:-/home/pi/.config/pcbm/audio.conf}"
PCBM_ASOUNDRC="${PCBM_ASOUNDRC:-/home/pi/.asoundrc}"
PCBM_AUDIO_LOG="${PCBM_AUDIO_LOG:-/tmp/pcbm-audio.log}"
PCBM_DIALOG_LIB="/usr/local/bin/pcbm-dialog-lib.sh"

QUIET=0
COMMAND="${1:-menu}"
shift || true

for arg in "$@"; do
  case "$arg" in
    --quiet|-q) QUIET=1 ;;
  esac
done

log() {
  printf '%s\n' "$*" >>"$PCBM_AUDIO_LOG"
  if (( QUIET == 0 )); then
    printf '%s\n' "$*"
  fi
}

ensure_audio_dirs() {
  mkdir -p "$(dirname "$PCBM_AUDIO_CONF")"
  mkdir -p "$(dirname "$PCBM_ASOUNDRC")"
  : >"$PCBM_AUDIO_LOG" 2>/dev/null || true
}

load_audio_conf() {
  MODE="auto"
  CARD=""
  DEVICE="0"

  if [[ -f "$PCBM_AUDIO_CONF" ]]; then
    # shellcheck disable=SC1090
    source "$PCBM_AUDIO_CONF"
  fi

  [[ -z "${MODE:-}" ]] && MODE="auto"
  [[ -z "${DEVICE:-}" ]] && DEVICE="0"
}

save_audio_conf() {
  local mode="$1"
  local card="${2:-0}"
  local device="${3:-0}"

  ensure_audio_dirs
  cat >"$PCBM_AUDIO_CONF" <<EOF
MODE=$mode
CARD=$card
DEVICE=$device
EOF
}

card_for_vc4_index() {
  local idx="$1"
  local name="vc4hdmi${idx}"

  awk -v target="$name" '
    $0 ~ "\\[" target "[[:space:]]*\\]" { print $1; exit }
  ' /proc/asound/cards 2>/dev/null
}

first_vc4_card() {
  awk '/vc4hdmi/ { print $1; exit }' /proc/asound/cards 2>/dev/null
}

first_aplay_card_device() {
  aplay -l 2>/dev/null | awk '
    /^card [0-9]+:/ {
      card=$2; gsub(":", "", card)
      for (i=1; i<=NF; i++) {
        if ($i == "device") {
          dev=$(i+1); gsub(":", "", dev); print card " " dev; exit
        }
      }
    }
  '
}

connected_hdmi_indexes() {
  local status base name number idx
  for status in /sys/class/drm/card*-HDMI-A-*/status; do
    [[ -e "$status" ]] || continue
    [[ "$(cat "$status" 2>/dev/null)" == "connected" ]] || continue
    base="${status%/status}"
    name="$(basename "$base")"
    if [[ "$name" =~ HDMI-A-([0-9]+)$ ]]; then
      number="${BASH_REMATCH[1]}"
      idx=$((number - 1))
      (( idx >= 0 )) && printf '%s\n' "$idx"
    fi
  done | awk '!seen[$0]++'
}

resolve_auto_device() {
  local idx card fallback carddev

  # Prefer the HDMI connector Linux reports as physically connected.
  while IFS= read -r idx; do
    [[ -n "$idx" ]] || continue
    card="$(card_for_vc4_index "$idx")"
    if [[ -n "$card" ]]; then
      printf '%s 0\n' "$card"
      return 0
    fi
  done < <(connected_hdmi_indexes)

  # Fallback: first vc4 HDMI card exposed by ALSA.
  fallback="$(first_vc4_card)"
  if [[ -n "$fallback" ]]; then
    printf '%s 0\n' "$fallback"
    return 0
  fi

  # Last fallback: first playback device shown by aplay.
  carddev="$(first_aplay_card_device)"
  if [[ -n "$carddev" ]]; then
    printf '%s\n' "$carddev"
    return 0
  fi

  return 1
}

resolve_configured_device() {
  load_audio_conf

  case "$MODE" in
    auto|AUTO|Auto)
      resolve_auto_device
      ;;
    manual|MANUAL|Manual|card|CARD|Card)
      [[ -n "${CARD:-}" ]] || return 1
      printf '%s %s\n' "$CARD" "${DEVICE:-0}"
      ;;
    hdmi0|HDMI0)
      local c0
      c0="$(card_for_vc4_index 0)"
      [[ -z "$c0" ]] && c0="0"
      printf '%s 0\n' "$c0"
      ;;
    hdmi1|HDMI1)
      local c1
      c1="$(card_for_vc4_index 1)"
      [[ -z "$c1" ]] && c1="1"
      printf '%s 0\n' "$c1"
      ;;
    *)
      resolve_auto_device
      ;;
  esac
}

write_asoundrc() {
  local card="$1"
  local device="${2:-0}"

  ensure_audio_dirs
  cat >"$PCBM_ASOUNDRC" <<EOF
pcm.!default {
    type plug
    slave.pcm "hw:${card},${device}"
}

ctl.!default {
    type hw
    card ${card}
}
EOF

  log "Project CBM audio default set to hw:${card},${device} using ALSA plug conversion."
}

configure_audio() {
  local resolved card device
  ensure_audio_dirs
  resolved="$(resolve_configured_device || true)"

  if [[ -z "$resolved" ]]; then
    log "Project CBM audio: no playback device could be resolved."
    return 1
  fi

  read -r card device <<<"$resolved"
  [[ -z "$device" ]] && device="0"
  write_asoundrc "$card" "$device"
}

show_plain_status() {
  ensure_audio_dirs
  load_audio_conf
  echo "${PCBM_PROJECT_NAME:-Project CBM} Audio Status"
  echo "========================"
  echo "Version: ${PCBM_VERSION:-dev} (${PCBM_BUILD:-local})"
  echo
  echo "Config file: $PCBM_AUDIO_CONF"
  echo "Mode: ${MODE:-auto}"
  echo "Manual card/device: ${CARD:-unset}/${DEVICE:-0}"
  echo
  echo "Connected DRM HDMI connectors:"
  local found=0 status name state idx card
  for status in /sys/class/drm/card*-HDMI-A-*/status; do
    [[ -e "$status" ]] || continue
    found=1
    name="$(basename "${status%/status}")"
    state="$(cat "$status" 2>/dev/null)"
    idx="unknown"
    card="unknown"
    if [[ "$name" =~ HDMI-A-([0-9]+)$ ]]; then
      idx=$((${BASH_REMATCH[1]} - 1))
      card="$(card_for_vc4_index "$idx")"
      [[ -z "$card" ]] && card="unknown"
    fi
    echo "  $name: $state, HDMI index $idx, ALSA card $card"
  done
  (( found == 0 )) && echo "  none reported under /sys/class/drm"
  echo
  echo "ALSA playback devices:"
  aplay -l 2>/dev/null || echo "  aplay failed or alsa-utils is missing"
  echo
  echo "Current $PCBM_ASOUNDRC:"
  if [[ -f "$PCBM_ASOUNDRC" ]]; then
    sed 's/^/  /' "$PCBM_ASOUNDRC"
  else
    echo "  not created yet"
  fi
}

test_default() {
  configure_audio >/dev/null 2>&1 || true
  speaker-test -D default -c 2 -twav
}

test_card() {
  local idx="$1"
  local card
  card="$(card_for_vc4_index "$idx")"
  [[ -z "$card" ]] && card="$idx"
  speaker-test -D "plughw:${card},0" -c 2 -twav
}

menu_mode() {
  if [[ -f "$PCBM_DIALOG_LIB" ]]; then
    # shellcheck disable=SC1090
    source "$PCBM_DIALOG_LIB"
  else
    show_plain_status
    exit 0
  fi

  pcbm_trap_cleanup

  while true; do
    local status_text resolved
    resolved="$(resolve_configured_device 2>/dev/null || true)"
    [[ -z "$resolved" ]] && resolved="unresolved"
    status_text="Configured output: $resolved\n\nAUTO detects the currently connected HDMI output and writes ~/.asoundrc using ALSA's plug layer. Manual HDMI choices are available for stubborn displays."

    pcbm_show_menu "Project CBM Audio" "$status_text" \
      AUTO    "Auto-detect connected HDMI audio and set ALSA default" \
      HDMI0   "Force HDMI 0 / vc4hdmi0" \
      HDMI1   "Force HDMI 1 / vc4hdmi1" \
      TEST    "Run left/right speaker test using current default" \
      STATUS  "Show detailed ALSA and HDMI audio status" \
      RETURN  "<- Return to the control panel"

    case "$PCBM_STATUS" in
      0)
        case "$PCBM_CHOICE" in
          AUTO)
            save_audio_conf auto 0 0
            if configure_audio >/dev/null 2>&1; then
              pcbm_show_msg "Audio" "Project CBM audio is now set to AUTO.\n\nALSA default has been regenerated using the detected HDMI output and the plug conversion layer."
            else
              pcbm_show_msg "Audio" "Project CBM could not auto-detect a playback device.\n\nUse STATUS for details, or force HDMI 0 / HDMI 1."
            fi
            ;;
          HDMI0)
            local c0
            c0="$(card_for_vc4_index 0)"
            [[ -z "$c0" ]] && c0="0"
            save_audio_conf manual "$c0" 0
            configure_audio >/dev/null 2>&1 || true
            pcbm_show_msg "Audio" "Project CBM audio is now forced to HDMI 0 / hw:${c0},0."
            ;;
          HDMI1)
            local c1
            c1="$(card_for_vc4_index 1)"
            [[ -z "$c1" ]] && c1="1"
            save_audio_conf manual "$c1" 0
            configure_audio >/dev/null 2>&1 || true
            pcbm_show_msg "Audio" "Project CBM audio is now forced to HDMI 1 / hw:${c1},0."
            ;;
          TEST)
            pcbm_cleanup_terminal
            test_default
            read -r -p "Press ENTER to return to Project CBM Audio..." _
            ;;
          STATUS)
            pcbm_show_textbox "Project CBM Audio Status" "$(show_plain_status)"
            ;;
          RETURN)
            exit 0
            ;;
        esac
        ;;
      1|255)
        exit 0
        ;;
      *)
        exit 0
        ;;
    esac
  done
}

case "$COMMAND" in
  auto|configure|ensure)
    configure_audio
    ;;
  status)
    show_plain_status
    ;;
  test)
    test_default
    ;;
  test-hdmi0|test-0)
    test_card 0
    ;;
  test-hdmi1|test-1)
    test_card 1
    ;;
  set-auto)
    save_audio_conf auto 0 0
    configure_audio
    ;;
  set-hdmi0)
    c="$(card_for_vc4_index 0)"
    [[ -z "$c" ]] && c="0"
    save_audio_conf manual "$c" 0
    configure_audio
    ;;
  set-hdmi1)
    c="$(card_for_vc4_index 1)"
    [[ -z "$c" ]] && c="1"
    save_audio_conf manual "$c" 0
    configure_audio
    ;;
  menu|"")
    menu_mode
    ;;
  *)
    cat <<EOF
Usage: pcbm-audio [command]

Commands:
  auto|configure|ensure   Configure ~/.asoundrc from current Project CBM audio mode
  status                  Show ALSA/HDMI status
  test                    Run speaker-test through ALSA default
  test-hdmi0              Test HDMI 0 directly
  test-hdmi1              Test HDMI 1 directly
  set-auto                Use automatic connected-HDMI detection
  set-hdmi0               Force HDMI 0
  set-hdmi1               Force HDMI 1
  menu                    Open the Project CBM audio dialog menu

Options:
  --quiet, -q             Suppress normal output, useful before launching VICE
EOF
    exit 1
    ;;
esac
```

## scripts/pcbm-bbs

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-bbs
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

bbs_items=(
  "START"   "Start TCPser for TCP-to-serial modem connectivity"
  "STOP"    "Stop TCPser"
  "RESTART" "Restart TCPser"
  "STATUS"  "View TCPser service status"
  "RETURN"  "<- Return to the control panel"
)

show_tcpser_status() {
  if systemctl status tcpser >/dev/null 2>&1; then
    pcbm_show_textbox "TCPser Status" "$(systemctl status tcpser --no-pager 2>&1)"
  else
    pcbm_show_msg "TCPser Not Installed" "Project CBM could not read TCPser service information.\n\nMake sure a tcpser systemd service exists before using this menu."
  fi
}

run_tcpser() {
  local action="$1"
  if sudo -n systemctl "$action" tcpser >/dev/null 2>&1; then
    pcbm_show_msg "TCPser" "TCPser $action completed successfully."
  else
    pcbm_show_msg "TCPser" "TCPser $action failed.\n\nProject CBM may need passwordless sudo for /usr/bin/systemctl $action tcpser, or the service may not be installed."
  fi
}

while true; do
  prompt="TCPser service status: $(pcbm_service_active tcpser)\n\nPlease select a BBS or serial and modem option."
  pcbm_show_menu "Project CBM BBS / Modem" "$prompt" "${bbs_items[@]}"

  case "$PCBM_STATUS" in
    0)
      case "$PCBM_CHOICE" in
        START)   run_tcpser start ;;
        STOP)    run_tcpser stop ;;
        RESTART) run_tcpser restart ;;
        STATUS)  show_tcpser_status ;;
        RETURN)  exit 0 ;;
      esac
      ;;
    1|255)
      exit 0
      ;;
    *)
      exit 0
      ;;
  esac
done
```

## scripts/pcbm-boot

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-boot
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
EMU_PROFILE="${1:-$(tr -d '\r\n' </etc/pcbm/default-machine.conf)}"
VICE_LOG="/tmp/pcbm-vice.log"
PCBM_VERSION_CONF="/etc/pcbm/version.conf"

if [[ -f "$PCBM_VERSION_CONF" ]]; then
  # shellcheck source=/etc/pcbm/version.conf
  source "$PCBM_VERSION_CONF"
fi

export HOME="/home/pi"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_STATE_HOME="$HOME/.local/state"
export XDG_DATA_HOME="$HOME/.local/share"

mkdir -p \
  "$XDG_CONFIG_HOME/vice" \
  "$XDG_STATE_HOME/vice" \
  "$XDG_DATA_HOME/vice"

: >"$VICE_LOG"
touch "$XDG_STATE_HOME/vice/vice.log" 2>/dev/null

clear
reset
stty sane
chvt 1 >/dev/null 2>&1 || true

cd /home/pi/pcbm || exit 1

sleep 1

EMU_BIN=""
declare -a EMU_ARGS

case "$EMU_PROFILE" in
  x64|x64sc|xscpu64|x64dtv|x128|xcbm2|xcbm5x0|xvic|xplus4|xpet)
    EMU_BIN="$EMU_PROFILE"
    ;;
  x128-80col)
    EMU_BIN="x128"
    EMU_ARGS=("-80col")
    ;;
  "")
    echo "Project CBM: no default machine configured." >/dev/tty
    sleep 2
    exit 1
    ;;
  *)
    echo "Project CBM: unknown machine profile '$EMU_PROFILE'." >/dev/tty
    sleep 2
    exit 1
    ;;
esac

# Refresh ALSA's default output before each VICE launch.
# This lets Project CBM follow HDMI cable changes on Pi models with dual HDMI.
if command -v /usr/local/bin/pcbm-audio >/dev/null 2>&1; then
  /usr/local/bin/pcbm-audio auto --quiet >>"$VICE_LOG" 2>&1 || true
fi

/usr/bin/env \
  HOME="$HOME" \
  XDG_CONFIG_HOME="$XDG_CONFIG_HOME" \
  XDG_STATE_HOME="$XDG_STATE_HOME" \
  XDG_DATA_HOME="$XDG_DATA_HOME" \
  SDL_AUDIODRIVER=alsa \
  /usr/local/bin/"$EMU_BIN" "${EMU_ARGS[@]}" -sounddev sdl \
  </dev/tty >"$VICE_LOG" 2>&1

STATUS=$?

reset
stty sane
clear

if (( STATUS != 0 )); then
  echo "Project CBM: $EMU_BIN exited with status $STATUS. See $VICE_LOG" >/dev/tty
  sleep 2
fi

exit $STATUS
```

## scripts/pcbm-bootmode

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-bootmode
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

PCBM_BOOT_MODE_CONF="$PCBM_CONFIG_DIR/boot-mode.conf"

pcbm_boot_mode_raw() {
  local mode
  mode=$(tr -d '\r\n' < "$PCBM_BOOT_MODE_CONF" 2>/dev/null || printf 'menu')
  [[ -z "$mode" ]] && mode="menu"
  printf '%s\n' "$mode"
}

pcbm_boot_mode_label() {
  case "$(pcbm_boot_mode_raw)" in
    machine|MACHINE|Machine)
      echo "Default machine at boot"
      ;;
    menu|MENU|Menu|*)
      echo "Project CBM menu"
      ;;
  esac
}

pcbm_save_boot_mode() {
  local mode="$1"

  if ! sudo -n mkdir -p "$PCBM_CONFIG_DIR" 2>/dev/null; then
    pcbm_show_msg "Permission Required" "Project CBM could not create $PCBM_CONFIG_DIR without sudo.\n\nAdd a passwordless sudo rule for /usr/bin/mkdir, or create the folder manually."
    return 1
  fi

  if ! printf '%s\n' "$mode" | sudo -n tee "$PCBM_BOOT_MODE_CONF" >/dev/null 2>&1; then
    pcbm_show_msg "Permission Required" "Project CBM could not save the boot mode.\n\nAdd a passwordless sudo rule for /usr/bin/tee, or save this file manually:\n$PCBM_BOOT_MODE_CONF"
    return 1
  fi

  return 0
}

boot_items=(
  "MENU"    "Boot to the Project CBM menu (recommended default)"
  "MACHINE" "Boot directly into the saved default machine, then return to menu on exit"
  "STATUS"  "Show current boot mode and default machine"
  "RETURN"  "<- Return to the system menu"
)

while true; do
  prompt="Current boot mode: $(pcbm_boot_mode_label)\nDefault machine: $(pcbm_default_machine_label)\n\nDEFAULT MACHINE is the machine launched by RUN.\nBOOT MODE controls what happens when Project CBM starts on tty1."
  pcbm_show_menu "Project CBM Boot Mode" "$prompt" "${boot_items[@]}"

  case "$PCBM_STATUS" in
    0)
      case "$PCBM_CHOICE" in
        MENU)
          if pcbm_save_boot_mode "menu"; then
            pcbm_show_msg "Boot Mode Saved" "Project CBM will boot to the main menu."
          fi
          ;;
        MACHINE)
          if pcbm_yesno "Enable Machine Autostart" "Project CBM will boot directly into:\n$(pcbm_default_machine_label)\n\nWhen VICE exits, Project CBM will return to the main menu.\n\nEnable this boot mode?"; then
            if pcbm_save_boot_mode "machine"; then
              pcbm_show_msg "Boot Mode Saved" "Project CBM will boot directly into the saved default machine.\n\nExiting VICE returns to the Project CBM menu."
            fi
          fi
          ;;
        STATUS)
          pcbm_show_msg "Boot Mode Status" "Boot mode: $(pcbm_boot_mode_label)\nRaw config: $(pcbm_boot_mode_raw)\nDefault machine: $(pcbm_default_machine_label)\nConfig file:\n$PCBM_BOOT_MODE_CONF"
          ;;
        RETURN)
          exit 0
          ;;
      esac
      ;;
    1|255)
      exit 0
      ;;
    *)
      exit 0
      ;;
  esac
done
```

## scripts/pcbm-content

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-content
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

mkdir -p "$PCBM_CONTENT_BASE"/{games,demos,music,programs,roms}

category_items=(
  "GAMES"    "Browse games in /home/pi/pcbm/games"
  "DEMOS"    "Browse demos in /home/pi/pcbm/demos"
  "MUSIC"    "Browse music and SID files in /home/pi/pcbm/music"
  "PROGRAMS" "Browse programs in /home/pi/pcbm/programs"
  "ROMS"     "Browse ROM files in /home/pi/pcbm/roms"
  "RETURN"   "<- Return to the content menu"
)

pick_content_file() {
  local category="$1"
  local dir="$2"
  local label="$3"
  local -a files menu_items
  local file rel prompt emu

  while IFS= read -r -d '' file; do
    files+=("$file")
  done < <(pcbm_find_content_files "$dir")

  if (( ${#files[@]} == 0 )); then
    pcbm_show_msg "No $label Found" "Project CBM did not find any compatible files in:\n$dir\n\nCopy or import files there first."
    return 0
  fi

  menu_items=()
  for i in "${!files[@]}"; do
    rel="${files[$i]#$dir/}"
    menu_items+=("$i" "$rel")
  done
  menu_items+=("RETURN" "<- Return to the content menu")

  while true; do
    prompt="Category: $label\nDefault launch machine: $(pcbm_default_machine_label)\n\nPlease select a file to launch."
    pcbm_show_menu "Launch $label" "$prompt" "${menu_items[@]}"

    case "$PCBM_STATUS" in
      0)
        if [[ "$PCBM_CHOICE" == "RETURN" ]]; then
          return 0
        fi
        if [[ -n "${files[$PCBM_CHOICE]}" ]]; then
          emu=$(pcbm_default_machine)
          [[ -z "$emu" ]] && emu="x64sc"
          pcbm_infobox "Launching Content" "Launching $(basename "${files[$PCBM_CHOICE]}") with $emu..."
          sleep 1
          pcbm_launch_content "$emu" "${files[$PCBM_CHOICE]}"
        fi
        ;;
      1|255)
        return 0
        ;;
      *)
        return 0
        ;;
    esac
  done
}

while true; do
  prompt="Select a content area to browse.\n\nCurrent default machine: $(pcbm_default_machine_label)\n\nTip: Project CBM scans these folders recursively, so machine-specific subfolders such as games/c64 or demos/c128/80col are fine."
  pcbm_show_menu "Project CBM Content" "$prompt" "${category_items[@]}"

  case "$PCBM_STATUS" in
    0)
      case "$PCBM_CHOICE" in
        GAMES)    pick_content_file "games"    "$PCBM_CONTENT_BASE/games"    "Games" ;;
        DEMOS)    pick_content_file "demos"    "$PCBM_CONTENT_BASE/demos"    "Demos" ;;
        MUSIC)    pick_content_file "music"    "$PCBM_CONTENT_BASE/music"    "Music" ;;
        PROGRAMS) pick_content_file "programs" "$PCBM_CONTENT_BASE/programs" "Programs" ;;
        ROMS)     pick_content_file "roms"     "$PCBM_CONTENT_BASE/roms"     "ROMs" ;;
        RETURN)   exit 0 ;;
      esac
      ;;
    1|255)
      exit 0
      ;;
    *)
      exit 0
      ;;
  esac
done
```

## scripts/pcbm-control

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-control
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

control_items=(
  "NETWORK" "Network settings and file sharing options"
  "AUDIO"   "Audio output selection, HDMI auto-detect, and speaker tests"
  "BBS"     "BBS and serial or modem communication settings"
  "ROMS"    "JiffyDOS and machine ROM import and viewing"
  "SYSTEM"  "System settings and Project CBM information"
  "RETURN"  "<- Return to the main menu"
)

while true; do
  tcpser=$(pcbm_service_active tcpser)
  smbd=$(pcbm_service_active smbd)
  audio_mode=$(awk -F= '/^MODE=/ {print $2}' /home/pi/.config/pcbm/audio.conf 2>/dev/null)
  [[ -z "$audio_mode" ]] && audio_mode="auto"
  prompt="${PCBM_PROJECT_NAME:-Project CBM} image v${PCBM_VERSION:-dev} | menu v${PCBM_MENU_VERSION:-6.5} (${PCBM_BUILD:-local})\nNetwork sharing (Samba): $smbd\nBBS service (TCPser): $tcpser\nAudio mode: $audio_mode\n\nPlease select a control panel option."
  pcbm_show_menu "Project CBM Control Panel" "$prompt" "${control_items[@]}"

  case "$PCBM_STATUS" in
    0)
      case "$PCBM_CHOICE" in
        NETWORK) "$SCRIPT_DIR/pcbm-network" ;;
        AUDIO)   "$SCRIPT_DIR/pcbm-audio" ;;
        BBS)     "$SCRIPT_DIR/pcbm-bbs" ;;
        ROMS)    "$SCRIPT_DIR/pcbm-roms" ;;
        SYSTEM)  "$SCRIPT_DIR/pcbm-system" ;;
        RETURN)  exit 0 ;;
      esac
      ;;
    1|255)
      exit 0
      ;;
    *)
      exit 0
      ;;
  esac
done
```

## scripts/pcbm-cover

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-cover
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#

COVER_DIR="/opt/pcbm/covers"
DISPLAY_TIME=3

machine="${1:-}"

[ ! -d "$COVER_DIR" ] && exit 0

# Only run on tty1
if [[ "$(tty)" != "/dev/tty1" ]]; then
    exit 0
fi

pick_random_cover() {
    mapfile -t COVERS < <(
        find "$COVER_DIR" -maxdepth 1 -type f \
        \( -iname "pcbmcover[0-9]*.jpg" -o -iname "pcbmcover[0-9]*.png" \)
    )

    [ ${#COVERS[@]} -eq 0 ] && return 1

    printf '%s\n' "${COVERS[RANDOM % ${#COVERS[@]}]}"
}

pick_machine_cover() {
    local candidate

    candidate="$COVER_DIR/pcbmcover-${machine}.jpg"
    [[ -f "$candidate" ]] && {
        printf '%s\n' "$candidate"
        return 0
    }

    candidate="$COVER_DIR/pcbmcover-${machine}.png"
    [[ -f "$candidate" ]] && {
        printf '%s\n' "$candidate"
        return 0
    }

    pick_random_cover
}

if [[ -n "$machine" ]]; then
    COVER="$(pick_machine_cover)"
else
    COVER="$(pick_random_cover)"
fi

[ -z "$COVER" ] && exit 0

tput civis 2>/dev/null

cleanup() {
    tput cnorm 2>/dev/null
    clear
}
trap cleanup EXIT

clear

read FB_WIDTH FB_HEIGHT < <(
    fbset -s | awk '/geometry/ {print $2, $3}'
)

TARGET_HEIGHT=$((FB_HEIGHT * 50 / 100))

TMP_IMG="/tmp/pcbm_splash_$$.png"

convert "$COVER" \
  -resize x${TARGET_HEIGHT} \
  -gravity center \
  -background black \
  -extent ${FB_WIDTH}x${FB_HEIGHT} \
  "$TMP_IMG"

fbi -a --autozoom --once -noverbose -t "$DISPLAY_TIME" "$TMP_IMG"

rm -f "$TMP_IMG"
```

## scripts/pcbm-dialog-lib.sh

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-dialog-lib.sh
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
PCBM_VERSION_CONF="/etc/pcbm/version.conf"

if [[ -f "$PCBM_VERSION_CONF" ]]; then
  # shellcheck source=/etc/pcbm/version.conf
  source "$PCBM_VERSION_CONF"
else
  PCBM_PROJECT_NAME="Project CBM"
  PCBM_INTERNAL_NAME="pcbm"
  PCBM_VERSION="dev"
  PCBM_BUILD="local"
  PCBM_AUTHOR="Craig Daters"
  PCBM_REPO="https://github.com/cdaters/project-cbm"
  PCBM_TAGLINE="Power on. Boot fast. No nonsense. Just Commodore."
fi

PCBM_BACKTITLE="*** ${PCBM_PROJECT_NAME} v${PCBM_VERSION} - Raspberry Pi / Commodore machine distribution ***"
PCBM_HLINE="ENTER=Select   TAB=Buttons   ARROWS=Move   ESC=Back"
PCBM_MIN_WIDTH=72
PCBM_MAX_WIDTH=100
PCBM_EXTRA_WIDTH=12
PCBM_MIN_HEIGHT=14
PCBM_MAX_HEIGHT=22
PCBM_HEIGHT_PADDING=8
PCBM_BOX_MIN_WIDTH=56
PCBM_BOX_MAX_WIDTH=96
PCBM_BOX_MIN_HEIGHT=8
PCBM_BOX_MAX_HEIGHT=18
PCBM_TEXTBOX_MIN_WIDTH=64
PCBM_TEXTBOX_MAX_WIDTH=100
PCBM_TEXTBOX_MIN_HEIGHT=12
PCBM_TEXTBOX_MAX_HEIGHT=22
PCBM_CONTENT_BASE="/home/pi/pcbm"
PCBM_CONFIG_DIR="/etc/pcbm"
PCBM_DEFAULT_MACHINE_CONF="$PCBM_CONFIG_DIR/default-machine.conf"
PCBM_JIFFYDOS_CONF="$PCBM_CONFIG_DIR/jiffydos.conf"
PCBM_USB_MOUNT="/mnt/pcbm-usb"
PCBM_VICE_LOG="/tmp/pcbm-vice.log"

pcbm_cleanup_terminal() {
  clear
  stty sane 2>/dev/null || true
  tput cnorm 2>/dev/null || true
}

pcbm_trap_cleanup() {
  trap pcbm_cleanup_terminal EXIT
}

pcbm_term_cols() {
  tput cols 2>/dev/null || echo 80
}

pcbm_term_lines() {
  tput lines 2>/dev/null || echo 24
}

pcbm_expand_text() {
  printf '%b' "$1"
}

pcbm_longest_line() {
  local input
  input=$(pcbm_expand_text "$1")
  local max=0
  local line len
  while IFS= read -r line; do
    len=${#line}
    (( len > max )) && max=$len
  done <<< "$input"
  echo "$max"
}

pcbm_count_lines() {
  local input
  input=$(pcbm_expand_text "$1")
  local count=0
  while IFS= read -r _; do
    ((count++))
  done <<< "$input"
  (( count == 0 )) && count=1
  echo "$count"
}

pcbm_clamp() {
  local value="$1" min="$2" max="$3"
  (( value < min )) && value=$min
  (( value > max )) && value=$max
  echo "$value"
}

pcbm_calc_menu_dims() {
  local title="$1"
  local prompt="$2"
  shift 2
  local -a items=("$@")
  local item_count=$(( ${#items[@]} / 2 ))
  local max_tag=0 max_desc=0 max_prompt max_title max_hline desired_width
  local term_cols term_lines prompt_lines desired_height list_height tag desc i max_width max_height

  for ((i=0; i<${#items[@]}; i+=2)); do
    tag="${items[i]}"
    desc="${items[i+1]}"
    (( ${#tag} > max_tag )) && max_tag=${#tag}
    (( ${#desc} > max_desc )) && max_desc=${#desc}
  done

  max_prompt=$(pcbm_longest_line "$prompt")
  max_title=${#title}
  max_hline=${#PCBM_HLINE}
  desired_width=$(( max_tag + max_desc + PCBM_EXTRA_WIDTH ))
  (( max_prompt + 8 > desired_width )) && desired_width=$(( max_prompt + 8 ))
  (( max_title + 8 > desired_width )) && desired_width=$(( max_title + 8 ))
  (( max_hline + 4 > desired_width )) && desired_width=$(( max_hline + 4 ))

  term_cols=$(pcbm_term_cols)
  max_width=$(( term_cols - 4 ))
  (( max_width > PCBM_MAX_WIDTH )) && max_width=$PCBM_MAX_WIDTH
  PCBM_WIDTH=$(pcbm_clamp "$desired_width" "$PCBM_MIN_WIDTH" "$max_width")

  prompt_lines=$(pcbm_count_lines "$prompt")
  desired_height=$(( item_count + prompt_lines + PCBM_HEIGHT_PADDING ))
  term_lines=$(pcbm_term_lines)
  max_height=$(( term_lines - 2 ))
  (( max_height > PCBM_MAX_HEIGHT )) && max_height=$PCBM_MAX_HEIGHT
  PCBM_HEIGHT=$(pcbm_clamp "$desired_height" "$PCBM_MIN_HEIGHT" "$max_height")

  list_height=$(( PCBM_HEIGHT - prompt_lines - 7 ))
  (( list_height < 3 )) && list_height=3
  (( list_height > item_count )) && list_height=$item_count
  (( list_height < 1 )) && list_height=1
  PCBM_MENU_SIZE=$list_height
}

pcbm_calc_checklist_dims() {
  local title="$1"
  local prompt="$2"
  shift 2
  local -a items=("$@")
  local item_count=$(( ${#items[@]} / 3 ))
  local max_tag=0 max_desc=0 max_prompt max_title max_hline desired_width
  local term_cols term_lines prompt_lines desired_height list_height tag desc i max_width max_height

  for ((i=0; i<${#items[@]}; i+=3)); do
    tag="${items[i]}"
    desc="${items[i+1]}"
    (( ${#tag} > max_tag )) && max_tag=${#tag}
    (( ${#desc} > max_desc )) && max_desc=${#desc}
  done

  max_prompt=$(pcbm_longest_line "$prompt")
  max_title=${#title}
  max_hline=${#PCBM_HLINE}
  desired_width=$(( max_tag + max_desc + PCBM_EXTRA_WIDTH + 6 ))
  (( max_prompt + 8 > desired_width )) && desired_width=$(( max_prompt + 8 ))
  (( max_title + 8 > desired_width )) && desired_width=$(( max_title + 8 ))
  (( max_hline + 4 > desired_width )) && desired_width=$(( max_hline + 4 ))

  term_cols=$(pcbm_term_cols)
  max_width=$(( term_cols - 4 ))
  (( max_width > PCBM_MAX_WIDTH )) && max_width=$PCBM_MAX_WIDTH
  PCBM_WIDTH=$(pcbm_clamp "$desired_width" "$PCBM_MIN_WIDTH" "$max_width")

  prompt_lines=$(pcbm_count_lines "$prompt")
  desired_height=$(( item_count + prompt_lines + PCBM_HEIGHT_PADDING + 1 ))
  term_lines=$(pcbm_term_lines)
  max_height=$(( term_lines - 2 ))
  (( max_height > PCBM_MAX_HEIGHT )) && max_height=$PCBM_MAX_HEIGHT
  PCBM_HEIGHT=$(pcbm_clamp "$desired_height" "$PCBM_MIN_HEIGHT" "$max_height")

  list_height=$(( PCBM_HEIGHT - prompt_lines - 8 ))
  (( list_height < 3 )) && list_height=3
  (( list_height > item_count )) && list_height=$item_count
  (( list_height < 1 )) && list_height=1
  PCBM_MENU_SIZE=$list_height
}

pcbm_calc_box_dims() {
  local text="$1"
  local min_width="$2"
  local max_width_cap="$3"
  local min_height="$4"
  local max_height_cap="$5"
  local longest lines term_cols term_lines max_width max_height

  longest=$(pcbm_longest_line "$text")
  lines=$(pcbm_count_lines "$text")
  term_cols=$(pcbm_term_cols)
  term_lines=$(pcbm_term_lines)

  max_width=$(( term_cols - 4 ))
  (( max_width > max_width_cap )) && max_width=$max_width_cap
  max_height=$(( term_lines - 2 ))
  (( max_height > max_height_cap )) && max_height=$max_height_cap

  PCBM_WIDTH=$(pcbm_clamp $(( longest + 8 )) "$min_width" "$max_width")
  PCBM_HEIGHT=$(pcbm_clamp $(( lines + 6 )) "$min_height" "$max_height")
}

pcbm_show_menu() {
  local title="$1"
  local prompt="$2"
  shift 2
  local -a items=("$@")
  prompt=$(pcbm_expand_text "$prompt")
  pcbm_calc_menu_dims "$title" "$prompt" "${items[@]}"
  PCBM_CHOICE=$(dialog --stdout --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --menu "$prompt" "$PCBM_HEIGHT" "$PCBM_WIDTH" "$PCBM_MENU_SIZE" \
    "${items[@]}")
  PCBM_STATUS=$?
  pcbm_cleanup_terminal
}

pcbm_show_checklist() {
  local title="$1"
  local prompt="$2"
  shift 2
  local -a items=("$@")
  prompt=$(pcbm_expand_text "$prompt")
  pcbm_calc_checklist_dims "$title" "$prompt" "${items[@]}"
  PCBM_CHOICE=$(dialog --stdout --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --checklist "$prompt" "$PCBM_HEIGHT" "$PCBM_WIDTH" "$PCBM_MENU_SIZE" \
    "${items[@]}")
  PCBM_STATUS=$?
  pcbm_cleanup_terminal
}

pcbm_show_msg() {
  local title="$1"
  local text="$2"
  text=$(pcbm_expand_text "$text")
  pcbm_calc_box_dims "$text" "$PCBM_BOX_MIN_WIDTH" "$PCBM_BOX_MAX_WIDTH" "$PCBM_BOX_MIN_HEIGHT" "$PCBM_BOX_MAX_HEIGHT"
  dialog --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --msgbox "$text" "$PCBM_HEIGHT" "$PCBM_WIDTH"
  pcbm_cleanup_terminal
}

pcbm_show_textbox() {
  local title="$1"
  local text="$2"
  local tmp status
  text=$(pcbm_expand_text "$text")
  pcbm_calc_box_dims "$text" "$PCBM_TEXTBOX_MIN_WIDTH" "$PCBM_TEXTBOX_MAX_WIDTH" "$PCBM_TEXTBOX_MIN_HEIGHT" "$PCBM_TEXTBOX_MAX_HEIGHT"
  tmp=$(mktemp)
  printf '%s\n' "$text" > "$tmp"
  dialog --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --scrollbar \
    --textbox "$tmp" "$PCBM_HEIGHT" "$PCBM_WIDTH"
  status=$?
  rm -f "$tmp"
  pcbm_cleanup_terminal
  return $status
}

pcbm_yesno() {
  local title="$1"
  local text="$2"
  text=$(pcbm_expand_text "$text")
  pcbm_calc_box_dims "$text" "$PCBM_BOX_MIN_WIDTH" "$PCBM_BOX_MAX_WIDTH" "$PCBM_BOX_MIN_HEIGHT" "$PCBM_BOX_MAX_HEIGHT"
  dialog --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --yesno "$text" "$PCBM_HEIGHT" "$PCBM_WIDTH"
  local status=$?
  pcbm_cleanup_terminal
  return $status
}

pcbm_infobox() {
  local title="$1"
  local text="$2"
  text=$(pcbm_expand_text "$text")
  pcbm_calc_box_dims "$text" 46 76 6 10
  dialog --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --infobox "$text" "$PCBM_HEIGHT" "$PCBM_WIDTH"
}

pcbm_default_machine() {
  cat "$PCBM_DEFAULT_MACHINE_CONF" 2>/dev/null
}

pcbm_default_machine_label() {
  case "$(pcbm_default_machine)" in
    x64) echo "Commodore 64 (Fast)" ;;
    x64sc) echo "Commodore 64 (Recommended for games and demos)" ;;
    xscpu64) echo "Commodore 64 with CMD SuperCPU" ;;
    x64dtv) echo "Commodore 64 DTV" ;;
    x128) echo "Commodore 128 (40-column VIC display)" ;;
    x128-80col) echo "Commodore 128 (80-column VDC mode)" ;;
    xcbm2) echo "CBM-II" ;;
    xcbm5x0) echo "CBM-5x0" ;;
    xvic) echo "VIC-20" ;;
    xplus4) echo "Plus/4" ;;
    xpet) echo "PET" ;;
    *) echo "Not set" ;;
  esac
}

pcbm_machine_tag_to_emu() {
  case "$1" in
    C64) echo "x64" ;;
    C64SC) echo "x64sc" ;;
    SCPU64) echo "xscpu64" ;;
    C64DTV) echo "x64dtv" ;;
    C128) echo "x128" ;;
    C12880) echo "x128-80col" ;;
    CBM2) echo "xcbm2" ;;
    CBM5) echo "xcbm5x0" ;;
    VIC20) echo "xvic" ;;
    PET) echo "xpet" ;;
    PLUS4) echo "xplus4" ;;
    *) return 1 ;;
  esac
}

pcbm_emu_to_machine_tag() {
  case "$1" in
    x64) echo "C64" ;;
    x64sc) echo "C64SC" ;;
    xscpu64) echo "SCPU64" ;;
    x64dtv) echo "C64DTV" ;;
    x128) echo "C128" ;;
    x128-80col) echo "C12880" ;;
    xcbm2) echo "CBM2" ;;
    xcbm5x0) echo "CBM5" ;;
    xvic) echo "VIC20" ;;
    xpet) echo "PET" ;;
    xplus4) echo "PLUS4" ;;
    *) return 1 ;;
  esac
}

pcbm_emu_to_cover_tag() {
  case "$1" in
    x64|x64sc|xscpu64|x64dtv)
      echo "c64"
      ;;
    x128|x128-80col)
      echo "c128"
      ;;
    xcbm2)
      echo "cbm2"
      ;;
    xcbm5x0)
      echo "cbm5"
      ;;
    xvic)
      echo "vic20"
      ;;
    xpet)
      echo "pet"
      ;;
    xplus4)
      echo "plus4"
      ;;
    *)
      return 1
      ;;
  esac
}

pcbm_save_default_machine() {
  local emu="$1"
  if ! sudo -n mkdir -p "$PCBM_CONFIG_DIR" 2>/dev/null; then
    pcbm_show_msg "Permission Required" "Project CBM could not create $PCBM_CONFIG_DIR without sudo.\n\nAdd a passwordless sudo rule for mkdir and tee, or create the file manually."
    return 1
  fi

  if ! printf '%s\n' "$emu" | sudo -n tee "$PCBM_DEFAULT_MACHINE_CONF" >/dev/null 2>&1; then
    pcbm_show_msg "Permission Required" "Project CBM could not save the default machine.\n\nAdd a passwordless sudo rule for /usr/bin/tee or save the file manually:\n$PCBM_DEFAULT_MACHINE_CONF"
    return 1
  fi
  return 0
}

pcbm_service_active() {
  local service="$1"
  if systemctl list-unit-files "$service.service" >/dev/null 2>&1 || systemctl status "$service" >/dev/null 2>&1; then
    systemctl is-active "$service" 2>/dev/null || echo "inactive"
  else
    echo "not installed"
  fi
}

pcbm_hostname() {
  hostname 2>/dev/null || echo "unknown"
}

pcbm_ip_address() {
  hostname -I 2>/dev/null | awk '{print $1}'
}

pcbm_gateway() {
  ip route 2>/dev/null | awk '/default/ {print $3; exit}'
}

pcbm_dns_server() {
  awk '/^nameserver/ {print $2}' /etc/resolv.conf | paste -sd ','
}

pcbm_mount_usb_first_partition() {
  local dev

  if [[ ! -d "$PCBM_USB_MOUNT" ]]; then
    sudo -n mkdir -p "$PCBM_USB_MOUNT" || {
      echo ""
      return 2
    }
  fi

  dev=$(lsblk -rpno NAME,RM,TYPE | awk '$2==1 && $3=="part" {print $1; exit}')
  if [[ -z "$dev" ]]; then
    echo ""
    return 1
  fi

  if ! sudo -n mount "$dev" "$PCBM_USB_MOUNT" 2>/dev/null; then
    echo ""
    return 2
  fi

  echo "$dev"
  return 0
}

pcbm_unmount_usb() {
  sudo -n umount "$PCBM_USB_MOUNT" >/dev/null 2>&1 || true
}

pcbm_filtered_find() {
  local search_base="$1"
  shift

  find "$search_base" \
    \( -type d \( \
        -name '.*' -o \
        -name '__MACOSX' -o \
        -name '.Trashes' -o \
        -name '.Spotlight-V100' -o \
        -name '.fseventsd' \
      \) -prune \) -o \
    \( -type f \( \
        -name '.*' -o \
        -name '._*' -o \
        -name '.DS_Store' -o \
        -name '.AppleDouble' -o \
        -name '.LSOverride' -o \
        -name '.VolumeIcon.icns' -o \
        -name '.apdisk' -o \
        -name 'Thumbs.db' -o \
        -name 'desktop.ini' \
      \) -prune \) -o \
    "$@" -print0
}

pcbm_content_extensions() {
  cat <<'EXTS'
*.d64
*.d67
*.d71
*.d80
*.d81
*.d82
*.g64
*.g41
*.x64
*.p64
*.t64
*.tap
*.crt
*.prg
*.p00
*.sid
*.mus
*.bin
*.rom
*.reu
EXTS
}

pcbm_find_content_files() {
  local dir="$1"
  local expr=( )
  local pat first=1
  while IFS= read -r pat; do
    [[ -z "$pat" ]] && continue
    if (( first )); then
      expr+=( -iname "$pat" )
      first=0
    else
      expr+=( -o -iname "$pat" )
    fi
  done < <(pcbm_content_extensions)

  pcbm_filtered_find "$dir" -type f \( "${expr[@]}" \) | sort -z
}

pcbm_copy_clean() {
  local src="$1"
  local dest="$2"
  local base target path rel

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --ignore-existing --prune-empty-dirs \
      --exclude='.*' \
      --exclude='._*' \
      --exclude='.DS_Store' \
      --exclude='.AppleDouble' \
      --exclude='.LSOverride' \
      --exclude='.VolumeIcon.icns' \
      --exclude='.apdisk' \
      --exclude='__MACOSX/' \
      --exclude='.Trashes/' \
      --exclude='.Spotlight-V100/' \
      --exclude='.fseventsd/' \
      "$src" "$dest/"
    return $?
  fi

  if [[ -f "$src" ]]; then
    case "$(basename "$src")" in
      .* ) return 0 ;;
    esac
    cp -n "$src" "$dest/"
    return $?
  fi

  if [[ -d "$src" ]]; then
    base=$(basename "$src")
    target="$dest/$base"
    mkdir -p "$target" || return 1

    while IFS= read -r -d '' path; do
      rel="${path#$src/}"
      if [[ -d "$path" ]]; then
        mkdir -p "$target/$rel" || return 1
      elif [[ -f "$path" ]]; then
        mkdir -p "$(dirname "$target/$rel")" || return 1
        cp -n "$path" "$target/$rel" || return 1
      fi
    done < <(pcbm_filtered_find "$src" -mindepth 1 | sort -z)
    return 0
  fi

  return 1
}

pcbm_active_jiffydos() {
  local rom
  rom=$(cat "$PCBM_JIFFYDOS_CONF" 2>/dev/null)
  [[ -n "$rom" && -f "$rom" ]] && printf '%s\n' "$rom"
}

pcbm_launch_machine() {
  local emu="$1"
  local machine_tag

  # machine_tag=$(pcbm_emu_to_machine_tag "$emu" | tr '[:upper:]' '[:lower:]')
  machine_tag=$(pcbm_emu_to_cover_tag "$emu")

  pcbm_cleanup_terminal

  if command -v /usr/local/bin/pcbm-cover >/dev/null 2>&1; then
    /usr/local/bin/pcbm-cover "$machine_tag"
  fi

  /usr/local/bin/pcbm-boot "$emu"
}

pcbm_launch_content() {
  local emu="$1"
  local file="$2"
  local active_rom
  local emu_bin="$emu"
  local status=0
  local -a cmd extra_args

  case "$emu" in
    x128-80col)
      emu_bin="x128"
      extra_args=("-80col")
      ;;
  esac

  if ! command -v "$emu_bin" >/dev/null 2>&1; then
    pcbm_show_msg "Emulator Missing" "Project CBM could not find the emulator binary: $emu_bin"
    return 1
  fi

  export HOME="/home/pi"
  export XDG_CONFIG_HOME="$HOME/.config"
  export XDG_STATE_HOME="$HOME/.local/state"
  export XDG_DATA_HOME="$HOME/.local/share"

  mkdir -p \
    "$XDG_CONFIG_HOME/vice" \
    "$XDG_STATE_HOME/vice" \
    "$XDG_DATA_HOME/vice"

  cmd=("$emu_bin" "${extra_args[@]}" "-sounddev" "sdl" "-autostart" "$file")
  active_rom=$(pcbm_active_jiffydos)
  if [[ "$emu_bin" == "x64sc" && -n "$active_rom" ]]; then
    cmd=("$emu_bin" "-kernal" "$active_rom" "${extra_args[@]}" "-sounddev" "sdl" "-autostart" "$file")
  fi

  : >"$PCBM_VICE_LOG"
  pcbm_cleanup_terminal
  # Refresh ALSA's default output before launching content.
  # This keeps content launches aligned with the same HDMI auto-detection path as machine launches.
  if command -v /usr/local/bin/pcbm-audio >/dev/null 2>&1; then
    /usr/local/bin/pcbm-audio auto --quiet >>"$PCBM_VICE_LOG" 2>&1 || true
  fi

  /usr/bin/env \
    HOME="$HOME" \
    XDG_CONFIG_HOME="$XDG_CONFIG_HOME" \
    XDG_STATE_HOME="$XDG_STATE_HOME" \
    XDG_DATA_HOME="$XDG_DATA_HOME" \
    SDL_AUDIODRIVER=alsa \
    "${cmd[@]}" </dev/tty >"$PCBM_VICE_LOG" 2>&1

  status=$?

  if (( status != 0 )); then
    pcbm_show_msg "VICE Launch Failed" "Project CBM could not launch the selected content.\n\nSee log:\n$PCBM_VICE_LOG"
  fi

  return $status
}
```

## scripts/pcbm-firstboot-check

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-firstboot-check
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#

echo "Project CBM first boot validation"
df -h /
systemctl is-active smbd || true
systemctl is-active avahi-daemon || true
command -v x64sc >/dev/null && echo "VICE present"
```

## scripts/pcbm-import

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-import
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
# Project CBM v6.4.3c Importer
# Stable hybrid USB browser/importer:
# - SPACE selects files/folders
# - ENTER/OK processes selection
# - Single selected folder opens an explicit Browse / Import / Cancel menu
# - ALL imports everything in the current folder
# - Parent Directory climbs up one level
# - Uses a temp file for selected paths instead of stdout plumbing

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

mkdir -p "$PCBM_CONTENT_BASE"/{games,demos,music,programs}

dest_items=(
  "games"    "Games"
  "demos"    "Demos"
  "music"    "Music"
  "programs" "Programs"
  "RETURN"   "<- Return without importing"
)

folder_action_items=(
  "BROWSE" "Browse into this folder"
  "IMPORT" "Import this folder recursively"
  "CANCEL" "<- Go back"
)

browse_and_select() {
  local output_file="$1"
  local current="$PCBM_USB_MOUNT"
  local -a items menu_items selected selected_items
  local item base idx action

  : > "$output_file"

  while true; do
    items=()
    menu_items=("ALL" "[Import Everything in This Folder]" "off")

    if [[ "$current" != "$PCBM_USB_MOUNT" ]]; then
      menu_items+=(".." "[Parent Directory]" "off")
    fi

    while IFS= read -r -d '' item; do
      items+=("$item")
    done < <(pcbm_filtered_find "$current" -mindepth 1 -maxdepth 1 | sort -z)

    for i in "${!items[@]}"; do
      base=$(basename "${items[$i]}")
      if [[ -d "${items[$i]}" ]]; then
        menu_items+=("$i" "[Folder] $base" "off")
      else
        menu_items+=("$i" "[File] $base" "off")
      fi
    done

    pcbm_show_checklist "Import from USB"       "Current folder:\n$current\n\nSPACE = select item(s)\nENTER/OK = process selection\n\nSelect one folder to choose Browse or Import."       "${menu_items[@]}"

    (( PCBM_STATUS != 0 )) && return 1

    read -r -a selected <<< "$(echo "$PCBM_CHOICE" | tr -d '"')"

    if (( ${#selected[@]} == 0 )); then
      pcbm_show_msg "Nothing Selected" "Use SPACE to select one or more files/folders, then press ENTER or choose OK."
      continue
    fi

    if printf '%s\n' "${selected[@]}" | grep -qx "ALL"; then
      for item in "${items[@]}"; do
        printf '%s\n' "$item" >> "$output_file"
      done
      return 0
    fi

    if printf '%s\n' "${selected[@]}" | grep -qx ".."; then
      [[ "$current" != "$PCBM_USB_MOUNT" ]] && current=$(dirname "$current")
      continue
    fi

    # If exactly one folder is selected, explicitly ask Browse vs Import.
    if (( ${#selected[@]} == 1 )); then
      idx="${selected[0]}"
      if [[ "$idx" =~ ^[0-9]+$ && -n "${items[$idx]}" && -d "${items[$idx]}" ]]; then
        pcbm_show_menu "Folder Selected"           "Folder:\n$(basename "${items[$idx]}")\n\nWhat would you like to do?"           "${folder_action_items[@]}"

        case "$PCBM_CHOICE" in
          BROWSE)
            current="${items[$idx]}"
            continue
            ;;
          IMPORT)
            printf '%s\n' "${items[$idx]}" >> "$output_file"
            return 0
            ;;
          CANCEL|*)
            continue
            ;;
        esac
      fi
    fi

    selected_items=()
    for idx in "${selected[@]}"; do
      [[ "$idx" =~ ^[0-9]+$ ]] || continue
      [[ -n "${items[$idx]}" ]] && selected_items+=("${items[$idx]}")
    done

    if (( ${#selected_items[@]} == 0 )); then
      pcbm_show_msg "Nothing Importable Selected" "Project CBM did not find any valid selected files or folders."
      continue
    fi

    for item in "${selected_items[@]}"; do
      printf '%s\n' "$item" >> "$output_file"
    done

    return 0
  done
}

run_import() {
  local dev dest_dir item count=0 selected_file
  local -a selected_paths

  pcbm_infobox "USB Import" "Scanning for a USB drive..."
  sleep 1

  dev=$(pcbm_mount_usb_first_partition)
  case $? in
    1)
      pcbm_show_msg "USB Drive Not Found" "Project CBM could not find a removable USB partition to mount."
      return 0
      ;;
    2)
      pcbm_show_msg "Mount Failed" "Project CBM found a USB drive but could not mount it.\n\nPlease verify passwordless sudo for mount, umount, and mkdir."
      return 0
      ;;
  esac

  selected_file=$(mktemp)

  if ! browse_and_select "$selected_file"; then
    rm -f "$selected_file"
    pcbm_unmount_usb
    return 0
  fi

  mapfile -t selected_paths < "$selected_file"
  rm -f "$selected_file"

  if (( ${#selected_paths[@]} == 0 )); then
    pcbm_unmount_usb
    return 0
  fi

  pcbm_show_menu "Select Destination"     "Choose where the selected USB content should be copied."     "${dest_items[@]}"

  if (( PCBM_STATUS != 0 )) || [[ "$PCBM_CHOICE" == "RETURN" ]]; then
    pcbm_unmount_usb
    return 0
  fi

  dest_dir="$PCBM_CONTENT_BASE/$PCBM_CHOICE"
  mkdir -p "$dest_dir"

  pcbm_infobox "Importing Files" "Copying selected item(s) to:\n$dest_dir"
  sleep 1
  : >/tmp/pcbm-import.log

  for item in "${selected_paths[@]}"; do
    echo "COPYING: [$item]" >> /tmp/pcbm-import-debug.log
    if [[ -e "$item" ]]; then
      pcbm_copy_clean "$item" "$dest_dir" >>/tmp/pcbm-import.log 2>&1 && ((count++))
    fi
  done

  pcbm_unmount_usb
  pcbm_show_msg "Import Complete" "Imported $count item(s) into:\n$dest_dir"
}

while true; do
  prompt="Import content from a USB drive into Project CBM folders.\n\nYou can browse into folders or import entire folders recursively."
  pcbm_show_menu "Project CBM Import" "$prompt"     "IMPORT" "Import files or folders from a USB drive"     "RETURN" "<- Return to the main menu"

  case "$PCBM_STATUS" in
    0)
      case "$PCBM_CHOICE" in
        IMPORT) run_import ;;
        RETURN) exit 0 ;;
      esac
      ;;
    1|255)
      exit 0
      ;;
    *)
      exit 0
      ;;
  esac
done
```

## scripts/pcbm-machines

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-machines
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

machine_items=(
  "C64"     "Start the Commodore 64 (Faster, for older or weaker systems)"
  "C64SC"   "Start the Commodore 64 (Recommended for games and demos)"
  "SCPU64"  "Start the Commodore 64 with CMD SuperCPU"
  "C64DTV"  "Start the Commodore 64 DTV"
  "C128"    "Start the Commodore 128 (40-column VIC display)"
  "C12880"  "Start the Commodore 128 in 80-column VDC mode"
  "CBM2"    "Start the CBM-II"
  "CBM5"    "Start the CBM-5x0"
  "VIC20"   "Start the VIC-20"
  "PLUS4"   "Start the Plus/4"
  "PET"     "Start the PET"
  "DEFAULT" "Set the default machine launched by Project CBM"
  "RETURN"  "<- Return to the main menu"
)

default_items=(
  "C64"    "Commodore 64 (Fast emulator)"
  "C64SC"  "Commodore 64 (Recommended for games and demos)"
  "SCPU64" "Commodore 64 with CMD SuperCPU"
  "C64DTV" "Commodore 64 DTV"
  "C128"   "Commodore 128 (40-column VIC display)"
  "C12880" "Commodore 128 (80-column VDC mode)"
  "CBM2"   "CBM-II"
  "CBM5"   "CBM-5x0"
  "VIC20"  "VIC-20"
  "PLUS4"  "Plus/4"
  "PET"    "PET"
  "RETURN" "<- Return without changing the default"
)

while true; do
  prompt="Current default machine: $(pcbm_default_machine_label)\n\nPlease select a machine to launch, or choose DEFAULT to save one for startup."
  pcbm_show_menu "Project CBM Machines" "$prompt" "${machine_items[@]}"

  case "$PCBM_STATUS" in
    0)
      case "$PCBM_CHOICE" in
        C64|C64SC|SCPU64|C64DTV|C128|C12880|CBM2|CBM5|VIC20|PET|PLUS4)
          emu=$(pcbm_machine_tag_to_emu "$PCBM_CHOICE")
          pcbm_launch_machine "$emu"

          if [ "$(tty)" = "/dev/tty1" ]; then
            /usr/local/bin/pcbm-cover
            reset
            clear
          fi
          ;;
        DEFAULT)
          while true; do
            prompt="Current default machine: $(pcbm_default_machine_label)\n\nPlease select the machine Project CBM should start by default."
            pcbm_show_menu "Set Default Machine" "$prompt" "${default_items[@]}"
            case "$PCBM_STATUS" in
              0)
                case "$PCBM_CHOICE" in
                  RETURN) break ;;
                  C64|C64SC|SCPU64|C64DTV|C128|C12880|CBM2|CBM5|VIC20|PET|PLUS4)
                    emu=$(pcbm_machine_tag_to_emu "$PCBM_CHOICE")
                    if pcbm_save_default_machine "$emu"; then
                      pcbm_show_msg "Default Machine Saved" "Project CBM will now default to:\n$(pcbm_default_machine_label)"
                    fi
                    break
                    ;;
                esac
                ;;
              1|255)
                break
                ;;
              *)
                break
                ;;
            esac
          done
          ;;
        RETURN)
          exit 0
          ;;
      esac
      ;;
    1|255)
      exit 0
      ;;
    *)
      exit 0
      ;;
  esac
done
```

## scripts/pcbm-menu

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-menu
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

if [ "$(tty)" = "/dev/tty1" ] && [ -z "$PCBM_SPLASH_SHOWN" ]; then
  export PCBM_SPLASH_SHOWN=1
  /usr/local/bin/pcbm-cover
  reset
  clear
fi

while true; do
  current_emu=$(pcbm_default_machine)
  current_label=$(pcbm_default_machine_label)

  main_items=(
    "RUN"      "Run the current default machine now"
    "MACHINES" "Select a Commodore machine to boot or make the default"
    "CONTENT"  "Launch games, demos, music, programs, or ROM files"
    "IMPORT"   "Import demos, games, music, or programs from USB"
    "CONTROL"  "Open network, BBS, ROM, and system settings"
    "FILES"    "Start the Midnight Commander file browser"
    "QUIT"     "Exit Project CBM and return to the shell"
    "POWER"    "Shut down Project CBM safely"
    "REBOOT"   "Restart Project CBM"
  )

  prompt="Default machine: $current_label\n\nPlease select a Project CBM option."
  pcbm_show_menu "Project CBM Main Menu" "$prompt" "${main_items[@]}"

  case "$PCBM_STATUS" in
    0)
      case "$PCBM_CHOICE" in
        RUN)
          if [[ -z "$current_emu" ]]; then
            pcbm_show_msg "Default Machine Not Set" "No default machine is currently configured.\n\nChoose MACHINES first, then set a default machine."
          else
            pcbm_launch_machine "$current_emu"

            if [ "$(tty)" = "/dev/tty1" ]; then
              /usr/local/bin/pcbm-cover
              reset
              clear
            fi
          fi
          ;;
        MACHINES) "$SCRIPT_DIR/pcbm-machines" ;;
        CONTENT)  "$SCRIPT_DIR/pcbm-content" ;;
        IMPORT)   "$SCRIPT_DIR/pcbm-import" ;;
        CONTROL)  "$SCRIPT_DIR/pcbm-control" ;;
        FILES)
          pcbm_cleanup_terminal
          mc
          ;;
        QUIT)
          pcbm_cleanup_terminal
          exit 0
          ;;
        POWER)
          if pcbm_yesno "Shutdown Project CBM" "Shut down Project CBM now?"; then
            sudo -n /usr/sbin/poweroff || pcbm_show_msg "Permission Required" "Shutdown requires passwordless sudo for /usr/sbin/poweroff."
          fi
          ;;
        REBOOT)
          if pcbm_yesno "Reboot Project CBM" "Restart Project CBM now?"; then
            sudo -n /usr/sbin/reboot || pcbm_show_msg "Permission Required" "Reboot requires passwordless sudo for /usr/sbin/reboot."
          fi
          ;;
      esac
      ;;
    1|255)
      continue
      ;;
    *)
      continue
      ;;
  esac
done
```

## scripts/pcbm-network

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-network
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

TITLE="Project CBM Network"

start_samba() {
  if sudo -n systemctl start smbd >/dev/null 2>&1; then
    pcbm_show_msg "Samba" "Samba file sharing is now running.\n\nShare name: Project CBM\nHost name: $(pcbm_hostname)\nConnect from macOS with:\nsmb://pcbm.local/Project%20CBM"
  else
    pcbm_show_msg "Permission Required" "Project CBM could not start Samba.\n\nAdd a passwordless sudo rule for /usr/bin/systemctl start smbd, or start the service manually."
  fi
}

stop_samba() {
  if sudo -n systemctl stop smbd >/dev/null 2>&1; then
    pcbm_show_msg "Samba" "Samba file sharing has been stopped."
  else
    pcbm_show_msg "Permission Required" "Project CBM could not stop Samba.\n\nAdd a passwordless sudo rule for /usr/bin/systemctl stop smbd, or stop the service manually."
  fi
}

restart_network_stack() {
  if systemctl list-unit-files dhcpcd.service >/dev/null 2>&1; then
    if sudo -n systemctl restart dhcpcd >/dev/null 2>&1; then
      pcbm_show_msg "Network" "dhcpcd has been restarted."
      return
    fi
  fi

  if systemctl list-unit-files NetworkManager.service >/dev/null 2>&1; then
    if sudo -n systemctl restart NetworkManager >/dev/null 2>&1; then
      pcbm_show_msg "Network" "NetworkManager has been restarted."
      return
    fi
  fi

  pcbm_show_msg "Network" "Project CBM could not determine which network stack to restart automatically.\n\nUse raspi-config or restart the Pi if needed."
}

while true; do
  HOST=$(pcbm_hostname)
  IP=$(pcbm_ip_address)
  GW=$(pcbm_gateway)
  DNS="$(pcbm_dns_server)"

  if [[ -n "$IP" ]]; then
    NET_STATUS="connected ($IP)"
  else
    NET_STATUS="disconnected"
  fi

  SAMBA_STATUS=$(pcbm_service_active smbd)

  PROMPT="Host name: $HOST
IP address: ${IP:-none}
Gateway: ${GW:-unknown}
DNS Server: ${DNS:-unknown}
Network: $NET_STATUS
Samba: $SAMBA_STATUS

Please select a network option."

  pcbm_show_menu "$TITLE" "$PROMPT" \
    TEST     "Test network connectivity (gateway / internet / DNS)" \
    SAMBAON  "Start Samba file sharing so Project CBM appears on your network" \
    SAMBAOFF "Stop Samba file sharing" \
    RESTART  "Restart the active network stack" \
    CONFIG   "Advanced configuration (raspi-config)" \
    RETURN   "<- Return to the control panel"

  [[ $PCBM_STATUS -ne 0 ]] && break

  case "$PCBM_CHOICE" in
    TEST)
      pcbm_infobox "Network Test" "Running connectivity tests..."
      GW=$(pcbm_gateway)

      if [[ -n "$GW" ]] && ping -c 1 -W 1 "$GW" >/dev/null 2>&1; then
        GW_RESULT="OK"
      else
        GW_RESULT="FAILED"
      fi

      if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        NET_RESULT="OK"
      else
        NET_RESULT="FAILED"
      fi

      if ping -c 1 -W 2 google.com >/dev/null 2>&1; then
        DNS_RESULT="OK"
      else
        DNS_RESULT="FAILED"
      fi

      RESULT_TEXT="Gateway (${GW:-unknown}): $GW_RESULT
Internet (8.8.8.8): $NET_RESULT
DNS (google.com): $DNS_RESULT"

      pcbm_show_msg "Network Test Results" "$RESULT_TEXT"
      ;;
    SAMBAON)
      pcbm_infobox "Samba" "Starting Samba services..."
      start_samba
      ;;
    SAMBAOFF)
      pcbm_infobox "Samba" "Stopping Samba services..."
      stop_samba
      ;;
    RESTART)
      pcbm_infobox "Network" "Restarting network services..."
      restart_network_stack
      ;;
    CONFIG)
      pcbm_cleanup_terminal
      sudo -n raspi-config || pcbm_show_msg "Permission Required" "Launching raspi-config requires passwordless sudo for /usr/bin/raspi-config."
      ;;
    RETURN)
      break
      ;;
  esac
done

pcbm_cleanup_terminal
```

## scripts/pcbm-release-prep

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-release-prep
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  Cleans runtime cruft, logs, caches, shell history, first-boot
#  markers, and zero-fills free space before imaging a Project CBM
#  SD card for release.
#
# ---------------------------------------------------------------
#  License: MIT License. See LICENSE in the project repository.
#  No warranty is provided. Use at your own risk.
# ================================================================

set -u

ASSUME_YES=0
DO_POWEROFF=0
ZERO_FILL=1

usage() {
  cat <<'EOF'
Usage: sudo pcbm-release-prep [--yes] [--poweroff] [--no-zero-fill]

Options:
  --yes           Do not ask for confirmation.
  --poweroff      Power off after cleanup and sync complete.
  --no-zero-fill  Skip free-space zero fill. Faster, but larger image compression.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --yes|-y) ASSUME_YES=1 ;;
    --poweroff) DO_POWEROFF=1 ;;
    --no-zero-fill) ZERO_FILL=0 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; usage; exit 1 ;;
  esac
done

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Project CBM release prep must be run with sudo/root." >&2
  exit 1
fi

if (( ASSUME_YES == 0 )); then
  echo "Project CBM release prep will clean logs/caches/history and zero-fill free space."
  read -r -p "Continue? [y/N] " answer
  case "$answer" in
    y|Y|yes|YES) ;;
    *) echo "Canceled."; exit 0 ;;
  esac
fi

echo "Project CBM release prep starting..."

# Stop chatty services where practical.
systemctl stop tcpser 2>/dev/null || true

# Package/cache cleanup.
apt-get clean 2>/dev/null || true
rm -rf /var/cache/apt/archives/*.deb /var/cache/apt/*.bin 2>/dev/null || true

# Journals and logs.
journalctl --rotate 2>/dev/null || true
journalctl --vacuum-time=1s 2>/dev/null || true
find /var/log -type f -exec truncate -s 0 {} \; 2>/dev/null || true

# Runtime/temp files.
rm -rf /tmp/* /tmp/.[!.]* /tmp/..?* 2>/dev/null || true
rm -rf /var/tmp/* /var/tmp/.[!.]* /var/tmp/..?* 2>/dev/null || true
rm -rf /run/user/* 2>/dev/null || true

# User caches/history/runtime markers.
for home in /root /home/pi; do
  [[ -d "$home" ]] || continue
  rm -rf "$home/.cache"/* "$home/.thumbnails"/* 2>/dev/null || true
  rm -f "$home/.bash_history" "$home/.lesshst" "$home/.wget-hsts" 2>/dev/null || true
done
rm -f /home/pi/.config/pcbm/.firstboot_done 2>/dev/null || true

# VICE/log leftovers.
rm -f /tmp/pcbm-*.log /tmp/pcbm-*.tmp /tmp/pcbm_splash_*.png /tmp/pcbm-import-debug.log /tmp/pcbm-import.log /tmp/pcbm-vice.log 2>/dev/null || true
rm -f /home/pi/.local/state/vice/vice.log 2>/dev/null || true

sync

if (( ZERO_FILL == 1 )); then
  echo "Zero-filling free space. This may end with 'No space left on device'; that is expected."
  dd if=/dev/zero of=/ZERO.fill bs=16M status=progress 2>/dev/null || true
  rm -f /ZERO.fill
  sync
fi

echo "Project CBM release prep complete. Safe to image + PiShrink."

if (( DO_POWEROFF == 1 )); then
  echo "Powering off..."
  systemctl poweroff
fi
```

## scripts/pcbm-roms

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-roms
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

ROMDIR="$PCBM_CONTENT_BASE/roms"
mkdir -p "$ROMDIR"

run_rom_import() {
  local dev
  local -a rom_files menu_items selected

  dev=$(pcbm_mount_usb_first_partition) || {
    pcbm_show_msg "USB Error" "No USB device mounted."
    return
  }

  while IFS= read -r -d '' file; do
    rom_files+=("$file")
  done < <(pcbm_filtered_find "$PCBM_USB_MOUNT" -type f \( -iname '*.bin' -o -iname '*.rom' \) | sort -z)

  menu_items=("ALL" "Select every ROM file found" "off")
  for i in "${!rom_files[@]}"; do
    menu_items+=("$i" "USB ROM: $(basename "${rom_files[$i]}")" "off")
  done

  pcbm_show_checklist "Import ROM Files" "Select ROM files to import." "${menu_items[@]}"
  (( PCBM_STATUS != 0 )) && { pcbm_unmount_usb; return; }

  read -r -a selected <<< "$(echo "$PCBM_CHOICE" | tr -d '"')"

  if printf '%s
' "${selected[@]}" | grep -qx "ALL"; then
    selected=()
    for i in "${!rom_files[@]}"; do
      selected+=("$i")
    done
  fi

  count=0
  for idx in "${selected[@]}"; do
    pcbm_copy_clean "${rom_files[$idx]}" "$ROMDIR" && ((count++))
  done

  pcbm_unmount_usb
  pcbm_show_msg "ROM Import Complete" "Project CBM copied $count ROM file(s) into:
$ROMDIR"
}

run_rom_import
```

## scripts/pcbm-screenshot

```bash
#!/bin/bash
set -u

DIR="/home/pi/screenshots"
TS="$(date +%Y%m%d-%H%M%S)"
OUT="$DIR/pcbm-$TS.png"

mkdir -p "$DIR"

MODE="${1:-menu}"

capture_fb() {
  sudo fbgrab -c 1 "$OUT" >/dev/null 2>&1
}

capture_kms() {
  sudo ffmpeg \
    -hide_banner \
    -loglevel error \
    -f kmsgrab \
    -i - \
    -frames:v 1 \
    -vf 'hwdownload,format=bgr0' \
    -y "$OUT" >/dev/null 2>&1
}

case "$MODE" in
  menu|tty|console|fb)
    capture_fb
    RESULT=$?
    ;;

  emulator|vice|kms)
    capture_kms
    RESULT=$?
    ;;

  auto)
    capture_kms
    RESULT=$?

    if [ "$RESULT" -ne 0 ]; then
      capture_fb
      RESULT=$?
    fi
    ;;

  *)
    echo "Usage:"
    echo "  pcbm-screenshot              Capture Project CBM menu / TTY1"
    echo "  pcbm-screenshot menu         Capture Project CBM menu / TTY1"
    echo "  pcbm-screenshot emulator     Try SDL/KMS emulator capture"
    echo "  pcbm-screenshot auto         Try emulator capture, then fallback to menu capture"
    echo
    echo "Saved screenshots go to: $DIR"
    exit 1
    ;;
esac

if [ "$RESULT" -eq 0 ] && [ -f "$OUT" ]; then
  echo "Screenshot saved to: $OUT"
  exit 0
else
  echo "Screenshot failed."
  rm -f "$OUT" 2>/dev/null
  exit 1
fi
```

## scripts/pcbm-start

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-start
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#

set -u

PCBM_VERSION_CONF="/etc/pcbm/version.conf"
PCBM_BOOT_MODE_CONF="/etc/pcbm/boot-mode.conf"
PCBM_DEFAULT_MACHINE_CONF="/etc/pcbm/default-machine.conf"

FIRSTBOOT_MARKER="/home/pi/.config/pcbm/.firstboot_done"

if [[ ! -f "$FIRSTBOOT_MARKER" && -x "/usr/local/bin/pcbm-firstboot-check" ]]; then
  mkdir -p "$(dirname "$FIRSTBOOT_MARKER")" 2>/dev/null || true
  /usr/local/bin/pcbm-firstboot-check || true
  touch "$FIRSTBOOT_MARKER" 2>/dev/null || true
fi

if [[ -f "$PCBM_VERSION_CONF" ]]; then
  # shellcheck source=/etc/pcbm/version.conf
  source "$PCBM_VERSION_CONF"
fi

read_conf_value() {
  local file="$1"
  local fallback="$2"

  if [[ -f "$file" ]]; then
    tr -d '\r\n' < "$file"
  else
    printf '%s\n' "$fallback"
  fi
}

BOOT_MODE="$(read_conf_value "$PCBM_BOOT_MODE_CONF" "menu")"
DEFAULT_MACHINE="$(read_conf_value "$PCBM_DEFAULT_MACHINE_CONF" "x64sc")"

case "$BOOT_MODE" in
  machine|MACHINE|Machine)
    if [[ "$(tty 2>/dev/null)" = "/dev/tty1" ]] && command -v /usr/local/bin/pcbm-cover >/dev/null 2>&1; then
      /usr/local/bin/pcbm-cover
      reset
      clear
    fi

    /usr/local/bin/pcbm-boot "$DEFAULT_MACHINE"

    # When the emulator exits, always return to the Project CBM menu.
    exec /usr/local/bin/pcbm-menu
    ;;

  menu|MENU|Menu|*)
    exec /usr/local/bin/pcbm-menu
    ;;
esac
```

## scripts/pcbm-system

```bash
#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-system
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/pcbm-dialog-lib.sh"
pcbm_trap_cleanup

system_items=(
  "CONFIG"   "Launch raspi-config for Raspberry Pi system options"
  "BOOTMODE" "Choose whether Project CBM starts at the menu or default machine"
  "SHOW"     "Show Project CBM information and credits"
  "POWER"    "Shut down Project CBM safely"
  "REBOOT"   "Restart Project CBM"
  "RELEASE"  "Run release prep before imaging"
  "RETURN"   "<- Return to the control panel"
)

show_about() {
  local ip_addr gateway active_rom boot_mode
  ip_addr=$(pcbm_ip_address)
  [[ -z "$ip_addr" ]] && ip_addr="Not connected"
  gateway=$(pcbm_gateway)
  [[ -z "$gateway" ]] && gateway="Unknown"
  active_rom=$(pcbm_active_jiffydos)
  [[ -z "$active_rom" ]] && active_rom="None"
  boot_mode=$(tr -d '\r\n' < "$PCBM_CONFIG_DIR/boot-mode.conf" 2>/dev/null || printf 'menu')

  pcbm_show_textbox "About Project CBM" "${PCBM_PROJECT_NAME:-Project CBM}
Raspberry Pi / Commodore machine distribution

Image version: ${PCBM_VERSION:-dev}
Menu system: ${PCBM_MENU_VERSION:-6.5}
Build: ${PCBM_BUILD:-local}
Author: ${PCBM_AUTHOR:-Craig Daters}
Repository: ${PCBM_REPO:-not set}

Host name: $(pcbm_hostname)
IP address: $ip_addr
Gateway: $gateway
Default machine: $(pcbm_default_machine_label)
Boot mode: $boot_mode
Active custom ROM: $(basename "$active_rom" 2>/dev/null || printf '%s' "$active_rom")

${PCBM_TAGLINE:-Power on. Boot fast. No nonsense. Just Commodore.}

Core ideas:
- Launch classic Commodore machines quickly
- Keep common setup tasks inside dialog-based menus
- Make USB import, file browsing, and service control approachable for normal humans
- Auto-handle HDMI audio selection before VICE launch
- Keep menu-first boot as the default while allowing optional direct-machine startup

Credits:
- Project concept, design direction, and retro-computing curation by Craig Daters
- VICE Team, for the Versatile Commodore Emulator
- Raspberry Pi Foundation and Raspberry Pi OS developers
- Original Commodore engineers and developers
- The wider retro-computing and open source communities

Project CBM does not include or distribute copyrighted ROMs, commercial software, disk images, demos, or game collections."
}

while true; do
  boot_mode=$(tr -d '\r\n' < "$PCBM_CONFIG_DIR/boot-mode.conf" 2>/dev/null || printf 'menu')
  prompt="System settings and Project CBM information.\n\nDefault machine: $(pcbm_default_machine_label)\nBoot mode: $boot_mode"
  pcbm_show_menu "Project CBM System" "$prompt" "${system_items[@]}"

  case "$PCBM_STATUS" in
    0)
      case "$PCBM_CHOICE" in
        CONFIG)
          pcbm_cleanup_terminal
          sudo -n raspi-config || pcbm_show_msg "Permission Required" "Launching raspi-config requires passwordless sudo for /usr/bin/raspi-config."
          ;;
        BOOTMODE)
          "$SCRIPT_DIR/pcbm-bootmode"
          ;;
        SHOW)
          show_about
          ;;
        POWER)
          if pcbm_yesno "Shutdown Project CBM" "Shut down Project CBM now?"; then
            sudo -n /usr/sbin/poweroff || pcbm_show_msg "Permission Required" "Shutdown requires passwordless sudo for /usr/sbin/poweroff."
          fi
          ;;
        REBOOT)
          if pcbm_yesno "Reboot Project CBM" "Restart Project CBM now?"; then
            sudo -n /usr/sbin/reboot || pcbm_show_msg "Permission Required" "Reboot requires passwordless sudo for /usr/sbin/reboot."
          fi
          ;;
        RELEASE)
          if pcbm_yesno "Release Prep" "Run Project CBM release prep now?\n\nThis clears logs/caches/runtime files and zero-fills free space. Use this only when preparing an SD-card image."; then
            pcbm_cleanup_terminal
            sudo -n /usr/local/bin/pcbm-release-prep --yes || pcbm_show_msg "Permission Required" "Release prep requires passwordless sudo for /usr/local/bin/pcbm-release-prep or must be run manually with sudo."
          fi
          ;;
        RETURN)
          exit 0
          ;;
      esac
      ;;
    1|255)
      exit 0
      ;;
    *)
      exit 0
      ;;
  esac
done
```

---

# Appendix D - Cover Naming Reference

## Generic Random Covers

```text
pcbmcover0.jpg
pcbmcover1.jpg
pcbmcover2.jpg
pcbmcover3.jpg
pcbmcover4.jpg
```

## Machine Family Covers

```text
pcbmcover-c64.jpg
pcbmcover-c128.jpg
pcbmcover-vic20.jpg
pcbmcover-pet.jpg
pcbmcover-plus4.jpg
pcbmcover-cbm2.jpg
pcbmcover-cbm5.jpg
```

---

# Appendix E - Release Workflow Summary

```bash
sudo pcbm-release-prep --yes --poweroff
# image SD card on macOS or Linux
# run PiShrink with -a -z, not -s
sha256sum Project-CBM-v1.0.0.img.gz > Project-CBM-v1.0.0.img.gz.sha256
```

---

# Appendix F - Troubleshooting Ledger

## Duplicate Finder entries

Cause:

- NetBIOS browsing plus other network discovery can create duplicate-looking entries.

Fix:

```text
disable netbios = yes
smb ports = 445
```

Then restart only `smbd`:

```bash
sudo systemctl restart smbd
```

## `pcbm.local` not resolving

Fix:

```bash
sudo systemctl enable avahi-daemon
sudo systemctl restart avahi-daemon
hostname
```

Connect directly:

```text
smb://pcbm.local/Project%20CBM
```

## Splash not machine-specific

Confirm the family cover file exists:

```text
/opt/pcbm/covers/pcbmcover-c64.jpg
/opt/pcbm/covers/pcbmcover-c128.jpg
```

Confirm `pcbm_emu_to_cover_tag()` exists in `pcbm-dialog-lib.sh`.

## Double splash at startup

Confirm `pcbm-menu` exports:

```bash
PCBM_SPLASH_SHOWN=1
```

## Importer recursive folder behavior

Expected behavior:

- SPACE selects files/folders.
- ENTER/OK processes selection.
- One selected folder gives Browse / Import / Cancel.
- Import preserves substructure recursively.
- macOS metadata junk is filtered.

## RELEASE menu item does nothing

Use the corrected v6.5 `pcbm-system`. The `RELEASE)` case must call:

```bash
sudo -n /usr/local/bin/pcbm-release-prep --yes
```

## First-boot check runs every boot

Use the corrected v6.5 `pcbm-start`. The marker belongs here:

```text
/home/pi/.config/pcbm/.firstboot_done
```
