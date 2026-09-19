import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
import pcbm_status_view as s

def fixture():
    return {'format':'project-cbm.appliance-info','schema_version':1,'computer_name':'projectcbm','owner_username':'pcbm','sharing_username':'pcbm','sharing_password_set':False,'share_name':'Project CBM','interfaces':[],'issues':[],'modem_port':25232,'services':{n:{'state':'off','enabled':False,'listening':False} for n in s.LABELS}}

def nic(kind='ethernet',ip='192.0.2.12/24',name='enp9s4'):
    return {'interface':name,'type':kind,'state':'connected','operstate':'up','mac':'02:00:00:00:00:01','ipv4':[ip],'ipv6':[],'ssid':None}

class Status(unittest.TestCase):
    def test_off_on_pending_failed_unavailable_actions(self):
        d=fixture()
        for state,enabled,tags in [('off',False,['ENABLE']),('on',True,['DISABLE']),('pending',True,['DISABLE']),('pending',False,[]),('failed',True,['DISABLE']),('failed',False,['ENABLE']),('unavailable',False,[])]:
            d['services']['ssh'].update(state=state,enabled=enabled)
            self.assertEqual([x[0] for x in s.actions(d,'ssh')],tags)
            self.assertIn(s.STATES[state],s.view(d,'ssh'))
    def test_offline_main_is_compact(self):
        self.assertIn('Network',s.summary(fixture()));self.assertNotIn('File Sharing',s.summary(fixture()))
    def test_multiple_interfaces_and_active_services(self):
        d=fixture();d['interfaces']=[nic(),nic('wifi','198.51.100.4/24','wlx123')]
        d['services']['sharing'].update(state='on',enabled=True,listening=True)
        out=s.summary(s.parse(json.dumps(d)))
        for value in ('192.0.2.12','198.51.100.4','File Sharing: On'):self.assertIn(value,out)
        self.assertNotIn('02:00:',out)
    def test_network_hierarchy_and_ssid_control_safety(self):
        d=fixture();d['interfaces']=[nic('wifi')];d['interfaces'][0]['ssid']='Room\\Z1'
        out=s.view(d,'network');self.assertIn('Computer Name: projectcbm',out);self.assertNotIn('\\Z',out)
    def test_ssh_username_secret_guidance_ip_and_mdns(self):
        d=fixture();d['interfaces']=[nic()]
        self.assertIn('ssh pcbm@192.0.2.12',s.connection(d,'ssh'))
        d['services']['discovery']['state']='on'
        self.assertIn('ssh pcbm@projectcbm.local',s.connection(d,'ssh'))
        self.assertIn('first-boot owner password',s.connection(d,'ssh'))
    def test_smb_separate_password_real_share_and_paths(self):
        d=fixture();d['interfaces']=[nic()];out=s.connection(d,'sharing')
        for value in ('separate password','smb://192.0.2.12/Project%20CBM','pcbm','Project CBM'):self.assertIn(value,out)
    def test_ipv6_only_connection(self):
        d=fixture();row=nic();row.update(ipv4=[],ipv6=['2001:db8::1/64']);d['interfaces']=[row]
        self.assertIn('ssh pcbm@2001:db8::1',s.connection(d,'ssh'))
        self.assertIn('smb://[2001:db8::1]/',s.connection(d,'sharing'))
    def test_secret_extras_never_rendered(self):
        d=fixture();d['password']='fixture-do-not-output';d['services']['ssh']['private']='fixture-do-not-output'
        for name in s.LABELS:self.assertNotIn('fixture-do-not-output',s.connection(s.parse(json.dumps(d)),name))
    def test_invalid_identifiers_types_control_sequences_rejected(self):
        for key,value in [('computer_name','bad\nname'),('owner_username','$(id)'),('modem_port','\x1b[31m'),('sharing_password_set',1)]:
            d=fixture();d[key]=value
            with self.assertRaises(ValueError):s.parse(json.dumps(d))
        d=fixture();d['services']['ssh']['enabled']=1
        with self.assertRaises(ValueError):s.parse(json.dumps(d))
    def test_no_network_commands_in_formatter(self):
        text=(Path(s.__file__)).read_text()
        for value in ('subprocess','socket.','nmcli','systemctl','ip -'):self.assertNotIn(value,text)
