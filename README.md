[![Project CBM 1.1.0](https://img.shields.io/badge/Project%20CBM-1.1.0-blue)](https://github.com/cdaters/project-cbm/releases/tag/v1.1.0) [![Menu source 1.1.0](https://img.shields.io/badge/Menu%20source-1.1.0-blue)](https://github.com/cdaters/project-cbm-menu/tree/v1.1.0) [![Code license: MIT](https://img.shields.io/badge/code%20license-MIT-orange)](LICENSE)

# Project CBM Menu

This is the source repository for the keyboard-operated Bash/dialog front panel
used by **Project CBM 1.1.0**. Menu owns navigation, presentation, machine Covers,
interface contracts and its independently versioned Debian package. The main
[Project CBM repository](https://github.com/cdaters/project-cbm) owns OS/runtime
integration, image construction, qualification and authoritative user documentation.

## Download Project CBM

**Normal users should download the complete [Project CBM 1.1.0 image](https://github.com/cdaters/project-cbm/releases/tag/v1.1.0).**
This Menu source checkout is not a bootable image or a standalone replacement for
the installed appliance. Start with the Product [Getting Started guide](https://github.com/cdaters/project-cbm/blob/feature/1.1-build-foundation/docs/release/getting-started.md)
and [documentation index](https://github.com/cdaters/project-cbm/blob/feature/1.1-build-foundation/docs/README.md).

## Current Menu Identity

- Source version: **1.1.0**; annotated tag [`v1.1.0`](https://github.com/cdaters/project-cbm-menu/tree/v1.1.0).
- Tagged source commit: `7df45cf40eae1ca64cd5740e4b93347e3717bdb4`.
- Package shipped in Project CBM 1.1.0: `project-cbm-menu_1.1.0-1+pcbm1_all.deb`.
- Product and Menu versions are independent; the Product release records the exact
  Menu source and package identity. There is no separate Menu 1.1.0 GitHub Release.

The existing tag remains the released source snapshot. Later documentation commits
on `feature/1.1-debian-package` do not change the package inside the 1.1.0 image.
That branch is the active public development/documentation branch; `main` is retained
as historical repository history.

## Developer Starting Points

| Area | Location |
| --- | --- |
| Menu actions and shared launcher | `scripts/pcbm-*` |
| Dialog/result helpers and validated bridges | `lib/` |
| Debian package definition | `debian/` |
| Focused behavior and interface tests | `tests/` |
| Artwork and provenance | [Cover manifest](docs/cover-artwork.json), [primary artwork](docs/primary-artwork.json), [provenance](docs/provenance.md) |
| Engineering checkpoint | [CURRENT-STATE](CURRENT-STATE.md) |

Use the Product [developer guide](https://github.com/cdaters/project-cbm/blob/feature/1.1-build-foundation/docs/release/development.md)
and [build guide](https://github.com/cdaters/project-cbm/blob/feature/1.1-build-foundation/docs/release/build-your-own.md)
for the supported native arm64 Debian/Lima factory and exact dependency workflow.
Menu packaging uses the repository's Debian metadata, not the old ZIP installer.
A Menu build alone does not produce or qualify a Project CBM image.

[Versioning](docs/VERSIONING.md) and [UI contract](docs/UI-CONTRACT.md) retain the
independent-version and structured-result interfaces. Their dated development
notes are historical; current installed behavior is documented by Product.
Do not use the historical installer or docs-sync tooling to update a released image.
The `public-docs/` directory is an archived packaging mirror, not the current manual.

## Future Work

The accepted [content-ingestion / Online Library design](https://github.com/cdaters/project-cbm/blob/feature/1.1-build-foundation/docs/design/content-ingestion-online-library.md)
targets provisional Product **1.2.0**. USB preview/selection under CONTENT,
read-only USB browsing and Assembly64 Online Library are **not implemented**.
No Menu behavior or version changes are part of this documentation cleanup.

## License and Upstream Software

Project-owned code uses [MIT](LICENSE). Artwork and third-party material have
separate provenance and conditions; see the Product
[release policy](https://github.com/cdaters/project-cbm/blob/feature/1.1-build-foundation/docs/release/release-policy.md).
The code license is not a blanket redistribution grant for every asset or title.

## History / Maintainer Records

- [Historical 1.0.0 build notes](docs/Project%20CBM%20Menu%20v1.0.0%20Build%20Notes%20and%20Documentation.md).
- [Early Debian packaging checkpoint](docs/DEBIAN-PACKAGE.md).
- [Historical public-image workflow](docs/PUBLIC-IMAGE-RELEASE-WORKFLOW.md) and [audit notes](docs/AUDIT-NOTES.md).
- [Product history and corrections](https://github.com/cdaters/project-cbm/blob/feature/1.1-build-foundation/docs/v1.0-current-notes.md).

The internal v6.5 lineage and first formal Menu v1.0.0 release remain historical
records. They do not identify the current Project CBM image. Project CBM acknowledges
Combian64's inspiration without being its fork or claiming affiliation; see the
Product [acknowledgements](https://github.com/cdaters/project-cbm/blob/feature/1.1-build-foundation/ACKNOWLEDGEMENTS.md).
