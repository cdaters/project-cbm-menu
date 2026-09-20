#!/bin/bash
#
# ================================================================
#  Project CBM (pcbm)
#  Raspberry Pi Commodore System
#
#  Script: pcbm-dialog-lib.sh
#  Version: Loaded from /etc/pcbm/version.conf
#
#  Author: Craig Daters
#  Repository: https://github.com/cdaters/project-cbm
#
# ---------------------------------------------------------------
#  Description:
#  This script is part of Project CBM, a lightweight, appliance-
#  style Commodore environment for Raspberry Pi OS using the
#  VICE emulator suite.
#
# ---------------------------------------------------------------
#  License:
#  MIT License. See LICENSE in the project repository.
#
# ---------------------------------------------------------------
#  Credits & Acknowledgements:
#  - Combian64 by Carmelo Maiolino from which this build was inspired
#  - VICE Team, for the Versatile Commodore Emulator
#  - Raspberry Pi Foundation and Raspberry Pi OS developers
#  - Original Commodore engineers and developers
#  - The wider retro-computing and open source communities
#
#  Third-party content retains its own license and redistribution requirements.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
# Product/build information belongs to pcbm-info; chrome stays stable between builds.
PCBM_PROJECT_NAME="Project CBM"
PCBM_BACKTITLE="*** Project CBM - Raspberry Pi / Commodore appliance ***"
PCBM_HLINE="ENTER=Select   TAB=Buttons   ARROWS=Move   ESC=Back"
PCBM_MIN_WIDTH=72
PCBM_MAX_WIDTH=100
PCBM_EXTRA_WIDTH=12
PCBM_MIN_HEIGHT=14
PCBM_MAX_HEIGHT=22
PCBM_HEIGHT_PADDING=8
PCBM_BOX_MIN_WIDTH=56
PCBM_BOX_MAX_WIDTH=96
PCBM_BOX_MIN_HEIGHT=8
PCBM_BOX_MAX_HEIGHT=18
PCBM_TEXTBOX_MIN_WIDTH=64
PCBM_TEXTBOX_MAX_WIDTH=100
PCBM_TEXTBOX_MIN_HEIGHT=12
PCBM_TEXTBOX_MAX_HEIGHT=22
PCBM_CONTENT_BASE="/home/pcbm/content"
PCBM_CONFIG_DIR="/etc/pcbm"
PCBM_DEFAULT_MACHINE_CONF="$PCBM_CONFIG_DIR/default-machine.conf"
PCBM_JIFFYDOS_CONF="$PCBM_CONFIG_DIR/jiffydos.conf"
PCBM_USB_MOUNT="/mnt/pcbm-usb"
PCBM_VICE_LOG="/tmp/pcbm-vice.log"

pcbm_cleanup_terminal() {
  clear
  stty sane 2>/dev/null || true
  tput cnorm 2>/dev/null || true
}

pcbm_trap_cleanup() {
  trap pcbm_cleanup_terminal EXIT
}

pcbm_term_cols() {
  tput cols 2>/dev/null || echo 80
}

pcbm_term_lines() {
  tput lines 2>/dev/null || echo 24
}

pcbm_expand_text() {
  printf '%b' "$1"
}

