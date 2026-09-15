# Menu release, image recovery and maintenance

The [product provenance record](../../project-cbm/docs/provenance.md) is authoritative
for image/input history and storage. [Current state](../CURRENT-STATE.md) provides
the exact refs without requiring old conversations. The [full reconciled audit](../../project-cbm/docs/audit-2026-09-15.md)
retains the findings and hardware matrix.

Formal Menu v1.0.0 is a related, later source release. It is not byte-identical to
the 17 scripts in Project CBM image v1.0.0. Twelve match; pcbm-control, pcbm-system,
pcbm-network, pcbm-start and pcbm-release-prep differ. The tag additionally ships
experimental pcbm-screenshot. Current main at b7e4d85 retains that runtime unchanged.
No original Git commit exactly matches all shipped scripts.

The annotated recovered/image-v1.0.0-runtime tag names a new forensic root commit,
`a4148db54001790eaddb4e31104917c16149b181`. It deliberately has no parent; there is
no invented historical commit ancestry. scripts/ contains byte-exact extracts from
the verified published image, checked against the historical raw image and original
audit extraction. A hash/mode manifest, recovery note and original-source MIT
license accompany them. There are no config examples, packaging, media or private
machine state in that snapshot. It must not be installed as a complete bundle.

v6.1/v6.3/v6.4/v6.5 loose/archive history, GoldMaster, scriptsForChat/for65 and patches
remain under TheBench's original Project CBM directory. v6.5 executable-source
equivalence is established, but shipped bytes differ and surrounding config is
not an exact installed snapshot. The raw image strongly appears pre-PiShrink; the
complete transformation chain remains unknown. Full manifests/logs stay private.

maintenance/1.0 begins at the recovered root; important/security changes require
an explicit reconciliation changelog, packaging/config review and product tests.
It does not change formal v1.0.0. A future maintenance release must have new input
mapping and qualification; no 1.0.1 is created/approved. Active 1.1 development will
use reviewed feature branches off main after owner authorization, not rewrite the
recovery. Product 1.0 and 1.1 are both Trixie generations; there is no Bookworm line.

Menu owns scripts/assets/interfaces/packaging/focused tests. Product owns image
integration, supported hardware, VICE/TCPser/Menu mapping and public docs. Future
consumption requires independent Menu version + explicit tag + peeled commit +
artifact SHA-256, per the [release contract](../../project-cbm/docs/build-and-release.md).
Do not run docs-sync or treat public-docs/ as authoritative. Historical manual
image-build instructions are not the 1.1 builder design.

## Recoverability from retained component inputs

Follow the self-contained [product recovery specification](../../project-cbm/docs/recovery.md).
Retain complete Menu refs/source, exact released artifact, source/packaging/config
schema identity, ordered patches, asset licenses and tests. If GitHub vanishes, the
verified full bundle and ref inventory restore history without the original Mac.
A source bundle is distinct from an installed image and cannot supply missing OS/
VICE/TCPser inputs or hardware qualification. Public metadata must exclude secrets;
current absolute paths are deployment locators, not component requirements.

## Authorized unpublished identity repair

The [2026-09-15 privacy reconciliation](../../project-cbm/docs/privacy-reconciliation-2026-09-15.md)
records old/new commit and forensic-tag IDs, exact-content verification, retained
private originals and current bundle/restore status. Existing published tags remain
unchanged; older checkpoint records intentionally retain pre-rewrite identities.
