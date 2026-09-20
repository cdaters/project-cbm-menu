> Current 1.1 refinement: Menu consumes `pcbm-info --json --appliance` for network
> and service state, without local probing. Main Menu is concise; submenus and service
> screens add actual readiness, useful state-aware actions and connection help. Owner
> login is `owner`; SSH uses the first-boot password, File Sharing a separate password.
> Default Computer Name is `projectcbm`. Product's [connection guide](../../project-cbm/docs/release/networking.md)
> is authoritative. Earlier activation-pending notes below describe historical staging.
> Cover/VICE/session ownership remains unchanged.

# Project CBM configuration

Use **CONTROL** on Main Menu, or `pcbm-config`. The familiar Bash/dialog front door
now opens a shallow task-oriented settings experience. System Information and About
consume product pcbm-info JSON; no duplicated hardware/version probes.

- [Normal-user guide](../../project-cbm/docs/runtime/pcbm-config.md)
- [Developer/privilege/activation contract](../../project-cbm/docs/runtime/configuration-contract.md)
- [Checkpoint and test results](../../project-cbm/docs/runtime/configuration-maturation.md)
- [Shared UI contract](UI-CONTRACT.md)
- [Machine/preference migration](INFORMATION-MACHINES.md)

Menu owns scripts, presentation/request formatting and shared dialog behavior. Product
owns info, preferences, profile registry, schemas, validated OS operations, accounts and
image activation. Menu's pcbm-config bridge encodes fields and displays fixed messages;
it is not the security validator and never executes privileged operations itself.

Compatibility entry points route to pcbm-config. Main QUIT is retired; Advanced →
Terminal runs an unprivileged child shell and waits, so exit returns naturally. Machine
choice remains user-owned. The legacy default/start/status/version and generic USB
mount paths have been removed from the migrated runtime. Audio reads only typed data
and saves atomically; VICE presentation and shared launch behavior remain unchanged.

This is source work, not an installed image. Future matching product runtime/package
installation, first-boot owner authentication and tested service readiness are required.
USB import's narrow broker, TCPser typed launch adapter and boot-preference consumer
remain product runtime gates, not another Menu architecture study. The UI clearly
marks pending operations; no service is silently enabled or unmasked.

Do not rebuild the existing package/tag with these changed bytes. A future candidate
requires new Menu version/tag, peeled commit, source/package hashes and a matching
product runtime dependency. Product's frozen POC1–3 packages and behavior are unchanged.

Run `python3 -m unittest discover -s tests -v` with sibling product source and its pinned
developer requirements. Fake dialogs/Linux operations prove control/data behavior;
real TTY/dialog, Linux service/account integration and Pi performance require later tests.

## Optional C64 applications

The [product user guide](../../project-cbm/docs/release/user-guide.md#optional-applications)
describes SID-Wizard and the CCGMS 2021 application disk. Their normal CONTENT folders
use Product's C64 profile without changing the saved default. CCGMS gets temporary
SwiftLink/IP232 arguments from the Product `content-options` command; other media
retain the shared launcher and normal preferences. G71 uses compatible C64/C128
1571 routing. Menu RC4 requires Runtime >=1.1.0~rc4-1 for this interface.

[CCGMS integration](../../project-cbm/docs/runtime/ccgms-integration.md) owns the exact
program/source/license identity and modem contract. Artwork permission is recorded
separately from code licensing in `debian/copyright` and the artwork manifests.
