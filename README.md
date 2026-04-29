# Project CBM Menu

Private source repository for the Project CBM menu system, helper scripts, configuration examples, cover assets, and build notes.

Public release repo:

```text
https://github.com/cdaters/project-cbm
```

Private menu/build repo:

```text
https://github.com/cdaters/project-cbm-menu
```

## Version model

```text
Project CBM public image/build version: 1.0.0
Project CBM menu system version:       6.5
```

## Build a menu bundle

```bash
make bundle
```

or:

```bash
./packaging/build-menu-bundle.sh
```

The output lands in `dist/`.

## Install onto a source Pi

From an extracted bundle or repo checkout on the Pi:

```bash
sudo ./packaging/install-menu-bundle.sh
```

Review `docs/Project CBM v6.5 Build Notes and Documentation.md` before using this on a release image.

## Legal/distribution note

Project CBM does not include or distribute copyrighted Commodore ROMs, commercial software, disk images, demos, or game collections. Users are responsible for supplying their own legally obtained content.
