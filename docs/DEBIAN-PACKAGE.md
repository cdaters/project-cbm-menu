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
