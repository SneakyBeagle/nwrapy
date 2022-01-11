from nwrapy.utils import *
from nwrapy.nmap_db import db

def read_target(target, database):
    db.read_init(database)
    res=db.get_all_from_host(ip=target)
    print_dict(res)