pcbm_longest_line() {
  local input
  input=$(pcbm_expand_text "$1")
  local max=0
  local line len
  while IFS= read -r line; do
    len=${#line}
    (( len > max )) && max=$len
  done <<< "$input"
  echo "$max"
}

pcbm_count_lines() {
  local input
  input=$(pcbm_expand_text "$1")
  local count=0
  while IFS= read -r _; do
    ((count++))
  done <<< "$input"
  (( count == 0 )) && count=1
  echo "$count"
}

pcbm_clamp() {
  local value="$1" min="$2" max="$3"
  (( value < min )) && value=$min
  (( value > max )) && value=$max
  echo "$value"
}

pcbm_calc_menu_dims() {
  local title="$1"
  local prompt="$2"
  shift 2
  local -a items=("$@")
  local item_count=$(( ${#items[@]} / 2 ))
  local max_tag=0 max_desc=0 max_prompt max_title max_hline desired_width
  local term_cols term_lines prompt_lines desired_height list_height tag desc i max_width max_height

  for ((i=0; i<${#items[@]}; i+=2)); do
    tag="${items[i]}"
    desc="${items[i+1]}"
    (( ${#tag} > max_tag )) && max_tag=${#tag}
    (( ${#desc} > max_desc )) && max_desc=${#desc}
  done

  max_prompt=$(pcbm_longest_line "$prompt")
  max_title=${#title}
  max_hline=${#PCBM_HLINE}
  desired_width=$(( max_tag + max_desc + PCBM_EXTRA_WIDTH ))
  (( max_prompt + 8 > desired_width )) && desired_width=$(( max_prompt + 8 ))
  (( max_title + 8 > desired_width )) && desired_width=$(( max_title + 8 ))
  (( max_hline + 4 > desired_width )) && desired_width=$(( max_hline + 4 ))

  term_cols=$(pcbm_term_cols)
  max_width=$(( term_cols - 4 ))
  (( max_width > PCBM_MAX_WIDTH )) && max_width=$PCBM_MAX_WIDTH
  PCBM_WIDTH=$(pcbm_clamp "$desired_width" "$PCBM_MIN_WIDTH" "$max_width")

  prompt_lines=$(pcbm_count_lines "$prompt")
  desired_height=$(( item_count + prompt_lines + PCBM_HEIGHT_PADDING ))
  term_lines=$(pcbm_term_lines)
  max_height=$(( term_lines - 2 ))
  (( max_height > PCBM_MAX_HEIGHT )) && max_height=$PCBM_MAX_HEIGHT
  PCBM_HEIGHT=$(pcbm_clamp "$desired_height" "$PCBM_MIN_HEIGHT" "$max_height")

  list_height=$(( PCBM_HEIGHT - prompt_lines - 7 ))
  (( list_height < 3 )) && list_height=3
  (( list_height > item_count )) && list_height=$item_count
  (( list_height < 1 )) && list_height=1
  PCBM_MENU_SIZE=$list_height
}

pcbm_calc_checklist_dims() {
  local title="$1"
  local prompt="$2"
  shift 2
  local -a items=("$@")
  local item_count=$(( ${#items[@]} / 3 ))
  local max_tag=0 max_desc=0 max_prompt max_title max_hline desired_width
  local term_cols term_lines prompt_lines desired_height list_height tag desc i max_width max_height

  for ((i=0; i<${#items[@]}; i+=3)); do
    tag="${items[i]}"
    desc="${items[i+1]}"
    (( ${#tag} > max_tag )) && max_tag=${#tag}
    (( ${#desc} > max_desc )) && max_desc=${#desc}
  done

  max_prompt=$(pcbm_longest_line "$prompt")
  max_title=${#title}
  max_hline=${#PCBM_HLINE}
  desired_width=$(( max_tag + max_desc + PCBM_EXTRA_WIDTH + 6 ))
  (( max_prompt + 8 > desired_width )) && desired_width=$(( max_prompt + 8 ))
  (( max_title + 8 > desired_width )) && desired_width=$(( max_title + 8 ))
  (( max_hline + 4 > desired_width )) && desired_width=$(( max_hline + 4 ))

  term_cols=$(pcbm_term_cols)
  max_width=$(( term_cols - 4 ))
  (( max_width > PCBM_MAX_WIDTH )) && max_width=$PCBM_MAX_WIDTH
  PCBM_WIDTH=$(pcbm_clamp "$desired_width" "$PCBM_MIN_WIDTH" "$max_width")

  prompt_lines=$(pcbm_count_lines "$prompt")
  desired_height=$(( item_count + prompt_lines + PCBM_HEIGHT_PADDING + 1 ))
  term_lines=$(pcbm_term_lines)
  max_height=$(( term_lines - 2 ))
  (( max_height > PCBM_MAX_HEIGHT )) && max_height=$PCBM_MAX_HEIGHT
  PCBM_HEIGHT=$(pcbm_clamp "$desired_height" "$PCBM_MIN_HEIGHT" "$max_height")

  list_height=$(( PCBM_HEIGHT - prompt_lines - 8 ))
  (( list_height < 3 )) && list_height=3
  (( list_height > item_count )) && list_height=$item_count
  (( list_height < 1 )) && list_height=1
  PCBM_MENU_SIZE=$list_height
}

pcbm_calc_box_dims() {
  local text="$1"
  local min_width="$2"
  local max_width_cap="$3"
  local min_height="$4"
  local max_height_cap="$5"
  local longest lines term_cols term_lines max_width max_height

  longest=$(pcbm_longest_line "$text")
  lines=$(pcbm_count_lines "$text")
  term_cols=$(pcbm_term_cols)
  term_lines=$(pcbm_term_lines)

  max_width=$(( term_cols - 4 ))
  (( max_width > max_width_cap )) && max_width=$max_width_cap
  max_height=$(( term_lines - 2 ))
  (( max_height > max_height_cap )) && max_height=$max_height_cap

  PCBM_WIDTH=$(pcbm_clamp $(( longest + 8 )) "$min_width" "$max_width")
  PCBM_HEIGHT=$(pcbm_clamp $(( lines + 6 )) "$min_height" "$max_height")
}

pcbm_show_menu() {
  local title="$1"
  local prompt="$2"
  shift 2
  local -a items=("$@")
  prompt=$(pcbm_expand_text "$prompt")
  pcbm_calc_menu_dims "$title" "$prompt" "${items[@]}"
  PCBM_CHOICE=$(dialog --stdout --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --menu "$prompt" "$PCBM_HEIGHT" "$PCBM_WIDTH" "$PCBM_MENU_SIZE" \
    "${items[@]}")
  PCBM_STATUS=$?
  pcbm_cleanup_terminal
}

pcbm_show_checklist() {
  local title="$1"
  local prompt="$2"
  shift 2
  local -a items=("$@")
  prompt=$(pcbm_expand_text "$prompt")
  pcbm_calc_checklist_dims "$title" "$prompt" "${items[@]}"
  PCBM_CHOICE=$(dialog --stdout --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --checklist "$prompt" "$PCBM_HEIGHT" "$PCBM_WIDTH" "$PCBM_MENU_SIZE" \
    "${items[@]}")
  PCBM_STATUS=$?
  pcbm_cleanup_terminal
}

pcbm_show_msg() {
  local title="$1"
  local text="$2"
  text=$(pcbm_expand_text "$text")
  pcbm_calc_box_dims "$text" "$PCBM_BOX_MIN_WIDTH" "$PCBM_BOX_MAX_WIDTH" "$PCBM_BOX_MIN_HEIGHT" "$PCBM_BOX_MAX_HEIGHT"
  dialog --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --msgbox "$text" "$PCBM_HEIGHT" "$PCBM_WIDTH"
  pcbm_cleanup_terminal
}

pcbm_show_textbox() {
  local title="$1"
  local text="$2"
  local tmp status
  text=$(pcbm_expand_text "$text")
  pcbm_calc_box_dims "$text" "$PCBM_TEXTBOX_MIN_WIDTH" "$PCBM_TEXTBOX_MAX_WIDTH" "$PCBM_TEXTBOX_MIN_HEIGHT" "$PCBM_TEXTBOX_MAX_HEIGHT"
  tmp=$(mktemp)
  printf '%s\n' "$text" > "$tmp"
  dialog --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --scrollbar \
    --textbox "$tmp" "$PCBM_HEIGHT" "$PCBM_WIDTH"
  status=$?
  rm -f "$tmp"
  pcbm_cleanup_terminal
  return $status
}

pcbm_yesno() {
  local title="$1"
  local text="$2"
  text=$(pcbm_expand_text "$text")
  pcbm_calc_box_dims "$text" "$PCBM_BOX_MIN_WIDTH" "$PCBM_BOX_MAX_WIDTH" "$PCBM_BOX_MIN_HEIGHT" "$PCBM_BOX_MAX_HEIGHT"
  dialog --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --yesno "$text" "$PCBM_HEIGHT" "$PCBM_WIDTH"
  local status=$?
  pcbm_cleanup_terminal
  return $status
}

pcbm_infobox() {
  local title="$1"
  local text="$2"
  text=$(pcbm_expand_text "$text")
  pcbm_calc_box_dims "$text" 46 76 6 10
  dialog --clear \
    --backtitle "$PCBM_BACKTITLE" \
    --title "$title" \
    --hline "$PCBM_HLINE" \
    --infobox "$text" "$PCBM_HEIGHT" "$PCBM_WIDTH"
}

# Product contract 1 supplies the registry and preference authority. No shell eval.
pcbm_load_default_machine() {
  local fields
  PCBM_DEFAULT_ID= PCBM_DEFAULT_LABEL=Unavailable PCBM_PREFERENCE_STATUS=invalid
  fields=$(/usr/bin/pcbm-profiles default) || return 1
  IFS=$'\t' read -r PCBM_DEFAULT_ID PCBM_DEFAULT_LABEL PCBM_PREFERENCE_STATUS <<< "$fields"
  [[ -n $PCBM_DEFAULT_ID && -n $PCBM_DEFAULT_LABEL ]]
}

pcbm_default_machine() {
  /usr/bin/pcbm-profiles default --id-only
}

pcbm_default_machine_label() {
  pcbm_load_default_machine || return 1
  printf '%s\n' "$PCBM_DEFAULT_LABEL"
}

pcbm_emu_to_cover_tag() {
  /usr/bin/pcbm-profiles resolve "$1" --cover
}

pcbm_save_default_machine() {
  /usr/bin/pcbm-preferences set default_machine "$1" >/dev/null
}

pcbm_filtered_find() {
  local search_base="$1"
  shift

  find "$search_base" \
    \( -type d \( \
        -name '.*' -o \
        -name '__MACOSX' -o \
        -name '.Trashes' -o \
        -name '.Spotlight-V100' -o \
        -name '.fseventsd' \
      \) -prune \) -o \
    \( -type f \( \
        -name '.*' -o \
        -name '._*' -o \
        -name '.DS_Store' -o \
        -name '.AppleDouble' -o \
        -name '.LSOverride' -o \
        -name '.VolumeIcon.icns' -o \
        -name '.apdisk' -o \
        -name 'Thumbs.db' -o \
        -name 'desktop.ini' \
      \) -prune \) -o \
    "$@" -print0
}

pcbm_content_extensions() {
  cat <<'EXTS'
*.d64
*.d67
*.d71
*.d80
*.d81
*.d82
*.g64
*.g41
*.x64
*.p64
*.t64
*.tap
*.crt
*.prg
*.p00
*.sid
*.mus
*.bin
*.rom
*.reu
EXTS
}

pcbm_find_content_files() {
  local dir="$1"
  local expr=( )
  local pat first=1
  while IFS= read -r pat; do
    [[ -z "$pat" ]] && continue
    if (( first )); then
      expr+=( -iname "$pat" )
      first=0
    else
      expr+=( -o -iname "$pat" )
    fi
  done < <(pcbm_content_extensions)

  pcbm_filtered_find "$dir" -type f \( "${expr[@]}" \) | sort -z
}

pcbm_copy_clean() {
  local src="$1"
  local dest="$2"
  local base target path rel

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --ignore-existing --prune-empty-dirs \
      --exclude='.*' \
      --exclude='._*' \
      --exclude='.DS_Store' \
      --exclude='.AppleDouble' \
      --exclude='.LSOverride' \
      --exclude='.VolumeIcon.icns' \
      --exclude='.apdisk' \
      --exclude='__MACOSX/' \
      --exclude='.Trashes/' \
      --exclude='.Spotlight-V100/' \
      --exclude='.fseventsd/' \
      "$src" "$dest/"
    return $?
  fi

  if [[ -f "$src" ]]; then
    case "$(basename "$src")" in
      .* ) return 0 ;;
    esac
    cp -n "$src" "$dest/"
    return $?
  fi

  if [[ -d "$src" ]]; then
    base=$(basename "$src")
    target="$dest/$base"
    mkdir -p "$target" || return 1

    while IFS= read -r -d '' path; do
      rel="${path#$src/}"
      if [[ -d "$path" ]]; then
        mkdir -p "$target/$rel" || return 1
      elif [[ -f "$path" ]]; then
        mkdir -p "$(dirname "$target/$rel")" || return 1
        cp -n "$path" "$target/$rel" || return 1
      fi
    done < <(pcbm_filtered_find "$src" -mindepth 1 | sort -z)
    return 0
  fi

  return 1
}

pcbm_active_jiffydos() {
  local rom
  rom=$(cat "$PCBM_JIFFYDOS_CONF" 2>/dev/null)
  [[ -n "$rom" && -f "$rom" ]] && printf '%s\n' "$rom"
}

pcbm_launch_machine() {
  pcbm_cleanup_terminal
  /usr/bin/pcbm-boot "$1"
}

pcbm_launch_content() {
  local status=0
  pcbm_cleanup_terminal
  /usr/bin/pcbm-run-vice "$1" "$2" || status=$?
  if (( status != 0 )); then
    pcbm_show_msg "VICE Launch Failed" "VICE exited with status $status. For engineering diagnostics use tty2: pcbm-diagnostics"
  fi
  return "$status"
}
