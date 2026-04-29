# Project CBM Menu

Private source repository for the Project CBM menu system, helper scripts, configuration examples, splash cover assets, build notes, release workflow documentation, and bundle packaging tools.

Public Project CBM release repo:

```text
https://github.com/cdaters/project-cbm
```

Private menu/build repo:

```text
https://github.com/cdaters/project-cbm-menu
```

## Repository purpose

This repo is the private builder-side source repo for the Project CBM menu system.

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
- [Menu Repo Setup](docs/MENU-REPO-SETUP.md)

## Legal/distribution note

Project CBM does not include or distribute copyrighted Commodore ROMs, commercial software, disk images, demos, or game collections. Users are responsible for supplying their own legally obtained content.
