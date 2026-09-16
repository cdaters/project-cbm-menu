# First-boot/runtime activation — 2026-09-16 / IN PROGRESS

Owner authorized one new private engineering candidate using the accepted architecture.
Source now adds a short local first-run UI, active boot preference messaging, Wi-Fi
selection, the constrained USB broker client, authenticated owner Terminal and the
safe refusal of generic SID autostart. Runtime API 1 is a versioned Debian dependency.
Product owns root operations/accounts/service policy and exact optional media admission.
No framework redesign, public release, push or physical test. POC1–3 remain untouched.

Menu source version is 1.1.0_poc4; it is not yet a frozen/tagged candidate input.
50 Menu tests plus launcher checks and 135 product tests pass at this source checkpoint.
Native integration and matching package/image construction are still in progress.
See [product progress and staging evidence](../project-cbm/docs/build/runtime-activation.md).
Do not treat fixture passes or this source version as a hardware-qualified image.

Earlier completed checkpoints below retain their original scope and conclusions.

# Configuration maturation complete — 2026-09-16 / STOP

## Optional C64 application content routing — 2026-09-16 / STOP

Owner authorized SID-Wizard/StrikeTerm integration following configuration maturation.
CONTENT now consumes `pcbm-profiles content-profile FILE` from the product runtime:
Music/Creation/SID-Wizard and Programs/Communications/StrikeTerm use the registry's
validated x64sc with a regular standard D64; ordinary content retains the user's
default. No preference write, new main-menu item, one-off launcher, sudo or downloader.
Shared VICE launcher/F10/geometry/session/audio/diagnostics remain unchanged.

Product admits only the verified SID-Wizard 1.97 native one-SID core for a later
frozen candidate. StrikeTerm and the requested third-party SID/demo set remain
owner-supplied. See [application guide](../project-cbm/docs/runtime/optional-applications.md)
and [exact contract](../project-cbm/docs/runtime/optional-applications-contract.md).
Matching product/Menu packages and normal runtime activation remain pending; no POC4,
package/image build, new hardware qualification, service enablement or publication.

44 Menu tests plus launcher checker and 120 product tests pass; the new content UI
fixture covers profile routing, filenames with spaces, rejection and return. These
are source tests, not application playback qualification. All prior POC evidence and
tags remain unchanged. Checkpoint: configured bulk workspace
`archive/optional-content-2026-09-16`, both bundles and exact refs restored offline.
Next owner review is product first-boot/owner-account/runtime integration, not another
Menu architecture study. Branch remains feature/1.1-debian-package; no push authorized.

The owner-authorized final configuration architecture pass is source-complete.
[Menu entry guide](docs/CONFIGURATION.md) links the product user, developer and
activation contracts. CONTROL now invokes the coherent Bash/dialog pcbm-config;
System Information/About consume pcbm-info JSON. Registry/preferences remain the
machine authority. Audio settings are data-only/atomic; geometry/launcher are unchanged.

Normal user operations use preferences or fixed JSON requests to the product backend.
Advanced Terminal is an unprivileged child shell; exit returns. Owner administration
and raspi-config require a separately initialized owner account and authenticated sudo.
No universal password or arbitrary passwordless command. Dead QUIT, competing legacy
startup/status/version logic and unsafe generic USB mount paths are retired; old entry
names redirect to the current UI or explain pending safe import.

Runtime/package installation, first-boot/account setup and individual network/service
readiness remain pending. Boot intent needs its consumer, TCPser typed settings need
its fixed launch adapter and USB import needs the constrained broker specified in the
product contract. Nothing is installed/activated on POC3 and no POC4 is built.

43 Menu tests and the included launcher checker, 108 product tests, Bash/Python/JSON/
link/privacy/size/ref checks and sudoers syntax pass. Mac fixture cost is recorded;
no real dialog/Linux installation, Pi performance or new hardware qualification.
No package version/tag changes, image/package build, VM start, push or publication.

Menu stays feature/1.1-debian-package; product stays feature/1.1-build-foundation.
The new source checkpoint archive/configuration-maturation-2026-09-16 beneath configured
external bulk storage retains exact output commits, both bundles, all refs and verified
offline restoration. POC1–3 and prior checkpoints/tags remain unchanged. Independent
backup is unresolved. Future consumption requires newly versioned exact Menu/product
packages, not changed bytes under an existing package identity or arbitrary main.

**Next product milestone:** owner-approved first-boot/owner-account and runtime activation
integration with Linux staging tests. Complete backend readiness/storage/modem/boot
consumers before an explicitly approved candidate. Do not recommend another Menu
architecture pass absent a real blocker. Boot optimization and optional software remain
later product work; no automatic build, service enablement or hardware test.

Earlier sections below record completed historical checkpoints, not the present task.

---

# Information and machine consumers complete — 2026-09-16 / STOP

