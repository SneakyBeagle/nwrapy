from nwrapy.nmap_db import db
from nwrapy.colours import clr
from nwrapy.utils import *
import sys


def init(args):
    print("Connecting to", args.database)
    try:
        db.read_init(args.database)
        print("Connected to", args.database)
    except Exception as e:
        print("Failed to connect to db:", e, file=sys.stderr)
    

def getter(args):
    if db.initialised:
        target=args.target
        res=db.get_all_from_host(ip=target)
        print_dict(res)

def lister(args):
    if db.initialised:
        if args.objects=='targets':
            targets=db.get_all_hosts()
            for target in targets:
                print(target)
        elif args.objects=='commands':
            pass
        elif args.objects=='subnets':
            subnets=db.get_all_subnets()
            for subnet in subnets:
                print(subnet)
        
    
def exit(args):
    sys.exit(0)
