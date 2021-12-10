from src.utils import *
from src.nmap_db import db

def read_target(target, database):
    db.read_init(database)
    res=db.get_all_from_host(ip=target)
    print_dict(res)
