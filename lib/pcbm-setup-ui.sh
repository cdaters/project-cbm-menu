#!/bin/bash
# Common appliance selections and Wi-Fi flow. Caller supplies request().
# No locale/radio probes or privileged writes in this presentation library.
pcbm_setup_choice() {
  local kind=$1 title value; local rows=()
  case $kind in
    region) title=Region;rows=(en_AU.UTF-8 "Australia — English" en_CA.UTF-8 "Canada — English" fr_CA.UTF-8 "Canada — French" fr_FR.UTF-8 "France — French" de_DE.UTF-8 "Germany — German" en_GB.UTF-8 "United Kingdom — English" en_US.UTF-8 "United States — English") ;;
    keyboard) title=Keyboard;rows=(us "English (US / Australia)" gb "English (UK)" ca "Canadian" fr "French" de "German") ;;
    timezone) title=Timezone;rows=(UTC "Coordinated Universal Time" America.Phoenix "Phoenix (Arizona)" America.New_York "New York (Eastern)" America.Chicago "Chicago (Central)" America.Denver "Denver (Mountain)" America.Los_Angeles "Los Angeles (Pacific)" America.Toronto "Toronto" America.Vancouver "Vancouver" Europe.London "London" Europe.Paris "Paris" Europe.Berlin "Berlin" Australia.Sydney "Sydney" Australia.Perth "Perth" Asia.Tokyo "Tokyo" Asia.Kolkata "Kolkata") ;;
    country) title="Wi-Fi country";rows=(AU "Australia" CA "Canada" FR "France" DE "Germany" GB "United Kingdom" US "United States") ;;
    *) return 3 ;;
  esac
  pcbm_ui_menu "$title" "Choose the setting for where you use this Pi. Advanced supports other configurations. Back returns without applying this screen." "${rows[@]}" ADVANCED "Advanced: enter an identifier" || return $?
  if [[ $PCBM_UI_CHOICE == ADVANCED ]]; then
    case $kind in
      region) value=en_GB.UTF-8 ;;
      keyboard) value=gb ;;
      timezone) value=UTC ;;
      country) value=GB ;;
    esac
    pcbm_ui_input "$title — Advanced" "Enter a supported $kind identifier (example: $value). Product validation checks it before applying." "" || return $?
  elif [[ $kind == timezone ]]; then PCBM_UI_CHOICE=${PCBM_UI_CHOICE//./\/};fi
}

pcbm_setup_wifi() {
  local prefix=$1 stage=country rows index name detail ssid secret rc
  local names=() choices=()
  while true; do
    case $stage in
      country)
        if ! pcbm_setup_choice country;then [[ $PCBM_UI_STATUS != back ]] || return 3;return 1;fi
        if request "${prefix}wifi-country" "$PCBM_UI_CHOICE";then stage=scan;fi ;;
      scan)
        if ! request "${prefix}wifi-rescan";then stage=recover;continue;fi
        pcbm_ui_working "Reading nearby Wi-Fi networks..." || return 3
        if ! rows=$(/usr/bin/pcbm-wifi-list | /usr/bin/python3 "$bridge" wifi-list);then
          pcbm_ui_message "Wi-Fi unavailable" "The network list could not be read safely. Retry, change country/radio settings, or stay offline." || true
          stage=recover;continue
        fi
        names=();choices=()
        while IFS=$'\t' read -r index name detail;do
          [[ -n $index ]] || continue
          names+=("$name");choices+=("$index" "$name ($detail)")
        done <<< "$rows"
        if (( ${#choices[@]}==0 ));then
          pcbm_ui_message "Wi-Fi" "No supported WPA-personal networks found. Retry the scan or check country/radio settings." || true
          stage=recover;continue
        fi
        if pcbm_ui_menu "Nearby Wi-Fi" "Select a network. Back returns to Wi-Fi country." "${choices[@]}";then
          ssid=${names[$PCBM_UI_CHOICE]};stage=password
        else [[ $PCBM_UI_STATUS != back ]] || return 3;stage=country;fi ;;
      password)
        if ! pcbm_ui_secret "Wi-Fi password" "Enter the password for $ssid (8–63 printable ASCII characters, including spaces and punctuation). Back selects another network.";then [[ $PCBM_UI_STATUS != back ]] || return 3;stage=scan;continue;fi
        secret=$PCBM_UI_CHOICE;PCBM_UI_CHOICE=
        if request "${prefix}wifi-enroll" "$ssid" "$secret";then unset secret;return 0;fi
        unset secret;stage=recover ;;
      recover)
        choices=()
        [[ -z ${ssid:-} ]] || choices+=(RETRY "Retry password for selected network")
        if ! pcbm_ui_menu "Wi-Fi not connected" "Choose how to continue. No Internet connection is required." "${choices[@]}" SCAN "Scan / choose another network" COUNTRY "Wi-Fi country and radio" OFFLINE "Stay Offline";then [[ $PCBM_UI_STATUS != back ]] || return 3;return 1;fi
        case $PCBM_UI_CHOICE in RETRY) stage=password ;; SCAN) stage=scan ;; COUNTRY) stage=country ;; OFFLINE) return 2 ;; esac ;;
    esac
  done
}
