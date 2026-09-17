# POC4 attempt #3 lifecycle investigation

2026-09-17: **STOP for existing physical SD-card evidence. No runtime correction
selected and no new Menu version/tag/package.** The governing owner scope is the
unchanged AGENTS.md at predecessor `be73ff1`; Product predecessor is `8a93683`.

The [Product owner-review report](../../project-cbm/docs/qualification/poc4-regression-investigation-2026-09-17.md)
is authoritative for the differential, evidence, first-boot audit and recovery. The
[additive physical record](../../project-cbm/docs/qualification/poc4-attempt3-pi3b-owner-report-2026-09-17.json)
binds the owner's Pi 3B run to frozen Menu `v1.1.0_poc4.1`, peeled
`407ced58b711209631cdfb4db6dcd741a555f408`, Product lock
`435c6e0d7a5a45eaff3f45af6d384fca5b602139fa9fb640950e2f5e7b4f39a9` and raw image
`37d2699c7a639e050e531a4d5a132d4b197e5a60270a969814c573f436036cd8`.

RUN/VICE/F10/Quit/visual Menu return passed. Visible Cover, returned Menu keyboard,
Ctrl+Alt+F2 and Ctrl+C failed. mc launch and optional application presence passed;
SID-Wizard/StrikeTerm operation is still UNTESTED. POC3 physically proved responsive
Menu return and VT switching, but it did not contain the new SDL Cover.

## Evidence and remaining uncertainty

All base package hashes, including SDL/Mesa/login/PAM, match POC3. VICE bytes,
geometry/audio/F10, Product engineering wrapper and getty/profile recipes are unchanged.
New Cover runs under GNU timeout in its own process group before the engineering
wrapper saves terminal/keyboard state. Normal SDL cleanup releases its resources;
forced termination cannot guarantee application cleanup. The exact retained SDL source
can change keyboard translation and VT ownership during KMS initialization.

If Cover leaves altered keyboard state, the unchanged VICE wrapper can save and restore
that already-bad state. That conditional sequence is a strong candidate, not a captured
physical event. Missing Cover could also be a tty guard, display/init/renderer error,
early key skip or timing failure. The launcher discards its output and exit status.
Physical logs/state are missing; the relationship between failures is **UNKNOWN**.

Do not patch timeout, add sleeps/resets, switch VT or change privileges on this evidence
alone. Do not assume a visually returned Menu proves live stdin/dialog/foreground
ownership. The old reset/clear return hook is unchanged; the new no-argument Cover exits
before SDL. No per-menu duplicate renderer, artwork or mapping change is justified.

## First boot and tests

The [first-boot audit](../../project-cbm/docs/qualification/poc4-first-boot-ux-findings-2026-09-17.md)
confirms Back exits rather than going to the preceding field, raw locale/layout/country
identifiers, no password mask/invisible-typing explanation, invisible synchronous work,
generic failure messages and a Wi-Fi subflow entered only after setup completion.
No UX correction was implemented because the higher-priority physical-evidence stop
applies. Punctuation/spaces are permitted by the WPA-personal validator; never request
the failed credential. Retained native tests prove selected synthetic keyfile parsing,
not physical authentication.

65/65 Menu baseline tests and included launcher checker pass. Product has 142/143
passing, with an unrelated macOS mktemp failure in the existing environment-boundary
test. Fixtures do not prove physical KMS/keyboard/VT cleanup. Future changes need focused
failure/timeout/cleanup/repeated-cycle and first-boot navigation/progress/security tests,
then separate physical qualification. No new behavioral tests or runtime edits here.

## Handoff and recovery

Next: owner [collects existing card evidence read-only](../../project-cbm/docs/qualification/poc4-regression-collect-evidence.md).
No reboot/relaunch or new physical test is required for offline extraction. If the
failed live session still exists, report that before powering down.

Recovery under configured bulk root:
`archive/poc4-regression-investigation-2026-09-17`; evidence:
`qualification/poc4-regression-2026-09-17`. The manifest records exact final refs,
full bundles, offline restoration/fsck and preserved candidate identities. No image
duplication or independent-backup claim. Future source corrections require a newly
versioned Menu input; no new tag, package, lock or image is assigned here. The
[next-candidate procedure](../../project-cbm/docs/qualification/poc4-next-candidate-regression-draft.md)
is an unbound draft, NOT READY TO FLASH. Nothing pushed; AGENTS unchanged.

All seven artwork files, names and rights classifications remain unchanged. No Dosbian
source copied, no MEDIA/TOOLS/POWER/recovery restructuring, boot optimization, PSID/RSID
implementation or other-model work. The owner's design suggestions remain backlog
input for later review, not acceptance of every proposal for 1.1.
