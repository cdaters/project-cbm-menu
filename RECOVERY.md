# Recovered Project CBM image v1.0.0 runtime

Created 2026-09-15 as a forensic recovery, not a historical source release.
This root commit deliberately has no parent: available Git history does not
contain the exact shipped runtime, and no historical Git ancestry is asserted.

The 17 files in scripts/ are BYTE-EXACT extracts of /usr/local/bin/pcbm-* from
the published image. No normalization, reconstruction, fixes, or added runtime
scripts were applied. Git records executable mode; original uid/gid/modes and
SHA-256 values are in runtime-manifest.json. Git cannot preserve inode metadata.

Published compressed image SHA-256:
0bb17d7c72d2de7f8e70f77f001683547ae3cf2db6f832f3d2727d971cd47ec9
Published decompressed image SHA-256:
168a3026eca2bc328e03e47dfbb0cbe17740180504ad7858496df84982e89849
Historical raw image SHA-256:
845d99d1ea20aca85c0739e5fa1bf8a9d2046bcb5f9d302576ef74bb39cdc9fe

Both images were opened read-only with dissect.extfs 3.15/dissect.volume 3.18.
All 17 script bytes match between images and the original audit extraction.
Historical v6.5 loose/archive, GoldMaster and scriptsForChat/for65 material
supports the source lineage; those are not byte-identical runtime snapshots.
The accepted audit establishes v6.5 executable-source equivalence. Simple
whitespace/comment comparison is corroboration, not a general semantic proof.
Surrounding v6.5 configuration is not an installed-system snapshot.

Formal Menu v1.0.0 is unchanged: tag object
0756331cf872dfeaec17bdb75939f84e47e04f9f, peeled commit
399c6158caa8ed2762744d512c1841b94ad64403. Twelve shipped scripts match;
pcbm-control, pcbm-system, pcbm-network, pcbm-start and pcbm-release-prep differ.
The formal source additionally contains experimental pcbm-screenshot.

This recovery is scripts only. It is NOT an installable bundle, full image,
configuration snapshot, safe release candidate, or replacement for v1.0.0.
LICENSE records the owner's original-script MIT grant; no third-party media,
image contents, keys, credentials, shell history, or configuration are imported.
The current main branch's docs/provenance.md explains the maintenance policy.
maintenance/1.0 starts here for deliberate important/security fixes only; new
packaging/configuration must be separately reviewed before any maintenance build.

Evidence stays in /Volumes/TheBench/Projects/Project CBM (do not modify) and
/Volumes/TheBench/ProjectCBM-Work/archive/preservation-2026-09-15/reconciliation.
Use main's AGENTS.md and CURRENT-STATE.md before further development. Never run
these historical scripts on the Mac or casually broaden sudo/network/boot policy.
