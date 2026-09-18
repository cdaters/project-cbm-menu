"""Presentation only: consume pcbm-info contract 1; never probe Linux or run a command."""
import argparse
import ipaddress
import re
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
    interfaces = c.get('network_interfaces')
    if isinstance(interfaces, list):
        result.append(('NETWORK INTERFACES', None))
        for item in interfaces[:32]:
            item = object_value(item)
            result.append((clean(item.get('interface')), clean(item.get('type')) + '; ' + clean(item.get('state')) + '; link ' + clean(item.get('operstate'))))
            result.append(('Current MAC', clean(item.get('mac'))))
            for family in ('ipv4', 'ipv6'):
                values = item.get(family)
                rendered = ', '.join(clean(v) for v in values[:8]) if isinstance(values, list) else UNKNOWN
                result.append((family.upper(), rendered or 'None assigned'))
            ssid = item.get('ssid')
            if ssid is not None:
                # Unlike path/identifier fields, SSIDs may contain a backslash.
                safe = ssid if isinstance(ssid, str) and 0 < len(ssid.encode('utf-8')) <= 32 and ssid.isprintable() else UNKNOWN
                result.append(('Wi-Fi SSID', safe))
        if not interfaces: result.append(('', 'No non-loopback interfaces observed'))
        result.append(('', 'Addresses and link state do not establish Internet access. IPv6 link-local addresses require the interface as their zone.'))
    elif 'network_interfaces' in c:
        result.append(('Interface addresses', UNKNOWN))
    service_rows=[]
    for key,label in [('samba','File Sharing'),('ssh','SSH'),('tcpser','BBS/Modem'),('avahi','mDNS')]:
        state=object_value(services.get(key))
        if not state:status=UNKNOWN
        elif state.get('LoadState')=='not-found':status='not installed'
        elif state.get('LoadState')=='masked' or state.get('UnitFileState')=='masked':status='unavailable in this profile'
        elif state.get('ActiveState')=='active':status='running'
        elif state.get('ActiveState')=='failed':status='failed'
        elif state.get('ActiveState')=='inactive':status='enabled but stopped' if state.get('UnitFileState')=='enabled' else 'off'
        else:status=UNKNOWN
        effective=object_value(object_value(c.get('appliance')).get('services')).get({'samba':'sharing','ssh':'ssh','tcpser':'modem','avahi':'discovery'}[key],{})
        status={'on':'On','off':'Off','pending':'Starting / Pending','unavailable':'Unavailable','failed':'Failed'}.get(effective.get('state'),status)
        service_rows.append(label+': '+status)
    result.append(('Services','; '.join(service_rows)))
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


def network_summary(raw):
    # Product's small projection uses the same collector as System Information.
    if len(raw)>65536: raise ValueError('size')
    data=json.loads(raw)
    if (not isinstance(data,dict) or data.get('format')!='project-cbm.network-info'
            or type(data.get('schema_version')) is not int or data['schema_version']!=1):
        raise ValueError('network_contract')
    entries=data.get('interfaces')
    if not isinstance(entries,list): return 'Network: information unavailable'
    if len(entries)>32: raise ValueError('interfaces')
    connected=[]
    for entry in entries:
        if not isinstance(entry,dict): raise ValueError('interface')
        if entry.get('state')!='connected': continue
        name=entry.get('interface')
        if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,15}',name):
            raise ValueError('interface_name')
        addresses=[]
        for key,version in [('ipv4',4),('ipv6',6)]:
            values=entry.get(key)
            if not isinstance(values,list) or len(values)>32: raise ValueError('addresses')
            for value in values:
                if not isinstance(value,str) or '%' in value: raise ValueError('address')
                address=ipaddress.ip_interface(value).ip
                if address.version!=version: raise ValueError('family')
                if address.is_unspecified or address.is_loopback or address.is_multicast: continue
                addresses.append(address)
        addresses.sort(key=lambda a:(a.is_link_local,a.version,int(a)))
        address=addresses[0] if addresses else None
        label={'ethernet':'Ethernet','wifi':'Wi-Fi'}.get(entry.get('type'),'Network')
        connected.append((label,name,address))
    if not connected:
        return 'Network: information unavailable' if data.get('issues') else 'Network: no connected interface'
    lines=[]
    for label,name,address in connected[:2]:
        if sum(row[0]==label for row in connected)>1: label+=' ('+name+')'
        value=str(address) if address else 'awaiting IP'
        if address and address.version==6 and address.is_link_local: value+='%'+name
        lines.append(label+': '+value)
    if len(connected)>2: lines[-1]+='; +'+str(len(connected)-2)+' more'
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--columns', type=int, default=80)
    parser.add_argument('--network-summary', action='store_true')
    args = parser.parse_args()
    try:
        raw=sys.stdin.buffer.read(65537)
        print(network_summary(raw) if args.network_summary else render(parse(raw), args.columns), end='\n' if args.network_summary else '')
        return 0
    except (ValueError, TypeError, RecursionError, UnicodeError):
        print('Project CBM information is unavailable. Return and try again.', file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
