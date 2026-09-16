# Shared UI/result contract 1

The new `lib/pcbm-ui.sh` is an opt-in Bash/dialog foundation. Existing Main Menu,
CONTROL hierarchy, launcher and frozen packages are unchanged. Future packaging
installs it under `/usr/share/project-cbm-menu/`; no package is built in this slice.
No new tag/version is implied by modifying this feature branch.

## Calling convention

Source the library once. Import performs no probes, external calls or terminal changes.
Functions run unprivileged; the library contains no sudo, service or configuration
operations. Use conditional calls, including in scripts using `set -e`:

```bash
source /usr/share/project-cbm-menu/pcbm-ui.sh
if pcbm_ui_menu 'Project CBM' 'Choose a task' INFO 'System information' BACK 'Back'; then
    selected=$PCBM_UI_CHOICE
    # Dispatch a validated domain operation here, outside the UI helper.
else
    status=$?
    # Handle Cancel, Back, unavailable or failure; do not assume all mean cancel.
fi
```

| Return | PCBM_UI_STATUS | Meaning |
|---:|---|---|
| 0 | success | Selection/acknowledgment/confirmation succeeded |
| 1 | cancel | Cancel/No from dialog |
| 2 | back | Escape from dialog |
| 3 | failure | Tool failed or returned an unexpected selection |
| 4 | validation_error | Invalid UI/domain input |
| 5 | unavailable | Missing dialog or terminal too small |

`PCBM_UI_CHOICE` contains only a validated menu tag on successful selection and is
cleared on non-success. Do not invoke these functions through command substitution:
that would discard their status/choice globals. `pcbm_ui_result N` maps an already
normalized domain result to this contract; it does not translate arbitrary command
exit codes. For example, a preferences CLI exit 2 is an operation error, not UI Back.
A future adapter must inspect its own operation contract and choose failure/validation.

`pcbm_ui_confirm TITLE TEXT` defaults to No. `pcbm_ui_message TITLE TEXT` is a plain
informational acknowledgment. Wrappers do not implement the domain operation or
silently retry it. The representative test dispatches a harmless fake domain action
only after selection and proves Cancel makes no domain change.

## Rendering boundary

Keep Project CBM's backtitle, keyboard/dialog experience and optional existing theme;
no new renderer is introduced. Mouse interaction is disabled. COLUMNS/LINES use an
80×24 fallback, numeric validation and bounded widget dimensions; a terminal below
40×12 returns unavailable instead of retrying forever. Callers should refresh their
terminal dimensions on resize. No complete resize/event framework is claimed here.

Menu inputs must be tag/description pairs with unique simple tags; returned choices
must match the offered tags. Control bytes except newline/tab are rejected. A menu
is bounded to 128 choices and total input text to 32 KiB; larger content libraries
need pagination in their domain browser, not a giant dialog argument list. Text is passed as data,
without eval or printf %b. More complete Unicode width/wrapping/accessibility work and
real on-console rendering tests remain future work. This helper has no forms/password
entry yet; add them only with their operation/secret-handling contract.

Set PCBM_DIALOG_BIN only for controlled tests or an explicit unprivileged embedding.
Production defaults to `/usr/bin/dialog`. It is not a privileged executable-selection
interface. Missing tools, tool failures and unavailable operations must remain visible
to callers. Power/security-sensitive confirmation policy belongs to each operation.

## Tests

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_ui_contract.py -v
bash -n lib/pcbm-ui.sh
```

The fake dialog records arguments and returns deterministic choices/status codes.
Tests cover selection, Cancel/Escape/error, unknown choice, safe confirmation default,
invalid inputs/dimensions, missing dialog, informational acknowledgment, import without
side effects, and no domain action after Cancel. Tested with macOS Bash 3.2. These
are contract tests, not a Raspberry Pi or real-dialog rendering qualification.

The product [runtime contract](../../project-cbm/docs/runtime/info-contract.md) defines
how future pcbm-config consumes JSON. Keep detection in pcbm-info, not this library.
