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
#  Project CBM does not include or distribute copyrighted ROMs,
#  commercial software, disk images, or game collections.
#
# ---------------------------------------------------------------
#  Notice:
#  You may use, modify, and share this script under the project
#  license, but please preserve attribution where practical.
#
#  No warranty is provided. Use at your own risk.
# ================================================================
#
PCBM_VERSION_CONF="/etc/pcbm/version.conf"

if [[ -f "$PCBM_VERSION_CONF" ]]; then
  # shellcheck source=/etc/pcbm/version.conf
  source "$PCBM_VERSION_CONF"
else
  PCBM_PROJECT_NAME="Project CBM"
  PCBM_INTERNAL_NAME="pcbm"
  PCBM_VERSION="dev"
  PCBM_BUILD="local"
  PCBM_AUTHOR="Craig Daters"
  PCBM_REPO="https://github.com/cdaters/project-cbm"
  PCBM_TAGLINE="Power on. Boot fast. No nonsense. Just Commodore."
fi

PCBM_BACKTITLE="*** ${PCBM_PROJECT_NAME} v${PCBM_VERSION} - Raspberry Pi / Commodore machine distribution ***"
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
PCBM_CONTENT_BASE="/home/pi/pcbm"
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

pcbm_default_machine() {
  cat "$PCBM_DEFAULT_MACHINE_CONF" 2>/dev/null
}

pcbm_default_machine_label() {
  case "$(pcbm_default_machine)" in
    x64) echo "Commodore 64 (Fast)" ;;
    x64sc) echo "Commodore 64 (Recommended for games and demos)" ;;
    xscpu64) echo "Commodore 64 with CMD SuperCPU" ;;
    x64dtv) echo "Commodore 64 DTV" ;;
    x128) echo "Commodore 128 (40-column VIC display)" ;;
    x128-80col) echo "Commodore 128 (80-column VDC mode)" ;;
    xcbm2) echo "CBM-II" ;;
    xcbm5x0) echo "CBM-5x0" ;;
    xvic) echo "VIC-20" ;;
    xplus4) echo "Plus/4" ;;
    xpet) echo "PET" ;;
    *) echo "Not set" ;;
  esac
}

pcbm_machine_tag_to_emu() {
  case "$1" in
    C64) echo "x64" ;;
    C64SC) echo "x64sc" ;;
    SCPU64) echo "xscpu64" ;;
    C64DTV) echo "x64dtv" ;;
    C128) echo "x128" ;;
    C12880) echo "x128-80col" ;;
    CBM2) echo "xcbm2" ;;
    CBM5) echo "xcbm5x0" ;;
    VIC20) echo "xvic" ;;
    PET) echo "xpet" ;;
    PLUS4) echo "xplus4" ;;
    *) return 1 ;;
  esac
}

pcbm_emu_to_machine_tag() {
  case "$1" in
    x64) echo "C64" ;;
    x64sc) echo "C64SC" ;;
    xscpu64) echo "SCPU64" ;;
    x64dtv) echo "C64DTV" ;;
    x128) echo "C128" ;;
    x128-80col) echo "C12880" ;;
    xcbm2) echo "CBM2" ;;
    xcbm5x0) echo "CBM5" ;;
    xvic) echo "VIC20" ;;
    xpet) echo "PET" ;;
    xplus4) echo "PLUS4" ;;
    *) return 1 ;;
  esac
}

pcbm_emu_to_cover_tag() {
  case "$1" in
    x64|x64sc|xscpu64|x64dtv)
      echo "c64"
      ;;
    x128|x128-80col)
      echo "c128"
      ;;
    xcbm2)
      echo "cbm2"
      ;;
    xcbm5x0)
      echo "cbm5"
      ;;
    xvic)
      echo "vic20"
      ;;
    xpet)
      echo "pet"
      ;;
    xplus4)
      echo "plus4"
      ;;
    *)
      return 1
      ;;
  esac
}

pcbm_save_default_machine() {
  local emu="$1"
  if ! sudo -n mkdir -p "$PCBM_CONFIG_DIR" 2>/dev/null; then
    pcbm_show_msg "Permission Required" "Project CBM could not create $PCBM_CONFIG_DIR without sudo.\n\nAdd a passwordless sudo rule for mkdir and tee, or create the file manually."
    return 1
  fi

  if ! printf '%s\n' "$emu" | sudo -n tee "$PCBM_DEFAULT_MACHINE_CONF" >/dev/null 2>&1; then
    pcbm_show_msg "Permission Required" "Project CBM could not save the default machine.\n\nAdd a passwordless sudo rule for /usr/bin/tee or save the file manually:\n$PCBM_DEFAULT_MACHINE_CONF"
    return 1
  fi
  return 0
}

