# Current Menu package and historical packaging notes

Project CBM 1.1.0 ships Menu source **1.1.0**, tag `v1.1.0` at
`7df45cf40eae1ca64cd5740e4b93347e3717bdb4`, package **1.1.0-1+pcbm1**.
Current package inputs are `debian/`, `scripts/`, `lib/` and the reviewed artwork
specified by the package recipe. Use the Product
[build guide](https://github.com/cdaters/project-cbm/blob/feature/1.1-build-foundation/docs/release/build-your-own.md)
for the native arm64 factory and full integration. A standalone Menu package does
not establish Product image qualification. Do not run the historical ZIP installer
as an appliance upgrade.

## Historical initial packaging checkpoint

The early exclusions and untested status below describe that initial checkpoint,
not the released 1.1.0 package. They are retained as engineering history.

# Private POC Debian package

Version 1.1.0_poc1 / Debian 1.1.0~poc1-1+pcbm1; local candidate tag only,
not a published product/Menu release. Source baseline is the formal v1.0.0 script
lineage retained on main, not the byte-exact forensic runtime. Product provenance
already records the five differing scripts and extra screenshot helper.

Packaging owns /usr/bin/pcbm-* scripts and Debian metadata only. Explicit path
relocation from /usr/local/bin to /usr/bin is necessary for versioned installation;
cover lookup moves to /usr/share/project-cbm-menu/covers. No broad runtime fixes.
The package excludes pcbm-release-prep (development tool), pcbm-screenshot
(experimental), installer/config examples and cover art pending rights review.
The absent optional cover directory is already handled as a no-op by pcbm-cover.
Product integration supplies configuration, VICE, accounts, first boot and services.
No conffiles or maintainer scripts, no service enablement or sudo policy installation.
Existing controls requiring unavailable privileges remain unqualified in the POC.

Build with standard dpkg-buildpackage in the approved native arm64 Debian host;
output architecture is all. Retain source .dsc/orig/debian archives, .buildinfo,
.changes and .deb, exact tool dependencies and the tag/peeled commit/source hash.
No development helper/installer is executed. bash -n checks syntax only; console,
VICE-return, audio and physical Pi behavior remain untested until qualification.
