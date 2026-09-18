"""Synthetic IP summary contracts; no local probes or credentials."""
import importlib.util,json,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('view',Path(__file__).resolve().parents[1]/'lib/pcbm_info_view.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def row(name='enxfixture',kind='ethernet',address='192.0.2.3/24',state='connected'):
 return {'interface':name,'type':kind,'state':state,'ipv4':[address] if ':' not in address and address else [],'ipv6':[address] if ':' in address else []}
def summary(rows,issues=[]):
 return v.network_summary(json.dumps({'format':'project-cbm.network-info','schema_version':1,'interfaces':rows,'issues':issues}))
class Summary(unittest.TestCase):
 def test_none_and_unavailable(self):
  self.assertEqual(summary([]),'Network: no connected interface')
  self.assertEqual(summary([row(state='disconnected')]),'Network: no connected interface')
  self.assertEqual(summary(None),'Network: information unavailable')
 def test_ethernet_wifi_and_pending_ip(self):
  self.assertEqual(summary([row()]),'Ethernet: 192.0.2.3')
  self.assertEqual(summary([row('wlxfixture','wifi')]),'Wi-Fi: 192.0.2.3')
  self.assertEqual(summary([row(address='')]),'Ethernet: awaiting IP')
 def test_multiple_interfaces_and_bounded_display(self):
  value=summary([row(),row('radio2','wifi','192.0.2.4/24'),row('bridge2','bridge')])
  self.assertEqual(value,'Ethernet: 192.0.2.3\nWi-Fi: 192.0.2.4; +1 more')
  self.assertIn('(enxfixture)',summary([row(),row('enxsecond')]))
 def test_ipv6_global_preferred_and_linklocal_zone(self):
  r=row(address='fe80::2/64');r['ipv6'].append('2001:db8::1/64')
  self.assertEqual(summary([r]),'Ethernet: 2001:db8::1')
  self.assertEqual(summary([row(address='fe80::2/64')]),'Ethernet: fe80::2%enxfixture')
 def test_escape_payloads_rejected_and_extra_private_fields_ignored(self):
  for r in [row(name='bad\\Z1'),row(address='bad\x1b'),row(address='192.0.2.1%bad/24')]:
   with self.assertRaises(ValueError):summary([r])
  r={**row(),'ssid':'private-network','password':'synthetic secret','mac':'02:00:00:00:00:01'}
  self.assertEqual(summary([r]),'Ethernet: 192.0.2.3')
 def test_menu_consumes_only_product_projection(self):
  text=(Path(__file__).resolve().parents[1]/'scripts/pcbm-menu').read_text()
  self.assertIn('pcbm-info --json --appliance',text)
  for probe in ['nmcli','hostname -I','ip address','ifconfig']:self.assertNotIn(probe,text)
if __name__=='__main__':unittest.main()
