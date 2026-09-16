"""Presentation/request encoding only; no Linux probes and no privilege execution."""
import json
import sys
from pcbm_info_view import parse, clean, object_value, render, wrap

FIELDS={'hostname':['value'],'locale':['value'],'timezone':['value'],'keyboard':['value'],
        'wifi-country':['value'],'network':['enabled'],'wifi-enroll':['ssid','password'],
        'sharing-password':['password'],'service':['service','enabled'],'modem':['port','baud'],'power':['action']}
MESSAGES={'saved_restart': 'Keyboard layout saved. It applies after reboot; current console input is unchanged.', 'credentials_required':'Set a separate File Sharing password before enabling Samba.', 'ok':'Setting applied.','invalid':'Unsupported value. Check the setting and try again.',
          'pending':'Pending runtime activation: first-boot account and service setup must finish in a future candidate.',
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
            op=argv[1];values=raw.decode().splitlines();keys=FIELDS[op]
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
        elif action=='about':print(about(parse(raw),int(argv[1]) if len(argv)>1 else 80),end='')
        else:raise ValueError('action')
        return 0
    except (ValueError,TypeError,KeyError,IndexError,UnicodeError,RecursionError):
        print('Project CBM information or request is unavailable.',file=sys.stderr);return 3


if __name__=='__main__':raise SystemExit(main(sys.argv[1:]))
