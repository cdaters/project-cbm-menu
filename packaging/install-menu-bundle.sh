#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Run with sudo: sudo ./packaging/install-menu-bundle.sh" >&2
  exit 1
fi

install -d -m 755 /etc/pcbm /usr/local/bin /opt/pcbm/covers
install -m 644 "$ROOT_DIR/configs/version.conf" /etc/pcbm/version.conf
install -m 644 "$ROOT_DIR/configs/default-machine.conf.example" /etc/pcbm/default-machine.conf
install -m 644 "$ROOT_DIR/configs/boot-mode.conf.example" /etc/pcbm/boot-mode.conf
install -m 755 "$ROOT_DIR/configs/99-pcbm" /etc/update-motd.d/99-pcbm
install -m 440 "$ROOT_DIR/configs/pcbm-sudoers.example" /etc/sudoers.d/pcbm
visudo -cf /etc/sudoers.d/pcbm

for f in "$ROOT_DIR"/scripts/*; do
  [[ -f "$f" ]] || continue
  install -m 755 "$f" "/usr/local/bin/$(basename "$f")"
done

if [[ -d "$ROOT_DIR/covers" ]]; then
  install -m 644 "$ROOT_DIR"/covers/* /opt/pcbm/covers/ 2>/dev/null || true
fi

chown -R pi:pi /opt/pcbm 2>/dev/null || true

echo "Project CBM menu files installed. Review /etc/pcbm/version.conf, Samba, and boot integration before imaging."
