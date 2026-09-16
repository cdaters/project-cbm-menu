#!/bin/bash
# Project CBM UI contract 1 (MIT). Unprivileged presentation only.
# Call inside `if ...; then ...; else rc=$?; ...; fi` when using set -e.
# No sources, subprocesses, terminal changes or side effects on import.
PCBM_UI_STATUS=unavailable
PCBM_UI_CHOICE=

pcbm_ui_result() {
  PCBM_UI_CHOICE=
  case "$1" in
    0) PCBM_UI_STATUS=success ;;
    1) PCBM_UI_STATUS=cancel ;;
    2) PCBM_UI_STATUS=back ;;
    3) PCBM_UI_STATUS=failure ;;
    4) PCBM_UI_STATUS=validation_error ;;
    5) PCBM_UI_STATUS=unavailable ;;
    *) PCBM_UI_STATUS=failure; return 3 ;;
  esac
  return "$1"
}

pcbm_ui_invoke() {
  local kind=$1 title=$2 message=$3 raw rc cols=${COLUMNS:-80} lines=${LINES:-24}
  shift 3
  PCBM_UI_CHOICE=
  if [[ ! $cols =~ ^[0-9]{1,3}$ || ! $lines =~ ^[0-9]{1,3}$ ]]; then
    pcbm_ui_result 4; return 4
  fi
  cols=$((10#$cols)); lines=$((10#$lines))
  if (( cols < 40 || lines < 12 )); then pcbm_ui_result 5; return 5; fi
  (( cols > 100 )) && cols=100
  (( lines > 22 )) && lines=22
  local value printable total=0
  for value in "$title" "$message" "$@"; do
    printable=${value//$'\n'/}
    printable=${printable//$'\t'/}
    total=$((total + ${#value}))
    if [[ $printable =~ [[:cntrl:]] ]] || (( total > 32768 )); then pcbm_ui_result 4; return 4; fi
  done
  if [[ ! -x ${PCBM_DIALOG_BIN:-/usr/bin/dialog} ]]; then pcbm_ui_result 5; return 5; fi
  local options=(--stdout --no-mouse --backtitle 'Project CBM' --title "$title" --cancel-label Back)
  case "$kind" in
    menu) options+=(--menu "$message" "$lines" "$cols" "$((lines - 8))" "$@") ;;
    input) options+=(--max-input 128 --inputbox "$message" "$lines" "$cols") ;;
    secret) options+=(--max-input 128 --passwordbox "$message" "$lines" "$cols") ;;
    confirm) options+=(--defaultno --yesno "$message" "$lines" "$cols") ;;
    textbox) options+=(--exit-label Back --textbox "$message" "$lines" "$cols") ;;
    message) options+=(--msgbox "$message" "$lines" "$cols") ;;
    *) pcbm_ui_result 4; return 4 ;;
  esac
  if raw=$(DIALOG_OK=0 DIALOG_CANCEL=1 DIALOG_ESC=255 DIALOG_ERROR=254 DIALOG_HELP=2 DIALOG_EXTRA=3 "${PCBM_DIALOG_BIN:-/usr/bin/dialog}" "${options[@]}"); then rc=0; else rc=$?; fi
  case "$rc" in
    0) PCBM_UI_STATUS=success; PCBM_UI_CHOICE=$raw; return 0 ;;
    1) pcbm_ui_result 1; return 1 ;;
    255) pcbm_ui_result 2; return 2 ;;
    *) pcbm_ui_result 3; return 3 ;;
  esac
}

pcbm_ui_menu() {
  local title=${1:-} message=${2:-} rc tag
  if (( $# < 4 || $# > 258 || ($# - 2) % 2 )); then pcbm_ui_result 4; return 4; fi
  shift 2
  local tags=() args=("$@")
  while (( $# )); do
    tag=$1
    if [[ ! $tag =~ ^[A-Za-z0-9][A-Za-z0-9_.:-]*$ ]]; then pcbm_ui_result 4; return 4; fi
    local prior
    for prior in "${tags[@]-}"; do
      if [[ $prior == "$tag" ]]; then pcbm_ui_result 4; return 4; fi
    done
    tags+=("$tag"); shift 2
  done
  if pcbm_ui_invoke menu "$title" "$message" "${args[@]}"; then
    for tag in "${tags[@]}"; do [[ $PCBM_UI_CHOICE == "$tag" ]] && return 0; done
    pcbm_ui_result 3; return 3
  else rc=$?; return "$rc"; fi
}

pcbm_ui_confirm() { pcbm_ui_invoke confirm "${1:-Confirm}" "${2:-Continue?}"; }
pcbm_ui_message() { pcbm_ui_invoke message "${1:-Project CBM}" "${2:-}"; }

# Call in the interactive entry point, not on import. No assumptions about HDMI size.
pcbm_ui_terminal_size() {
  local rows cols
  if read -r rows cols < <(stty size 2>/dev/null) && [[ $rows =~ ^[0-9]+$ && $cols =~ ^[0-9]+$ ]] && (( rows > 0 && cols > 0 )); then
    LINES=$rows COLUMNS=$cols
  fi
  export LINES=${LINES:-24} COLUMNS=${COLUMNS:-80}
}

# Caller owns a private, bounded, formatted file and removes it after display.
pcbm_ui_textbox() {
  [[ -f ${2:-} && -r ${2:-} ]] || { pcbm_ui_result 5; return 5; }
  pcbm_ui_invoke textbox "${1:-Project CBM}" "$2"
}

pcbm_ui_input() { pcbm_ui_invoke input "${1:-Project CBM}" "${2:-}"; }
pcbm_ui_secret() { pcbm_ui_invoke secret "${1:-Project CBM}" "${2:-}"; }
