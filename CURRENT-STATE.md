# Project CBM Menu current state

Updated 2026-09-15: preservation/reconciliation/continuity complete, local commits
and refs externally bundled; no push, runtime edits, image build or new release.

- Independently versioned component of [Project CBM](../project-cbm/CURRENT-STATE.md).
  Formal VERSION/PUBLIC_VERSION remain 1.0.0; no version bump is part of this work.
- Formal v1.0.0: tag object `0756331cf872dfeaec17bdb75939f84e47e04f9f`, peeled
  `399c6158caa8ed2762744d512c1841b94ad64403`. Do not rewrite it.
- Main fast-forwarded from `f185d916959a7bd6ed4d561e0c66e7f42f1efb28` to verified
  GitHub `b7e4d858ce54e6623b6264b930e841e03fad1a19`, then local continuity commits.
  Its 18 scripts/configs/packaging are unchanged from the formal release.
- Product 1.0.0 is already arm64 Raspberry Pi OS Lite / Debian 13.4 Trixie,
  2026-04-21 base, vendor 6.12.75 kernels, source-built VICE 3.10 SDL2/ALSA.
- Shipped runtime has 17 scripts: 12 formal-tag matches, five differences, no
  experimental pcbm-screenshot. No pre-existing commit exactly represents it.
- Annotated recovered/image-v1.0.0-runtime -> `1cd5e0d378a4066f239c92a30aafdd97cb415dcf`.
  This new root commit holds byte-exact extracted scripts, not normalized v6.5,
  reconstructed source or a configuration snapshot. Its RECOVERY.md records scope.
- maintenance/1.0 starts at that recovery, not formal v1.0.0. It is not an installable
  package. Important/security fixes only, with deliberate packaging/config review
  and product qualification. No 1.0.1, Bookworm line or historical tag change.
- v6.5/GoldMaster/for65 establish lineage/source equivalence, not byte identity or
  exact surrounding installed configuration. See [provenance](docs/provenance.md).
- Known issues: broad sudo; fragile USB import/status/audio/launch behavior;
  installer resets config; docs-sync dry run writes and apply can delete pages;
  broken version display; CI still packages 6.5/watches menu-v*. All remain unfixed.
- Target Pi 3 through Pi 500+, Pi 3 performance floor, all physical qualification
  still open. Per-script syntax/integrity passed; no Pi/service/runtime tests.
- Next: explicitly authorized product 1.1 reproducible-build POC, consuming a
  pinned reviewed Menu candidate/tag/peeled commit/package hash. Read the
  [product handoff](../project-cbm/docs/build-and-release.md#new-session-first-task).
  No Menu candidate/package was newly built here; do not use arbitrary main.
- Original history: /Volumes/TheBench/Projects/Project CBM, untouched. Bulk new
  work/archive: /Volumes/TheBench/ProjectCBM-Work. No large artifacts in Git.
  TheBench is APFS; Linux build environment and second encrypted backup are open.

## First-class black-box recovery design

The [product recovery contract](../project-cbm/docs/recovery.md) is now a required
1.1 architectural input. It defines offline self-description from the same frozen
lock, independent component identities, portable source/storage roots, retained
source/package/environment closure, qualification binding and independent backups.
Proposed pcbm-info and generated identity are product integration work; Menu consumes
that authority rather than maintaining another version source. No implementation.

An actual offline restore of accepted preservation bundles verified all 5 product
refs, 8 Menu refs and all 17 recovered script hashes. The new design checkpoint is
retained separately at ProjectCBM-Work/archive/black-box-design-2026-09-15; original
preservation/historical evidence is untouched. Independent off-site copy, schema/
metadata generator, Linux host/bootstrap and all image/hardware recovery tests remain
open. Read AGENTS/current state/recovery first in the next newly authorized session.
