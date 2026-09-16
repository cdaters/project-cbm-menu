# System Information and machine selection

2026-09-16, source-only implementation. Product owns the information, registry and
preference authority; this repository presents it. No package/image build or push.

- [User workflow](../../project-cbm/docs/runtime/information-and-machines.md)
- [Developer interfaces and remaining debt](../../project-cbm/docs/runtime/information-machines-contract.md)
- [Source checkpoint and validation](../../project-cbm/docs/runtime/information-machines-slice.md)
- [Shared UI contract](UI-CONTRACT.md)

CONTROL adds INFO without reorganizing other settings. The Python standard-library
formatter consumes pcbm-info JSON once; it performs no hardware probes. MACHINES
keeps direct launch and default selection; a successful save returns straight to
Main Menu with the new label. Registry IDs replace duplicate Menu-only machine tags.
Cover selection, RUN and content use product-validated profiles/defaults. No sudo to
save a default. Boot preference remains inactive; dormant pcbm-start migration is deferred.

The future package installs the formatter under `/usr/libexec/project-cbm-menu`, the
shared UI under `/usr/share/project-cbm-menu` and `pcbm-system-info` under `/usr/bin`.
It requires the matching product runtime commands; encode a versioned product dependency
when that package is assigned. Do not rebuild the frozen POC2 version with these bytes.

Tests use both sibling source checkouts and the product's pinned developer test
requirements. They invoke actual source entry points against private temporary state,
fixture JSON and fake dialog/VICE, never a real emulator or privileged operation:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

No real-console rendering, Linux package integration or new physical result is claimed.
