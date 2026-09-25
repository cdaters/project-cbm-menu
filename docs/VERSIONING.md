# Current version identities

Project CBM image **1.1.0** consumes Menu source **1.1.0** and Debian package
**1.1.0-1+pcbm1**. Product and Menu versions remain independent. The existing
annotated `v1.1.0` tags identify their frozen release source; later documentation
commits do not move those tags or rebuild released packages. Product owns the exact
image/package mapping. See the [current repository overview](../README.md).

## Historical versioning introduction

The first-release identities below are retained as history, not current-version claims.

# Project CBM Versioning

> Historical source-release documentation. See [reconciliation](provenance.md):
> formal Menu v1.0.0 differs from the image runtime. Product owns image builds
> and release mapping. Do not execute legacy installer/docs-sync/release-prep
> during recovery; no 1.1 builder or release is authorized by this document.

Project CBM uses two version tracks:

```text
PCBM_VERSION      = public SD-card image/build version
PCBM_MENU_VERSION = menu system version
```

For the first public image:

```text
Project CBM image: v1.0.0
Project CBM menu:  v1.0.0
```

This lets the menu system evolve without forcing a public image release every time a script or build-note detail changes.

## Future dependency contract

Menu versions are independent of product versions. Every product candidate must
record the explicit Menu version/tag, peeled full commit and artifact SHA-256.
Never consume arbitrary main. The original image did not contain PCBM_MENU_VERSION;
its runtime is identified by the recovery tag and manifest, not retroactive metadata.
See [product contract](../../project-cbm/docs/build-and-release.md).
