"""Presentation/request encoding only; no Linux probes and no privilege execution."""
import json
import sys
from pcbm_info_view import parse, clean, object_value, render, wrap

FIELDS={'hostname':['value'],'locale':['value'],'timezone':['value'],'keyboard':['value'],
        'wifi-country':['value'],'network':['enabled'],'wifi-enroll':['ssid','password'],
        'sharing-password':['password'],'service':['service','enabled'],'modem':['port','baud'],'power':['action'],
        'setup-region':['locale','keyboard','timezone'],'setup-owner':['password'],
        'setup-network':['enabled'],'setup-finish':[], 'wifi-rescan':[], 'wifi-disconnect':[], 'wifi-forget':[]}
MESSAGES={'saved_restart': 'Keyboard layout saved. It applies after reboot; current console input is unchanged.', 'credentials_required':'Set a separate File Sharing password before enabling Samba.', 'ok':'Setting applied.','invalid':'Unsupported value. Check the setting and try again.',
          'pending':'Complete local first-boot setup before changing this setting.',
          'unavailable':'Required facility unavailable. Review System Information or Advanced guidance.',
          'failed':'The operation could not be confirmed. Review current state before retrying; part may have applied.',
          'busy':'Another configuration operation is running. Try again later.',
          'saved_pending':'Settings saved; runtime integration is pending. Service remains unchanged.'}


def about(data, columns=80):
    b=object_value(data.get('built_as'))
    lines=['ABOUT PROJECT CBM','A keyboard-first Commodore appliance for Raspberry Pi.',
           'Power on. Boot fast. Just Commodore.', '',
           'Project CBM: '+clean(b.get('product_version')),
           'Build: '+clean(b.get('build_id')),
           'Menu (built): '+clean(object_value(object_value(b.get('components')).get('menu')).get('version')), '',
           'Created and maintained by Craig Daters and Project CBM contributors.',
           'Inspired by Combian, by Carmelo Maiolino.',
           'Copyright Project CBM contributors. Project-owned code: MIT.',
           'Thanks to the VICE team, Raspberry Pi, Debian and the original Commodore engineers.',
           'VICE and Bash: GPL; dialog: LGPL; other components keep their own licenses.',
           'The Project CBM license does not relicense third-party ROMs, artwork or media.', '',
           'Project and support: https://github.com/cdaters/project-cbm',
           'Menu: https://github.com/cdaters/project-cbm-menu',
           'Detailed installed component notices: /usr/share/doc/<package>/copyright',
           'Build/release provenance is retained with the product release records.']
    if b.get('fixture') is True:lines.insert(1,'SYNTHETIC EXAMPLE - not a release')
    return '\n'.join(part for line in lines for part in wrap(line,max(14,min(columns,100)-6)))+'\n'


def main(argv):
    try:
        action=argv[0]
        raw=sys.stdin.buffer.read(65537)
        if len(raw)>65536:raise ValueError('size')
        if action=='request':
            op=argv[1];keys=FIELDS[op];values=raw.decode().splitlines() if keys else []
            if not keys and raw.strip():raise ValueError('unexpected_fields')
            if len(values)!=len(keys) or len(raw)>4096:raise ValueError('fields')
            d=dict(zip(keys,values))
            for k in d:
                if k=='enabled':
                    if d[k] not in ('true','false'):raise ValueError('boolean')
                    d[k]=d[k]=='true'
                if k in ('port','baud'):d[k]=int(d[k])
            print(json.dumps({'schema_version':1,'operation':op,'values':d}))
        elif action=='result':
            d=json.loads(raw)
            if not isinstance(d,dict):raise ValueError('contract')
            code=d.get('status')
            if d.get('format')!='project-cbm.config-result' or type(d.get('schema_version')) is not int or d['schema_version']!=1:raise ValueError('contract')
            print(MESSAGES[code]);return 0 if code in ('ok','saved_pending','saved_restart') else 2
        elif action=='import-list':
            d=json.loads(raw)
            if d['schema_version']!=1 or d['status']!='ok' or len(d['devices'])>16:raise ValueError('import')
            for row in d['devices']:
                import re
                if not re.fullmatch('[0-9a-f]{32}',row['token']) or not row['label'].isprintable() or len(row['label'])>128:raise ValueError('device')
                print(row['token']+'\t'+row['label'])
        elif action=='import-request':
            token,category=raw.decode().splitlines()
            import re
            if not re.fullmatch('[0-9a-f]{32}',token) or category not in ('games','demos','music','programs'):raise ValueError('import')
            print(json.dumps({'schema_version':1,'operation':'import','token':token,'category':category}))
        elif action=='import-result':
            d=json.loads(raw)
            if d['schema_version']!=1 or d['status']!='ok' or any(type(d[k]) is not int or d[k]<0 for k in ('copied','skipped','bytes')):raise ValueError('result')
            print(f"Copied {d['copied']} files ({d['bytes']} bytes); skipped {d['skipped']}. USB source unmounted. Find imported content through CONTENT.")
        elif action=='wifi-list':
            d=json.loads(raw)
            for i,row in enumerate(d['networks'][:32]):
                if not row['ssid'].isprintable() or len(row['ssid'].encode())>32:raise ValueError('ssid')
                print(str(i)+'\t'+row['ssid']+'\t'+str(row['signal_percent'])+'% '+row['security'])
        elif action=='about':print(about(parse(raw),int(argv[1]) if len(argv)>1 else 80),end='')
        else:raise ValueError('action')
        return 0
    except (ValueError,TypeError,KeyError,IndexError,UnicodeError,RecursionError):
        print('Project CBM information or request is unavailable.',file=sys.stderr);return 3


if __name__=='__main__':raise SystemExit(main(sys.argv[1:]))
