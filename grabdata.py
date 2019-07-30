import boto3
import sys
import xml.etree.ElementTree as ET

def main():
    if len(sys.argv) < 9:
        print('Usage: python grabdata.py {username, password, hostname, localgw, prefix, vpnid, region, workload_name}\n')
        sys.exit(0)
# data to pass in:
# 1. username: login username
# 2. password: login password
# 3. hostname: desired hostname
# 4. localgw: private ip of the fortigate firewall port3
# 5. prefix: cidr block of the source vpc, typically just 192.168.0.0/24
# 6. vpnid: vpn id of the established vpn connection
# 7. region: region that the vpc connecting to fw is in

    else:
        username = sys.argv[1]
        password = sys.argv[2]
        hostname = sys.argv[3]
        phase_1_localgw = sys.argv[4]
        router_bgp_network_prefix = sys.argv[5]
        vpnid = sys.argv[6]
        regionid = sys.argv[7]
        wkldname = str(sys.argv[8])
# get config data from aws
    client = boto3.client('ec2', region_name=regionid)
    data = client.describe_vpn_connections()
# find the correct vpn connection to write to xml
    for conns in data['VpnConnections']:
        if 'CustomerGatewayConfiguration' in conns.keys():
            if vpnid in conns['CustomerGatewayConfiguration']:
                with open ('firstpart.xml', 'w') as f:
                    f.write(conns['CustomerGatewayConfiguration'])
                    f.close()
# parse the tree
    tree = ET.parse('firstpart.xml')
    root = tree.getroot()
    host = root[3][0][0][0].text
    system_int_ip = root[3][0][1][0].text
    system_int_cidr = root[3][0][1][2].text
    system_int_remote_ip = root[3][1][1][0].text
    system_int_remote_cidr = root[3][1][1][2].text
    phase_1_keylife = root[3][2][2].text
    phase_1_remotegw = root[3][1][0][0].text
    phase_1_psksecret = root[3][2][5].text
    phase_1_retryint = root[3][3][9][0].text
    system_int_type = root[3][3][5].text
    phase_1_mode = root[3][2][4].text
    phase_2_keylife = root[3][3][3].text
    router_bgp_as = root[3][0][2][0].text
    router_bgp_ip = root[3][1][1][0].text
    router_bgp_remote = root[3][1][2][0].text
    router_bgp_network_id = host
    router_bgp_router_id = host
    system_zone_name = "Public"
