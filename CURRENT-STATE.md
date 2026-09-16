# Project CBM Menu current state

## Active private POC packaging — 2026-09-15

Owner approved package implementation after the product Lima/VZ capability gate.
Work is on feature/1.1-debian-package. VERSION is 1.1.0_poc1 for a private candidate;
PUBLIC_VERSION remains the published 1.0.0. New Debian packaging installs reviewed
scripts under /usr/bin with necessary absolute-path relocation. It excludes release
prep, experimental screenshot and art pending rights review. No product release,
service/sudo changes or physical qualification. See [package contract](docs/DEBIAN-PACKAGE.md).
The private Debian package built and its installed payload passed the product's
read-only image validation. Package: project-cbm-menu 1.1.0~poc1-1+pcbm1 (all), SHA-256
`3f7557cdbdd44922954a6e640a1bcb3a96f446f6dbe6631afe667aa5e5d5f0fd`.
Local tag v1.1.0_poc1 object `e265f3cbb995ad0a9a7748987b2d9c88019aa787` peels to
`77a708019c9d8a11e657d7e5d2dde7b7ecb340ba`. The tag remains at package source;
this later continuity update does not change the frozen package/input identity.
[Product POC checkpoint](../project-cbm/docs/build/private-poc1.md) owns image/lock
hashes and results. Runtime on a Raspberry Pi remains untested. STOP for owner review;
no further Menu work, physical testing or publication is authorized automatically.
All existing formal/recovery tags and main remain unchanged. Historical checkpoints
below describe their original dates and unchanged immutable release baselines.


Updated 2026-09-15: owner accepted cold-start comprehension; final architecture
reconciliation complete. The owner-authorized privacy repair replaces only four
unpublished Menu commits, preserving exact trees/messages/dates. Replacement refs
and all architecture work are externally bundled and restored offline. Publication
is complete for both main branches and Menu recovery/maintenance refs. Product
maintenance/1.0 is intentionally local/bundled after GH007 on historical metadata;
public product v1.0.0 is its authoritative maintenance baseline. No runtime edits
or image. See the
[product privacy record](../project-cbm/docs/privacy-reconciliation-2026-09-15.md).

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
- Annotated recovered/image-v1.0.0-runtime -> `a4148db54001790eaddb4e31104917c16149b181`.
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

## Final foundation and recovery scope

The [product recovery contract](../project-cbm/docs/recovery.md) is now a required
1.1 architectural input. Full recovery belongs to repositories and retained build/
release infrastructure. Only minimal installed identity is projected from the frozen
lock into the appliance; complete recipes, locks, inventories and recovery archives
remain external. Retain portable roots, source/package/environment closure, external
qualification binding and independent backups.
Proposed pcbm-info and generated identity are product integration work; Menu consumes
that authority rather than maintaining another version source. No implementation.

An actual offline restore of accepted preservation bundles verified all 5 product
refs, 8 Menu refs and all 17 recovered script hashes. The new design checkpoint is
retained separately at ProjectCBM-Work/archive/black-box-design-2026-09-15; original
preservation/historical evidence is untouched. Independent off-site copy, schema/
metadata generator, Linux host/bootstrap and all image/hardware recovery tests remain
open. Read AGENTS/current state/recovery first in the next newly authorized session.


[Product ADR-0001](../project-cbm/docs/adr/0001-base-distribution-and-image-architecture.md)
accepts Raspberry Pi OS Lite + pinned arm64 pi-gen, writable ext4, logical user-data
separation and external Debian package builds. Menu owns its future independent
package/interface; no package is built here. Content default stays `/home/pi/pcbm`.
There is no mandated 8 GB minimum; measure footprint and remaining user capacity.
Separate USERDATA/immutable roots and elaborate hooks/updaters are deferred.

Current product guidance corrects historical content, TCPser, Samba credentials and
hardware claims. The `public-docs/` mirror and historical source/build documents
remain unchanged; [product current notes](../project-cbm/docs/v1.0-current-notes.md)
take precedence. Milestone 1 is now authorized in the product repository, with a
mandatory owner checkpoint before Linux host provisioning. Resume product branch
creation/contracts/host study after synchronization; no Menu feature branch is needed
until actual Menu work is required. The privacy-repair task stops after publication
and final recovery validation.

Historical architecture phase input HEAD (pre-rewrite IDs): `c3746a12e6146f880c49979df8da2a3567200924`; product input
`7f9c4a363cf19154a9637ed8b251049bf23723e0`. Only AGENTS, CURRENT-STATE and README
change in this repository. Validation is in the [product phase record](../project-cbm/docs/architecture-phase-validation.md).
All runtime/config/packaging/CI/assets and existing tags remain unchanged.