The owner-authorized source slice adds CONTROL → INFO (System Information), consuming
pcbm-info JSON without hardware/version probes. MACHINES lists profiles/current state
from the product registry, saves a user-owned default without sudo and returns directly
to Main Menu. RUN/cover/content/no-argument boot helper share validated product selection.
Missing new preferences import recognized legacy state once; valid new data wins;
malformed data is retained until explicit backed-up recovery. Boot preference is inactive.

Read [user/developer navigation](docs/INFORMATION-MACHINES.md) and the product
[checkpoint](../project-cbm/docs/runtime/information-machines-slice.md). Product owns
runtime/bin/pcbm-info, pcbm-profiles, pcbm-preferences and their contracts. This Menu
source requires the matching product runtime; future packaging must assign a new
versioned dependency and validate installed paths. Existing VERSION, package changelog,
POC2 tag/package and POC1–3 images remain unchanged. Nothing was built or installed.

26 Menu tests plus the shared-launcher checker pass; 25 individual Bash syntax checks
pass. Product has 86 tests passing. Tests use fixtures/fake dialog/VICE and sibling source
checkouts. Performance samples are Mac-only; real dialog, Linux installation and new
physical Pi qualification remain untested. No sudo grant, SSH, networking, session,
geometry, audio, first boot or broad CONTROL change. No push/publication.

Branches remain Menu feature/1.1-debian-package and product feature/1.1-build-foundation.
New recovery checkpoint: configured external bulk workspace,
archive/information-machines-2026-09-16, exact commits/ref inventories/bundles and verified
offline restore. Earlier checkpoints remain immutable. Independent backup is unresolved.

Remaining debt: dormant pcbm-start legacy dispatch/default reader (migrate before boot
activation); existing About/version/status probes; unrelated legacy privileged helpers.
Next owner review: bounded About/current-status cleanup using the structured authority.
No POC4 or broader settings work is implied. Earlier sections below are historical
completed checkpoints, not the current consumer state.

---

# Shared UI/result foundation complete — 2026-09-16 / STOP

Owner approved retaining Bash + dialog and the pcbm-menu / pcbm-config / pcbm-info /
narrow-backend boundaries. This slice adds opt-in `lib/pcbm-ui.sh`, its future Debian
install entry, [contract documentation](docs/UI-CONTRACT.md) and ten fake-dialog tests.
Selection, Cancel, Escape/Back, success/failure, validation and unavailable are distinct.
No existing Main Menu/CONTROL screen, launcher, boot flow or privilege behavior changed.
A representative fake domain action runs only after successful selection.

Ten UI tests, the existing launcher checker and 24 per-file Bash syntax checks pass
on macOS Bash 3.2. ShellCheck is unavailable. No real dialog/Pi rendering performance
or Linux runtime qualification is claimed. The product supplies read-only pcbm-info,
user preference and profile-registry foundations; see its
[runtime checkpoint](../project-cbm/docs/runtime/foundation-slice.md).

Stay on feature/1.1-debian-package. VERSION and the frozen v1.1.0_poc2 tag/package are
unchanged; no package was built. A future package requires an intentional new version,
source pin and hash, never reuse/retag of POC2. Product POC3 physically passed its bounded
Pi 3B test; the older checkpoints below retain their historical physical-UNTESTED state.

Recovery: configured product bulk workspace, `archive/runtime-foundation-2026-09-16`,
manifest and offline restore report for both repositories. No push/publication.
Next owner decision: authorize a targeted read-only System Information consumer and
machine-preference/registry migration, with explicit compatibility tests, before broad
configuration reorganization. No POC4, image, first-boot/network/service implementation,
additional-model testing or optional software is authorized by this completed slice.

---

# POC2 Menu package complete — owner physical review pending

Active feature/1.1-debian-package supplied the frozen product POC2 Menu input:
local annotated v1.1.0_poc2 object 4ff0f9c5d94f16064e2c43c960a429ecb275372b,
peeled 897cee7c792b11bfed80168a576f263340f5f57d. Package
project-cbm-menu 1.1.0~poc2-1+pcbm1 (all), SHA-256
e29bc3598f3be0869f79184250f88a03f4c59f1304a20a428223bac58c97bd11.
Later documentation commits do not change that frozen source/package identity.

pcbm-run-vice shares RUN/content behavior, rejects root and invalid profiles, and
sets F10 to open VICE's menu (Quit returns to CBM). Product integration owns optional
bounded diagnostics, getty/PAM sessions and the private non-root diagnostic VT.
Engineering profile gates unsupported network/BBS/raspi-config setup. No broad sudo,
SSH or full settings redesign. Per-file Bash syntax and shared-launcher argument/
exit tests pass. Product POC2 passed offline payload checks; physical behavior is
UNTESTED. POC1 had boot/Menu success and x64sc/console-recovery failure on Pi 3B.

[Product checkpoint](../project-cbm/docs/build/private-poc2.md) owns exact image/
lock/media identities and [physical procedure](../project-cbm/docs/qualification/poc2-pi3b-smoke-test.md).
STOP for owner review. No physical testing, further code change, POC3 or publication.
Main and all pre-existing tags remain unchanged; POC1 package/input is immutable.
The historical checkpoints below retain their original context.

---

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
