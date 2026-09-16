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
