# Project CBM Menu Development Rules

Menu is the keyboard-first front panel for Project CBM. Preserve its personality,
user control and reliable emulator return while simplifying common tasks. Favor
clear Bash/dialog interfaces and measurable responsiveness on the Pi 4 floor.

## Authority and continuity

This file is standing Menu governance. It replaces all former milestone-specific
STOP/owner-review clauses, one-candidate limits and authorization sections in earlier
AGENTS revisions. Dated copies in CURRENT-STATE and build/recovery/qualification
records describe historical scope, not active restrictions on private engineering.
Their technical requirements, evidence and permanent protections remain applicable.

Read [CURRENT-STATE.md](CURRENT-STATE.md), [provenance](docs/provenance.md),
[versioning](docs/VERSIONING.md) and the [Product recovery contract](../project-cbm/docs/recovery.md).
Inspect actual refs/dirty work; never erase unknown work to match a checkpoint.
Current user instructions define and may narrow the task, including leaving changes
uncommitted. Do not expand a bounded task into unrelated backlog. Tool/sandbox
permissions still apply. Old sessions and reference projects are not dependencies.

Keep candidate identities, changing status, results and exact next actions in
CURRENT-STATE and canonical Product build/qualification/recovery records. Edit
AGENTS only for durable governance changes, not each milestone or candidate.

## Standing private engineering authority and owner gates

Within the requested outcome and these protections, Codex may autonomously
investigate, fix, test, commit locally, version/package Menu, supply frozen inputs,
validate installation, checkpoint and iterate on successive private candidates.
Coordinated Product work may freeze distinct candidates and build/validate them via
the approved Lima/VZ + pinned pi-gen factory under [Product governance](../project-cbm/AGENTS.md).
No fresh owner authorization or AGENTS edit is required for each private iteration.

Halt an affected build/validation on integrity failure, retain the failed attempt,
and diagnose it without bypassing gates. Evidence-supported fixes and distinct
retries are authorized once required gates pass. Escalate only a genuine missing
owner decision or hard-gated action, not a historical phase boundary.

Explicit owner approval is required for push/publication; destructive changes to
historical evidence, frozen inputs/outputs or recovery records; security/privacy/
privilege weakening; major architecture or repository-boundary changes; unresolved
third-party redistribution decisions; rewriting published history or replacing
protected tags/assets; and physical testing/flashing or advancing hardware claims
beyond exact retained owner reports. Approval cannot replace evidence or rights.
Recording an existing owner report additively needs no second approval. New local
private version tags and packages do not grant publication permission.

## Menu and Product responsibilities

- Menu owns independently versioned scripts/assets, UI and interface contracts,
  packaging and focused tests. Product owns OS/runtime integration, accounts and
  services, image construction, release identity/mapping, hardware policy,
  qualification, artifacts, recovery and product docs. public-docs is a historical
  packaging mirror, not a competing authority.
- `pcbm-menu` presents navigation; `pcbm-config` presents/orchestrates configuration.
  Product's read-only `pcbm-info` JSON is the information authority: consume its
  versioned structured data, never duplicate hardware/network probes or scrape its
  human display. See [information/machines](docs/INFORMATION-MACHINES.md) and the
  [configuration contract](../project-cbm/docs/runtime/configuration-contract.md).
- Product registry and user-owned validated preferences own machine/profile/default
  selection. No duplicate machine tables or privileged default writes. Valid new
  state wins, missing state may import legacy once, invalid state needs explicit
  recovery. Saved boot/modem/service intent is not activated runtime behavior.
- UI/client code stays unprivileged. Root operations belong to Product's fixed,
  validated, readiness-gated backend. Preserve authenticated owner administration,
  protected credential transport/storage and deliberate service/listener opt-in.
  No universal credentials, broad sudo or unrestricted passwordless root.
- Keep one shared unprivileged VICE launcher and Product terminal/session ownership.
  Capture state before Cover, supervise/bound/terminate/reap it, restore/verify before
  and after VICE and retain bounded diagnostics. Missing/failed Cover must permit
  VICE launch without weakening terminal safety. Retain F10/Quit, user preferences,
  VICE per-chip aspect-preserving geometry and reliable repeated Menu return.
- Preserve COVERS terminology, all seven existing artwork files/names/bytes/provenance
  and Product registry mapping. No per-menu mapping, root/framebuffer/resolution
  workaround or artwork substitution. See [Covers](../project-cbm/docs/runtime/covers.md).
  Private engineering use alone does not clear artwork for public distribution.
  Apply the explicit owner permission and [1.1 release policy](../project-cbm/docs/release/release-policy.md)
  for the existing Craig Daters branding/Covers; keep artwork licensing separate from MIT code.
- Preserve Bash/dialog, console getty/PAM/session behavior, SDL2 VICE and ALSA.
  Pi 4 is the 1.1 performance floor. Target Pi 4 B/400 and Pi 5/500/500+ only where
  supportable and individually qualified. Pi 3/Zero-class hardware is outside the
  1.1 release target; preserve its historical evidence without further optimization.
  No renderer migration for novelty.
