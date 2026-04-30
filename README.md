![Platform](https://img.shields.io/badge/platform-raspberry%20pi-C51A4A)
[![Project CBM Release](https://img.shields.io/github/v/release/cdaters/project-cbm?label=project-cbm%20release)](https://github.com/cdaters/project-cbm/releases/latest)
[![Menu Release](https://img.shields.io/github/v/release/cdaters/project-cbm-menu?label=menu%20release)](https://github.com/cdaters/project-cbm-menu/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-orange)](LICENSE.md)
![GitHub last commit](https://img.shields.io/github/last-commit/cdaters/project-cbm-menu)
![GitHub Issues](https://img.shields.io/github/issues/cdaters/project-cbm-menu)

# Project CBM Menu

Source repository for the Project CBM menu system, helper scripts, configuration examples, splash cover assets, build notes, release workflow documentation, and bundle packaging tools.

Public Project CBM release repo:

```text
https://github.com/cdaters/project-cbm
```

Menu/build source repo:

```text
https://github.com/cdaters/project-cbm-menu
```

## Repository purpose

This repo is the source repository for the Project CBM menu system.

It contains:

- Project CBM menu scripts
- System/control panel scripts
- Import, content, ROM, network, audio, BBS/TCPser, and boot-mode helpers
- Samba, TCPser, VICE, boot, and sudo config examples
- Splash screen cover assets
- Build notes and documentation
- Public image release workflow documentation
- Bundle packaging scripts

The public `project-cbm` repo remains the user-facing home for SD card image releases, public documentation, checksums, release notes, screenshots, and the public roadmap.

## Relationship to Project CBM

This repository contains the source and packaging workflow for the Project CBM menu system. The user-facing Project CBM image, releases, screenshots, checksums, end-user documentation, and acknowledgements live in the main `project-cbm` repository.

Project CBM exists in appreciation of the path [Carmelo Maiolino's Combian64](https://cmaiolino.wordpress.com/combian-64-v2/) helped establish, but it is not a fork of Combian64 and is not affiliated with or endorsed by Combian64 or Carmelo Maiolino.

## Version model

```text
Project CBM public image/build version: 1.0.0
Project CBM menu system version:       1.0.0
Legacy internal menu lineage:          v6.5
```

`v6.5` is preserved as the historical internal build-notes lineage used during development of the Project CBM v1.0.0 public image.

The first formal repository release of this menu system is:

```text
Project CBM Menu v1.0.0
```

## Build a menu bundle

```bash
make bundle
```

or:

```bash
./packaging/build-menu-bundle.sh
```

The output lands in:

```text
dist/
```

Expected v1.0.0 output:

```text
dist/Project-CBM-v1.0.0-Bundle.zip
```

## Install onto a source Pi

From an extracted bundle or repo checkout on the Pi:

```bash
sudo ./packaging/install-menu-bundle.sh
```

Review the main build notes before using this on a release image:

```text
docs/Project CBM Menu v1.0.0 Build Notes and Documentation.md
```

## Documentation Map

- [Project CBM Menu v1.0.0 Build Notes and Documentation](docs/Project%20CBM%20Menu%20v1.0.0%20Build%20Notes%20and%20Documentation.md)
- [Public Image Release Workflow](docs/PUBLIC-IMAGE-RELEASE-WORKFLOW.md)
- [Audit Notes](docs/AUDIT-NOTES.md)
- [Versioning Notes](docs/VERSIONING.md)

## Legal/distribution note

Project CBM does not include or distribute copyrighted Commodore ROMs, commercial software, disk images, demos, or game collections. Users are responsible for supplying their own legally obtained content.

## Public end-user documentation

The `public-docs/` folder contains the end-user documentation that is mirrored into the public `project-cbm` repository and packaged as the offline public docs ZIP.

Build the public documentation package:

```bash
make public-docs
```

Build both the menu bundle and public docs package:

```bash
make release-kit
```

Expected outputs:

```text
dist/Project-CBM-v1.0.0-Bundle.zip
dist/pcbm-v1.0.0-docs.zip
```

To preview syncing the public docs into the public repo:

```bash
./packaging/sync-public-docs.sh ../project-cbm --dry-run
```

To apply the sync:

```bash
./packaging/sync-public-docs.sh ../project-cbm --apply
```
