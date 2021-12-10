#!/usr/bin/env python3                                                        
import socket
import re

def get_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(('10.255.255.255', 1))
        IP = sock.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        sock.close()
    return IP

def get_subnet(cidr):
    if cidr == '16':
        patt='(?P<subnet>[\d]{1,3}\.[\d]{1,3}\.)'
        ip=get_ip()
        m=re.search(patt, ip)
        subnet=m['subnet']+'0.0/'+str(cidr)
    elif cidr == '24':
        patt='(?P<subnet>[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.)'
        ip=get_ip()
        m=re.search(patt, ip)
        subnet=m['subnet']+'0/'+str(cidr)
    return subnet

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cidr', choices=['16', '24'], required=False)
    args = parser.parse_args()
    
    if args.cidr:
        print(get_subnet(args.cidr))
    else:
        print(get_ip())