- Improve layout where concrete before/after benefit warrants it. Use shared UI/results,
  predictable Back/Cancel/retry/resume, human-readable setup choices and truthful
  working/error/hidden-password feedback. Do not equate arbitrary command exit 2
  with UI Back. Preserve user preferences and measure Pi 4 cost of material changes.

## Versioning and immutable integration inputs

- Menu and Product versions are independent. 1.0.x is important/security maintenance
  of the original Trixie line; 1.1.x is active modernization. Formal v1.0.0 and the
  recovered image runtime differ; forensic recovery refs are evidence, not releases.
  Preserve tags/history/assets; never infer Menu version from Product version.
- Every Product candidate consumes an explicit Menu version/tag, annotated tag object
  where applicable, peeled full commit and artifact SHA-256, never arbitrary main.
  Supply packaging recipes, patches/assets/licenses, schema compatibility and tests.
  See the [Product build contract](../project-cbm/docs/build-and-release.md).
- Changed package inputs require a new versioned identity; never replace completed
  package bytes or move tags. Verify exact identity/compatibility before reusing
  unchanged inputs. Product owns distinct frozen locks, build/attempt directories,
  full-image validation, raw/XZ hashes and host drift/capability gates.
- Source changes do not retroactively exist in frozen packages/images. A Menu package
  pass is not a Product image, reproducibility or physical qualification pass.
  Integrated version displays consume Product-generated metadata, not a competing
  editable Product identity.

## Storage, preservation, security and recovery

- Source/docs stay in configured Git roots (currently ~/Code); large inputs, packages,
  images, trees, caches, build temp and evidence belong on mounted
  /Volumes/TheBench/ProjectCBM-Work. Verify mount identity/capacity; never fall back
  silently to internal SSD. Tooling uses configured roots and portable locators.
- /Volumes/TheBench/Projects/Project CBM is original evidence: no edits, renames,
  normalization, deduplication, cleanup or execution in place. Preserve inventories
  and bundles in ProjectCBM-Work/archive/preservation-2026-09-15; verify manifests
  after preservation changes without replacing a baseline to hide a mismatch.
- TheBench is unencrypted APFS with ownership disabled, not Linux rootfs storage or
  an encryption boundary. Product's approved builder uses external-backed ext4.
  Historical/private records and public artifacts remain separate trust domains.
- Follow [Product security](../project-cbm/docs/security.md): record sensitive-file
  presence/type, never private keys, credentials, password hashes, shell history or
  private device/network identities in Git/output. Keep diagnostics allowlisted and
  private; do not read credentials to populate information views.
- Preserve rights/source/license evidence. Private admission of assets/applications
  is not redistribution approval; freeware, possession and archive inclusion do not
  establish rights. Do not import historical private content or run automatic content
  downloaders. Keep original qualification media distinct from third-party references.
- Full black-box recovery belongs to Product repositories and retained infrastructure.
  Menu supplies exact source/tag/package/recipe/test identities. Only minimal generated
  identity belongs in the appliance; no full locks, recipes, archives or closure merely
  for recovery. Preserve the acyclic checksum design and portable external records.
- Make additive checkpoints with both repositories' relevant refs/bundles/manifests
  and verified offline restore/ref/peeled-tag/fsck results. Retain earlier checkpoints.
  Independent backups and restore drills are required; GitHub/caches or another
  folder on TheBench are not independent custody. Report remaining gaps honestly.

## Validation and session close

- Run git diff --check, per-file bash -n for changed scripts/pcbm-* and packaging/*.sh,
  JSON/link validation and changed-file size/secret review. Use ShellCheck when available
  and focused behavioral/package/native tests for relevant changes; follow
  [Product testing](../project-cbm/docs/testing.md). Report contextual failures accurately.
- Never execute installer, docs-sync (even --dry-run), release-prep, privileged tooling
  or historical/runtime scripts as a static/documentation check.
- Preserve PASS/FAIL/UNTESTED/BLOCKED with exact candidate and test identities. Static,
  VM/headless and offline tests cannot prove physical Cover/KMS/keyboard/VT/audio or
  another model's support. Product owns hash-bound physical procedures and additive
  owner attestations; do not fabricate passes or retrospectively prove unknown causes.
- Before commits check effective author/committer identity and local overrides; use
  the contributor's GitHub noreply identity when email privacy is enabled. Do not
  disable privacy, hard-code operator emails or treat GH007 as rewrite authorization.
- After meaningful work update CURRENT-STATE with checks/limits, exact checkpoint,
  evidence/recovery links and next action; update relevant canonical docs additively.
  Leave clear Git status and logical local commits unless the user asks for uncommitted
  review. Explain confirmed, inferred and unresolved facts; favor concise how-to
  guidance and canonical links over repeated technical detail or historical ledgers.