pcbm_service_active() {
  local service="$1"
  if systemctl list-unit-files "$service.service" >/dev/null 2>&1 || systemctl status "$service" >/dev/null 2>&1; then
    systemctl is-active "$service" 2>/dev/null || echo "inactive"
  else
    echo "not installed"
  fi
}

pcbm_hostname() {
  hostname 2>/dev/null || echo "unknown"
}

pcbm_ip_address() {
  hostname -I 2>/dev/null | awk '{print $1}'
}

pcbm_gateway() {
  ip route 2>/dev/null | awk '/default/ {print $3; exit}'
}

pcbm_dns_server() {
  awk '/^nameserver/ {print $2}' /etc/resolv.conf | paste -sd ','
}

pcbm_mount_usb_first_partition() {
  local dev

  if [[ ! -d "$PCBM_USB_MOUNT" ]]; then
    sudo -n mkdir -p "$PCBM_USB_MOUNT" || {
      echo ""
      return 2
    }
  fi

  dev=$(lsblk -rpno NAME,RM,TYPE | awk '$2==1 && $3=="part" {print $1; exit}')
  if [[ -z "$dev" ]]; then
    echo ""
    return 1
  fi

  if ! sudo -n mount "$dev" "$PCBM_USB_MOUNT" 2>/dev/null; then
    echo ""
    return 2
  fi

  echo "$dev"
  return 0
}

pcbm_unmount_usb() {
  sudo -n umount "$PCBM_USB_MOUNT" >/dev/null 2>&1 || true
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
  local emu="$1"
  local machine_tag

  # machine_tag=$(pcbm_emu_to_machine_tag "$emu" | tr '[:upper:]' '[:lower:]')
  machine_tag=$(pcbm_emu_to_cover_tag "$emu")

  pcbm_cleanup_terminal

  if command -v /usr/local/bin/pcbm-cover >/dev/null 2>&1; then
    /usr/local/bin/pcbm-cover "$machine_tag"
  fi

  /usr/local/bin/pcbm-boot "$emu"
}

pcbm_launch_content() {
  local emu="$1"
  local file="$2"
  local active_rom
  local emu_bin="$emu"
  local status=0
  local -a cmd extra_args

  case "$emu" in
    x128-80col)
      emu_bin="x128"
      extra_args=("-80col")
      ;;
  esac

  if ! command -v "$emu_bin" >/dev/null 2>&1; then
    pcbm_show_msg "Emulator Missing" "Project CBM could not find the emulator binary: $emu_bin"
    return 1
  fi

  export HOME="/home/pi"
  export XDG_CONFIG_HOME="$HOME/.config"
  export XDG_STATE_HOME="$HOME/.local/state"
  export XDG_DATA_HOME="$HOME/.local/share"

  mkdir -p \
    "$XDG_CONFIG_HOME/vice" \
    "$XDG_STATE_HOME/vice" \
    "$XDG_DATA_HOME/vice"

  cmd=("$emu_bin" "${extra_args[@]}" "-sounddev" "sdl" "-autostart" "$file")
  active_rom=$(pcbm_active_jiffydos)
  if [[ "$emu_bin" == "x64sc" && -n "$active_rom" ]]; then
    cmd=("$emu_bin" "-kernal" "$active_rom" "${extra_args[@]}" "-sounddev" "sdl" "-autostart" "$file")
  fi

  : >"$PCBM_VICE_LOG"
  pcbm_cleanup_terminal
  # Refresh ALSA's default output before launching content.
  # This keeps content launches aligned with the same HDMI auto-detection path as machine launches.
  if command -v /usr/local/bin/pcbm-audio >/dev/null 2>&1; then
    /usr/local/bin/pcbm-audio auto --quiet >>"$PCBM_VICE_LOG" 2>&1 || true
  fi

  /usr/bin/env \
    HOME="$HOME" \
    XDG_CONFIG_HOME="$XDG_CONFIG_HOME" \
    XDG_STATE_HOME="$XDG_STATE_HOME" \
    XDG_DATA_HOME="$XDG_DATA_HOME" \
    SDL_AUDIODRIVER=alsa \
    "${cmd[@]}" </dev/tty >"$PCBM_VICE_LOG" 2>&1

  status=$?

  if (( status != 0 )); then
    pcbm_show_msg "VICE Launch Failed" "Project CBM could not launch the selected content.\n\nSee log:\n$PCBM_VICE_LOG"
  fi

  return $status
}