# hard coding the configs that are not
# available from data previous from aws
# issue: default proposal aes-128 is not
# available in ansible fortios module.
    vdom = "root"
    timezone = "04"
    system_alias = "FW name"
    system_int_name = vpnid[0:13]
    system_int_state = "present"
    system_zone_int_name = system_int_name
    system_zone_state = "present"
    phase_1_dpd = "on-demand"
    phase_1_dhgrp = "2"
    phase_1_proposal= "aes128-sha1"
    phase_1_int = "port3"
    phase_1_name = system_int_name
    phase_1_ike = "1"
    phase_1_authmethod = "psk"
    phase_1_type = "static"
    phase_1_encap = "none"
    phase_1_encap_addr = "ike"
    phase_1_modecfg = "disable"
    phase_1_acct_verify = "enable"
    phase_2_dhgrp = phase_1_dhgrp
    phase_2_pfs = "enable"
    phase_2_int_name = "phase_2_intf"
    phase_2_state = "present"
    router_bgp_capability_default_originate = "enable"
    policy_src_intf = "Public"
    policy_action = "accept"
    policy_state = "present"
    policy_status = "enable"
    policy_src_addr_in = "all"
    policy_dst_addr_in = "all"
    policy_service_in = "ALL"
    policy_src_addr_out = "all"
    policy_dst_addr_out = "all"
    policy_service_out = "ALL"
    #!!! this config will overwrite any policy with id=policy_id
    policy_id_in = "69"
    policy_id_out = "96"
    # put the hard coded part above to the variable yml file 
    hardcode = (
        'vdom: "'+vdom+'"\n'
        'timezone: "'+timezone+'"\n'
        'system_alias: "'+system_alias+'"\n'
        'system_int_name: "'+system_int_name+'"\n'
        'system_zone_int_name: "'+system_zone_int_name+'"\n'
        'phase_1_dpd: "'+phase_1_dpd+'"\n'
        'phase_1_dhgrp: "'+phase_1_dhgrp+'"\n'
        'phase_1_proposal: "'+phase_1_proposal+'"\n'
        'phase_1_int: "'+phase_1_int+'"\n'
        'phase_1_name: "'+phase_1_name+'"\n'
        'phase_1_ike: "'+phase_1_ike+'"\n'
        'phase_1_authmethod: "'+phase_1_authmethod+'"\n'
        'phase_1_type: "'+phase_1_type+'"\n'
        'phase_1_encap: "'+phase_1_encap+'"\n'
        'phase_1_encap_addr: "'+phase_1_encap_addr+'"\n'
        'phase_1_modecfg: "'+phase_1_modecfg+'"\n'
        'phase_2_dhgrp: "'+phase_2_dhgrp+'"\n'
        'phase_2_pfs: "'+phase_2_pfs+'"\n'
        'phase_2_int_name: "'+phase_2_int_name+'"\n'
        'router_bgp_capability_default_originate: "'+router_bgp_capability_default_originate+'"\n'
        'policy_src_intf: "'+policy_src_intf+'"\n'
        'policy_id_in: "'+policy_id_in+'"\n'
        'policy_id_out: "'+policy_id_out+'"\n'
        'system_int_state: "'+system_int_state+'"\n'
        'system_zone_state: "'+system_zone_state+'"\n'
        'phase_1_acct_verify: "'+phase_1_acct_verify+'"\n'
        'phase_2_state: "'+phase_2_state+'"\n'
        'policy_action: "'+policy_action+'"\n'
        'policy_state: "'+policy_state+'"\n'
        'policy_status: "'+policy_status+'"\n'
        'policy_src_addr_in: "'+policy_src_addr_in+'"\n'
        'policy_dst_addr_in: "'+policy_dst_addr_in+'"\n'
        'policy_service_in: "'+policy_service_in+'"\n'
        'policy_src_addr_out: "'+policy_src_addr_out+'"\n'
        'policy_dst_addr_out: "'+policy_dst_addr_out+'"\n'
        'policy_service_out: "'+policy_service_out+'"\n'
        
)
    # needs to munually input this config through cli because fortios does not 
    # currently have a module for route-map configuration 
    manual = ('config router prefix-list\n'
        ' edit "default_route"\n'
        '  config rule\n'
        '   edit 1\n'
        '    set prefix 0.0.0.0 0.0.0.0\n'
        '   next\n'
        '  end\n'
        'end\n\n'
        'config router route-map\n'
        ' edit "routemap1"\n'
        '  config rule\n'
        '   edit 1\n'
        '    set match-ip-address "default_route"\n'
        '   next\n'
        '  end\n'
        ' next\n'
        'end\n')
    with open ('manual.txt','w') as f:
        f.write(manual)
        f.close()
# write the variables to desired yml file.
    with open ('vars.yml', 'w') as f:
        f.write('host: "'+host+'"\n')
        f.write('system_int_ip: "'+system_int_ip+'/32'+'"\n')
        f.write('system_int_remote_ip: "'+system_int_remote_ip+'/'+system_int_remote_cidr+'"\n')
        f.write('system_zone_name: "'+system_zone_name+'"\n')
        f.write('phase_1_keylife: "'+phase_1_keylife+'"\n')
        f.write('phase_1_remotegw: "'+phase_1_remotegw+'"\n')
        f.write('phase_1_psksecret: "'+phase_1_psksecret+'"\n')
        f.write('phase_1_retryint: "'+phase_1_retryint+'"\n')
        f.write('system_int_type: "'+system_int_type+'"\n')
        f.write('phase_1_mode: "'+phase_1_mode+'"\n')
        f.write('phase_2_keylife: "'+phase_2_keylife+'"\n')
        f.write('router_bgp_as: "'+router_bgp_as+'"\n')
        f.write('router_bgp_ip: "'+router_bgp_ip+'"\n')
        f.write('router_bgp_remote: "'+router_bgp_remote+'"\n')
        f.write('router_bgp_network_id: "'+router_bgp_network_id+'"\n')
        f.write('router_bgp_router_id: "'+router_bgp_router_id+'"\n')
        f.write('username: "'+username+'"\n')
        f.write('password: "'+password+'"\n')
        f.write('hostname: "'+hostname+'"\n')
        f.write('phase_1_localgw: "'+phase_1_localgw+'"\n')
        f.write('router_bgp_network_prefix: "'+router_bgp_network_prefix+'"\n')
        f.write('policy_dst_intf: "'+system_zone_name+'"\n')
        f.write(hardcode)
        f.close()
if __name__ == '__main__':
    main()
