# Working on Project CBM Menu

Read CURRENT-STATE.md, docs/provenance.md, docs/VERSIONING.md and the companion
product docs/recovery.md first. Update
CURRENT-STATE.md after meaningful work; no prior Codex session is required.

This repo owns independently versioned Menu scripts/assets, interfaces/contracts,
packaging and focused tests. Companion ../project-cbm owns product/OS integration,
image builder, VICE/TCPser/Menu mapping, qualification, hardware policy, artifacts
and product documentation. Do not let public-docs/ become a competing authority.

Future products require a Menu version/tag, peeled commit and artifact SHA-256;
never arbitrary main. Existing v1.0.0 is immutable and differs from the image's
exact 17-script runtime. The recovered/image-v1.0.0-runtime tag is forensic evidence,
not a release. maintenance/1.0 begins at that root recovery; no 1.0.1 exists.
1.0.x is original Trixie important/security maintenance; 1.1.x is active modernization.
No Bookworm line exists. Do not reset, force-push, retag or replace release assets.

Keep the Pi 3 performance floor and target Pi 3 through Pi 500+ where qualified.
No hardware passes may be inferred from OS compatibility or syntax checks. Preserve
Bash/dialog/SDL2/ALSA architecture; do not silently optimize for Pi 5 only.
Do not casually broaden sudo, network/listener, service, boot or first-boot behavior.

Canonical source/docs stay under ~/Code. Large inputs/images/build trees/caches
belong on mounted /Volumes/TheBench/ProjectCBM-Work, never internal-SSD fallback.
Original /Volumes/TheBench/Projects/Project CBM is evidence: no edits, renames,
cleanup, normalization, deduplication or execution in place. Preservation inventory
and bundles are under ProjectCBM-Work/archive/preservation-2026-09-15.
APFS is not a ready Linux rootfs; no builder is provisioned. Historical evidence
and public artifacts are separate trust domains. Record sensitive-file presence,
never private keys, credentials, password hashes or shell history in Git/output.

Run git diff --check, per-file bash -n for scripts/pcbm-* and packaging/*.sh,
validate JSON/links and inspect staged sizes/secret patterns. Use ShellCheck when
available and focused tests for behavior changes. See product docs/testing.md and
docs/security.md. Never execute installer, docs-sync (even --dry-run), release-prep
or runtime scripts as a static check. Existing packaging/CI defects are recorded,
not repaired by this phase. Update current state with checks and remaining gaps.

Preservation, owner-accepted cold-start comprehension and final architecture
reconciliation are complete. Product ADR-0001 accepts Lite + pinned arm64 pi-gen
with bounded appliance practices. A NEW instruction must authorize the 1.1 POC;
stop this architecture phase before Linux provisioning, pi-gen, packaging, runtime
changes, first boot, image build, push or publication.

## Black-box recovery contract

Product docs/recovery.md defines full black-box PROJECT recovery in repositories
and retained build/release infrastructure: source/input/build/product/qualification
evidence and independent restore tests. The image carries only minimal installed
identity; no complete lock, recipes, recovery archive or package closure. No mandated
8 GB card minimum: qualify actual system footprint and free user-data capacity.
Menu must supply exact source/tag/peeled commit/artifact hashes, packaging recipe,
patches/assets/licenses/schema compatibility and focused test evidence. It must
not create a competing product identity or infer its version from the product.
Future Menu version displays consume product-generated metadata when integrated.
All of that runtime work remains deferred. Current local source/TheBench paths are
deployment choices; accept configured roots and portable locators in future tooling.
Preserve unknown dirty work after interruption, including work newer than CURRENT-STATE.
Neither old sessions nor Spitfire/FireComm/reference projects may become dependencies.

## Commit identity and current owner authorization

Use the contributor's GitHub-provided noreply identity when email privacy is enabled.
Before commits, check effective author/committer identity and repository-local
overrides; keep privacy protection enabled. Do not hard-code an operator email in
project tooling. Never repair published history. The 2026-09-15 owner exception
applied only to eight explicitly scoped unpublished commits and the dependent
unpublished Menu forensic tag; see the product privacy reconciliation record.

The owner has authorized Milestone 1 contracts/tests and build-host research, with
a hard approval checkpoint before Linux host provisioning, disk allocation, package
builds, pi-gen or images. The current identity-repair task authorizes its scoped
rewrite, additive documentation/checkpoints and normal publication only; stop after
verified pushes and offline recovery. Earlier phase-specific no-push/no-implementation
statements above describe those completed phases, not a substitute for current scope.

## Publication resolution and active milestone

Both main branches and Menu maintenance/recovery refs are published. Product
maintenance/1.0 stays local/bundled by owner decision: public v1.0.0 is the
authoritative public maintenance baseline. GH007 on the historical commit does
not authorize rewriting it, changing privacy settings or retrying that branch push.
The owner now authorizes resuming Milestone 1 on product
feature/1.1-build-foundation after synchronization/checkpoint verification. Complete
contracts/tests and retention/package/integration/first-boot design plus Linux host
research; STOP for the build-host options/recommendation checkpoint before installing
software, provisioning a VM/container/host, allocating large disks, building packages,
running pi-gen or building an image. No Menu feature branch without actual Menu work.

## Current POC2 owner authorization

Bounded shared unprivileged launch/F10 behavior, optional product diagnostics and
truthful engineering setup guidance are authorized on the existing feature branch.
No broad privilege/settings redesign or SSH. Preserve POC1 package/tag and all
historical refs. Stop at product POC2 offline validation; no physical test or push.
Use standard precise terminology in current docs, explain specialized terms, and
maintain concise how-to guides. Historical build notes remain unchanged evidence.

## Shared UI foundation (latest owner boundary / STOP)

The owner approved Bash/dialog and the Menu/config/info/backend boundaries. The first
slice adds only the opt-in UI/result library, contract/tests and future package install
entry. Existing scripts and frozen POC packages/tags remain unchanged. Product owns
pcbm-info and user preference/profile foundations; read its docs/runtime/foundation-slice.md.
No new image/package build, broad Menu/CONTROL reorganization, first boot, services,
SSH, other-model qualification or push. STOP for owner review after tests and recovery.
Future consumers must use structured pcbm-info output, not duplicate hardware detection
or parse its human display. Do not interpret arbitrary command exit 2 as UI Back.

## Information and machine consumers (latest completed boundary / STOP)

Owner-authorized source migration is complete. Read CURRENT-STATE and
`docs/INFORMATION-MACHINES.md`. System Information consumes pcbm-info JSON; MACHINES,
RUN and shared content/default/cover paths consume the product registry/preferences.
Do not reintroduce machine tables, hardware probes or privileged default-machine writes.
Missing state may import legacy once; invalid state requires explicit recovery. Boot
preference/dormant pcbm-start activation remains deferred. Preserve frozen tags/packages/
POC1–3. No package/image build, broad CONTROL/settings changes, SSH/services, new Pi test
or push. STOP for owner review after tests and verified source recovery checkpoint.
