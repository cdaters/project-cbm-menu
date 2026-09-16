"""Presentation only: consume pcbm-info contract 1; never probe Linux or run a command."""
import argparse
import json
import sys
import unicodedata

UNKNOWN = 'Unavailable'


def object_value(value):
    return value if isinstance(value, dict) else {}


def clean(value):
    if not isinstance(value, str) or not value or len(value) > 256:
        return UNKNOWN
    # Never render control sequences, raw paths or dialog formatting escapes.
    if not value.isprintable() or value.startswith('/') or '\\' in value:
        return UNKNOWN
    return value


def number(value):
    return value if type(value) in (int, float) and 0 <= value < 2**64 else None


def size(value):
    value = number(value)
    return UNKNOWN if value is None else f'{value / 1024**3:.2f} GiB'


def parse(raw):
    if len(raw) > 65536:
        raise ValueError('report_too_large')
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('duplicate')
            d[k] = v
        return d
    def invalid(_):
        raise ValueError('invalid_number')
    d = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    if not isinstance(d, dict) or d.get('format') != 'project-cbm.info' or type(d.get('schema_version')) is not int or d['schema_version'] != 1:
        raise ValueError('unsupported_contract')
    return d


def rows(data):
    b = object_value(data.get('built_as'))
    r = object_value(data.get('running_on'))
    c = object_value(data.get('current_state'))
    result = [('PROJECT CBM', None)]
    if b.get('fixture') is True:
        result.append(('', 'SYNTHETIC EXAMPLE - not a release'))
    result += [('Version', clean(b.get('product_version'))), ('Candidate', clean(b.get('candidate'))), ('Build', clean(b.get('build_id')))]
    packages = object_value(c.get('packages'))
    components = object_value(b.get('components'))
    for key, label in [('menu', 'Menu'), ('vice', 'VICE'), ('tcpser', 'TCPser')]:
        built = clean(object_value(components.get(key)).get('version'))
        current = object_value(packages.get(key))
        installed = current.get('installed')
        version = clean(current.get('version')) if installed is True else ('Not installed' if installed is False else UNKNOWN)
        result.append((label, f'{built} built; package {version}'))
    result += [('HARDWARE', None), ('Model', clean(r.get('model'))), ('Architecture', clean(r.get('architecture'))),
               ('Memory (usable)', size(object_value(r.get('memory')).get('usable_total_bytes')))]
    display = r.get('displays')
    summary = []
    if isinstance(display, list):
        for entry in display[:8]:
            entry = object_value(entry); mode = object_value(entry.get('active_mode'))
            w, h, hz = (number(mode.get(k)) for k in ('width', 'height', 'refresh_hz'))
            resolution = f'{int(w)}x{int(h)}' if w and h and w < 32769 and h < 32769 else 'mode unavailable'
            if hz and hz < 1001:
                resolution += f' @ {hz:g} Hz'
            summary.append(clean(entry.get('connector')) + ': ' + resolution)
    result.append(('Display', '; '.join(summary) if summary else ('None connected' if display == [] else UNKNOWN)))
    os_data = object_value(r.get('os')); disk = object_value(r.get('root_storage'))
    result += [('SYSTEM', None), ('OS', clean(os_data.get('pretty_name'))), ('Debian', clean(r.get('debian_version'))),
               ('Kernel', clean(r.get('kernel'))), ('Storage', f"{size(disk.get('total_bytes'))} total; {size(disk.get('available_bytes'))} available"),
               ('Hostname', clean(c.get('hostname')))]
    services = object_value(c.get('services')); net_service = object_value(services.get('network_manager'))
    links = c.get('network_links')
    if net_service.get('UnitFileState') in ('masked', 'disabled') and net_service.get('ActiveState') != 'active':
        network = 'Network management disabled'
    elif isinstance(links, list):
        network = '; '.join(clean(object_value(x).get('interface')) + ': ' + clean(object_value(x).get('operstate')) for x in links[:8]) or 'No links observed'
    else:
        network = UNKNOWN
    boot = object_value(c.get('boot_mode'))
    modes = {'menu': 'Menu', 'machine': 'Default machine', 'emulator': 'Default machine'}
    effective = modes.get(str(boot.get('effective')).lower())
    configured = modes.get(str(boot.get('configured')).lower())
    result += [('Network', network), ('CONFIGURATION', None), ('Default machine', clean(object_value(c.get('default_machine')).get('name'))),
               ('Boot mode', effective or (f'{configured} configured; active mode unavailable' if configured else UNKNOWN))]
    if object_value(c.get('preferences')).get('status') == 'invalid':
        result.append(('Preferences', 'Saved preferences need recovery; safe fallback in use'))
    if data.get('issues'):
        result.append(('', 'Some information is unavailable. Other details remain usable.'))
    return result


def cell_width(value):
    return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in ('W', 'F') else 1 for c in value)


def wrap(value, width):
    # Preserve every character of long IDs; wrap at spaces when practical.
    result = []
    while cell_width(value) > width:
        used = 0; end = 0
        for i, char in enumerate(value):
            used += cell_width(char)
            if used > width:
                break
            end = i + 1
        space = value.rfind(' ', 0, end + 1)
        if space > width // 2:
            end = space
        result.append(value[:end].rstrip()); value = value[end:].lstrip()
    return result + [value]


def render(data, columns=80):
    width = max(14, min(columns, 100) - 6)
    lines = []
    for label, value in rows(data):
        if value is None:
            if lines:
                lines.append('')
            lines += wrap(label, width)
        else:
            lines += wrap((label + ': ' if label else '') + value, width)
    lines += ['', *wrap('Up/Down or PgUp/PgDn scroll. Enter or Escape returns.', width)]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--columns', type=int, default=80)
    args = parser.parse_args()
    try:
        print(render(parse(sys.stdin.buffer.read(65537)), args.columns), end='')
        return 0
    except (ValueError, TypeError, RecursionError, UnicodeError):
        print('Project CBM information is unavailable. Return and try again.', file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
