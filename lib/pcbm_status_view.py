"""Appliance presentation only; Product JSON owns every runtime observation."""
import argparse
import ipaddress
import json
import re
import sys
from pcbm_info_view import network_summary, route_values

LABELS={'ssh':'Remote Access (SSH)','sharing':'File Sharing','discovery':'Network Discovery','modem':'BBS / Modem'}
STATES={'off':'Off','on':'On','pending':'Starting / Pending','unavailable':'Unavailable','failed':'Failed'}


def parse(raw):
    if len(raw)>65536:raise ValueError('size')
    d=json.loads(raw)
    if not isinstance(d,dict) or d.get('format')!='project-cbm.appliance-info' or type(d.get('schema_version')) is not int or d['schema_version']!=1:raise ValueError('contract')
    for key,pattern in [('computer_name',r'[a-z][a-z0-9-]{0,61}[a-z0-9]|[a-z]'),('owner_username',r'[a-z][a-z0-9_-]{0,30}'),('sharing_username',r'[a-z][a-z0-9_-]{0,30}')]:
        v=d.get(key)
        if v is not None and (not isinstance(v,str) or not re.fullmatch(pattern,v)):raise ValueError('identifier')
    if type(d.get('sharing_password_set')) is not bool or d.get('share_name')!='Project CBM':raise ValueError('sharing')
    for key in LABELS:
        row=d['services'][key]
        if row.get('state') not in STATES or type(row.get('enabled')) not in (bool,type(None)) or type(row.get('listening')) not in (bool,type(None)):raise ValueError('service')
    if type(d.get('modem_port')) is not int or not 1024<=d['modem_port']<=65535:raise ValueError('port')
    # Validate all displayed addresses through the existing strict formatter.
    network(d)
    return d


def network(d):
    return network_summary(json.dumps({'format':'project-cbm.network-info','schema_version':1,'interfaces':d.get('interfaces'),'issues':d.get('issues',[])}))


def status(d,name):return STATES[d['services'][name]['state']]


def actions(d,name):
    row=d['services'][name];state=row['state']
    if state=='off':return [('ENABLE','Turn On '+LABELS[name])]
    if state=='on':return [('DISABLE','Turn Off '+LABELS[name])]
    if state=='pending':return [('DISABLE','Turn Off '+LABELS[name])] if row['enabled'] else []
    if state=='failed':return [('DISABLE','Turn Off '+LABELS[name])] if row['enabled'] else [('ENABLE','Try Turning On '+LABELS[name])]
    return []


def summary(d):
    active=[LABELS[n]+': '+status(d,n) for n in ('sharing','ssh','modem') if d['services'][n]['state'] not in ('off','unavailable')]
    return network(d)+ ('\n'+' | '.join(active) if active else '')


def view(d,area):
    computer=d.get('computer_name') or 'unavailable'
    if area=='main':return summary(d)
    if area=='services':return '\n'.join(LABELS[n]+': '+status(d,n) for n in LABELS)
    lines=['Computer Name: '+computer,network(d)]
    if area=='network':
        for row in d.get('interfaces') or []:
            if row.get('state')=='connected':
                label=row.get('interface','Interface')
                if not isinstance(label,str) or not re.fullmatch('[A-Za-z0-9_.:-]{1,15}',label):label='Interface'
                for key,title in [('gateway_ipv4','IPv4 gateway'),('gateway_ipv6','IPv6 gateway'),('dns_ipv4','IPv4 DNS'),('dns_ipv6','IPv6 DNS')]:
                    lines.append(label+' '+title+': '+route_values(row.get(key)))
            ssid=row.get('ssid')
            if row.get('state')=='connected' and row.get('type')=='wifi' and isinstance(ssid,str) and ssid.isprintable() and len(ssid.encode())<=32:
                # Dialog literal data; suppress slash escapes in network-owned labels.
                lines.append('Wi-Fi network: '+ssid.replace('\\','?'))
        lines.append('Network Discovery: '+status(d,'discovery'))
        return '\n'.join(lines)
    lines.insert(0,'Status: '+status(d,area))
    if area in ('ssh','sharing'):
        lines.append('Username: '+(d.get('owner_username' if area=='ssh' else 'sharing_username') or 'unavailable'))
        lines.append('Password: your first-boot owner password' if area=='ssh' else 'Separate File Sharing password: '+('Set' if d['sharing_password_set'] else 'Not set'))
    if area=='sharing':lines.append('Network Discovery: '+status(d,'discovery'))
    if area=='discovery':lines.append('Local names and File Sharing discovery; no Internet access required.')
    return '\n'.join(lines)


def connection(d,name):
    computer=d.get('computer_name')
    discovery=d['services']['discovery']['state']=='on'
    targets=[]
    if computer and discovery:targets.append(computer+'.local')
    for row in d.get('interfaces') or []:
        if row.get('state')!='connected':continue
        for value in row.get('ipv4',[])+row.get('ipv6',[]):
            address=ipaddress.ip_interface(value).ip
            if not address.is_loopback and not address.is_link_local and not address.is_unspecified:targets.append(str(address))
    target=targets[0] if targets else None
    lines=[view(d,name),'']
    if name=='ssh':
        user=d.get('owner_username')
        lines+=['Use the owner password chosen during first boot.','From another computer:']
        lines.append('ssh '+user+'@'+target if target and user else 'Connect a network, then return here for an SSH command.')
    elif name=='sharing':
        lines+=['File Sharing uses a separate password set on this screen.','Share: Project CBM']
        if target:
            lines+=['Mac Finder > Go > Connect to Server:', 'smb://'+('['+target+']' if ':' in target else target)+'/Project%20CBM','Windows File Explorer address:', '\\\\'+(target.replace(':','-')+'.ipv6-literal.net' if ':' in target else target)+'\\Project CBM']
        else:lines+=['Connect a network, then return here for connection addresses.']
        lines+=['Sign in as '+(d.get('sharing_username') or 'the displayed username')+'.','Library: /home/pcbm/content. Files appear in CONTENT and FILES.','Windows Network browsing is not guaranteed; use the direct address.']
    elif name=='discovery':
        lines+=['When On, try '+computer+'.local.' if computer else 'Computer Name is unavailable.','File Sharing advertises itself to compatible Mac/Linux browsers.','If a name does not resolve, use the current IP.','Windows browsing varies; direct File Explorer access is supported.']
    else:
        lines+=['Local emulator modem: 127.0.0.1:'+str(d.get('modem_port',25232)), 'Use an owner-authorized BBS endpoint. This is not a public modem server.']
    if computer and not discovery:lines+=['Network Discovery is Off/unavailable; use an IP or turn it on.']
    if len(targets)>1:lines+=['Other current addresses: '+', '.join(targets[1:4])]
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['view','actions','connection','field']);p.add_argument('area');a=p.parse_args()
    try:
        d=parse(sys.stdin.buffer.read(65537))
        if a.mode=='view':print(view(d,a.area))
        elif a.mode=='connection':print(connection(d,a.area))
        elif a.mode=='actions':
            for tag,label in actions(d,a.area):print(tag+'\t'+label)
        elif a.area=='sharing_password_set':print('yes' if d[a.area] else 'no')
        else:raise ValueError('field')
    except (ValueError,KeyError,TypeError):return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
