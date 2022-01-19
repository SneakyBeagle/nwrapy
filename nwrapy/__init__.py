#!/usr/bin/env python3
from nwrapy.nmap_db import db
from nwrapy.nmap_wrapper import Nmap_Wrapper
from nwrapy.xml_parser import xml_parser, Parse_exception
from nwrapy.csv_conv import csv_conv
from nwrapy.colours import clr
from nwrapy.interactive import *
from nwrapy.read import *
from nwrapy.get_ip import *
from nwrapy.table import Table

import re
import sys
import os
import argparse
import subprocess
import time
import shlex
from threading import Thread, active_count

####################################################################
####################################################################
# CONFIGURATION
## Not required to do anything about, but you are able to change the
## default behaviour here.
### Exclude ports with specific probes. The default beheviour tries to prevent ISPs from flagging the TerminalServer probes
EXCLUDE_PORTS = [
    "T:9100-9107",
    "T:515",
    "T:1028",
    "T:1068",
    "T:1503",
    "T:1720",
    "T:1935",
    "T:2040",
    "T:3388",
]

DISCO_OPTIONS = [
    "-g 53",  # Source port 53 (20 is FTP-DATA, also an option)
    "--randomize-hosts",
    "--data-length 56",  # 56 simulates Linux ping while 32 simulates Windows
]

PORTSCAN_OPTIONS = [
    "-g 53",  # Source port 53 (20 is FTP-DATA, also an option)
    "--randomize-hosts",
    "--data-length 56",  # 56 simulates Linux ping while 32 simulates Windows
]

FULL_PORTSCAN_OPTIONS = [
    "-g 53",  # Source port 53 (20 is FTP-DATA, also an option)
    "--randomize-hosts",
    "--data-length 56",  # 56 simulates Linux ping while 32 simulates Windows
]

PROBE_OPTIONS = [
    "-g 53",  # Source port 53 (20 is FTP-DATA, also an option)
    "--version-intensity {INTENSITY}",
    "--exclude-ports " + ",".join(EXCLUDE_PORTS),
]

OS_OPTIONS = ["-g 53"]  # Source port 53 (20 is FTP-DATA, also an option)

SSL_CIPHER_OPTIONS = ["-g 53"]  # Source port 53 (20 is FTP-DATA, also an option)

SSL_CERT_OPTIONS = ["-g 53"]  # Source port 53 (20 is FTP-DATA, also an option)

### Colours
INIT = "[" + clr.BOLD_WHITE + "***" + clr.RESET + "]"
START = "[" + clr.BOLD_WHITE + "*" + clr.RESET + "]"
DONE = "[" + clr.GREY + "#" + clr.RESET + "]"
FIN = "[" + clr.BOLD_WHITE + "***" + clr.RESET + "]"
PRMPT = clr.BOLD_WHITE + "[$]: " + clr.RESET
####################################################################
####################################################################


class ArgParser(argparse.ArgumentParser):
    """
    Argument Parser that does not exit on error. To be used in interactive mode
    """

    def error(self, message):
        clr.RED
        self.print_help(sys.stderr)


def is_root():
    if os.geteuid() == 0:
        return True
    else:
        return False


def rm_duplicates(l: list):
    """
    Removes duplicates from a list
    """
    l = list(dict.fromkeys(l))
    return l


def convert_to_nmap_target(hosts: list):
    """
    Converts a list to a string, separated by spaces. To be used by nmap.

    Parameters
    ----------
    hosts: list
        The list to filter

    Returns
    -------
    .list:
        The list without duplicates
    """
    hosts = rm_duplicates(hosts)
    return " ".join(hosts)


def autoscan(args):
    """
    Scans the default network range, where the netmask can be CIDR /16 or /24

    Parameters
    ----------
    args:
        The arguments, as parsed by argparse
    """
    args.target = get_subnet(args.cidr)
    print(START, "AUTOSCANNING", args.target)
    scan(args)


def scan(args):
    if not (is_root()):
        print(clr.RED + "[!] Please run this as root" + clr.RESET, file=sys.stderr)
        sys.exit(1)

    print(START, "Initialising")
    if not args.database.endswith(".db"):
        args.database += ".db"

    db.db_init(db_name=args.database)

    if args.version_intensity:
        INTENSITY = args.version_intensity
    else:
        INTENSITY = 6
    for i in range(len(PROBE_OPTIONS)):
        if "INTENSITY" in PROBE_OPTIONS[i]:
            PROBE_OPTIONS[i] = PROBE_OPTIONS[i].format(INTENSITY=INTENSITY)

    if args.output:
        nwrap = Nmap_Wrapper(
            output_dir=args.output,
            disco_options=DISCO_OPTIONS,
            portscan_options=PORTSCAN_OPTIONS,
            full_portscan_options=FULL_PORTSCAN_OPTIONS,
            probe_options=PROBE_OPTIONS,
            os_options=OS_OPTIONS,
            ssl_cipher_options=SSL_CIPHER_OPTIONS,
            ssl_cert_options=SSL_CERT_OPTIONS,
        )
    else:
        nwrap = Nmap_Wrapper(
            disco_options=DISCO_OPTIONS,
            portscan_options=PORTSCAN_OPTIONS,
            full_portscan_options=FULL_PORTSCAN_OPTIONS,
            probe_options=PROBE_OPTIONS,
            os_options=OS_OPTIONS,
            ssl_cipher_options=SSL_CIPHER_OPTIONS,
            ssl_cert_options=SSL_CERT_OPTIONS,
        )

    max_threads = 1
    if args.threads:
        max_threads = args.threads

    print(DONE, "Initialisation done")

    #######################################################
    print(START, "STAGE 1: Host discovery for", args.target)
    args.target = convert_to_nmap_target(args.target.split(" "))
    nwrap.host_discovery(target=args.target)
    for dt, item in nwrap.executed.items():
        db.insert_command(
            cmd=item["cmd"],
            status_code=item["status_code"],
            time=item["time"],
            datetime=dt,
        )

    hosts = []
    for f in nwrap.xml_files:
        hosts += xml_parser.parse_disco_xml(xml_file=f)
    hosts = rm_duplicates(hosts)
    db.assert_subnets(hosts=hosts)
    for host in hosts:
        icmp_echo, icmp_netmask, icmp_timestamp = (
            "no-response",
            "no-response",
            "no-response",
        )
        for f in nwrap.xml_files:
            if host in xml_parser.parse_disco_xml(xml_file=f):
                if "icmp_echo" in f:
                    icmp_echo = "echo-reply"
                elif "icmp_netmask" in f:
                    icmp_netmask = "netmask-reply"
                elif "icmp_timestamp" in f:
                    icmp_timestamp = "timestamp-reply"

        db.insert_host(
            ip=host,
            icmp_echo=icmp_echo,
            icmp_netmask=icmp_netmask,
            icmp_timestamp=icmp_timestamp,
        )
    print(DONE, "STAGE 1 finished: found", len(rm_duplicates(hosts)), "hosts up")

    #######################################################
    targets = convert_to_nmap_target(hosts=hosts)
    print(
        START,
        "STAGE 2: Port Scanning for:\n\t"
        + clr.BOLD_WHITE
        + "\n\t".join(hosts)
        + clr.RESET,
    )
    nwrap.port_scanning(target=targets, full=False)

    for dt, item in nwrap.executed.items():
        db.insert_command(
            cmd=item["cmd"],
            status_code=item["status_code"],
            time=item["time"],
            datetime=dt,
        )
    results = {}
    for f in nwrap.xml_files:
        for key, el in xml_parser.parse_disco_ports_xml(xml_file=f).items():
            results[key] = el

    nr_ports = 0
    for ip, it in results.items():
        # update open ports
        db.update_host_open_ports(ip=ip, open_ports=len(it["ports"]))
        for i in range(len(it["ports"])):
            db.insert_port(ip=ip, port=it["ports"][i], reason=it["reason"][i])
            nr_ports += 1

    print(DONE, "STAGE 2 finished")

    #######################################################
    print(
        START,
        "STAGE 3: Service Scanning",
        nr_ports,
        "ports total, of",
        len(hosts),
        "hosts",
    )

    ctr = 1
    threads = []
    nwrap.empty_files()
    for ip, it in results.items():
        print(clr.BOLD_WHITE + "Host", str(ctr) + "/" + str(len(hosts)), clr.RESET)
        ctr += 1
        if it["ports"]:
            # threads.append(Thread(target=nwrap.service_scanning, args=(ip,it['ports'])))
            # threads[-1].start()
            # while active_count() >= max_threads:
            #    print('Waiting for a thread to finish', str(active_count())+'/'+str(max_threads),
            #          end='\r')
            #    time.sleep(0.1)
            nwrap.service_scanning(target_ip=ip, ports=it["ports"])
        else:
            print("No open ports discovered")

    for index, thread in enumerate(threads):
        print("Joining thread", i, end="\r")
        thread.join()
    print("")
    print(active_count())

    for f in nwrap.xml_files:
        for ip, it in xml_parser.parse_service_ports_xml(xml_file=f).items():
            for i in range(len(it["ports"])):
                db.insert_service(
                    ip=ip,
                    port=it["ports"][i],
                    name=it["name"][i],
                    product=it["product"][i],
                    version=it["version"][i],
                    extrainfo=it["extrainfo"][i],
                    ostype=it["ostype"][i],
                    method=it["method"][i],
                    script_id=it["script_id"][i],
                    script_output=it["script_output"][i],
                )

    print(DONE, "STAGE 3 finished")

    # -----------------------------------------------------#
    print(START, "Writing intermediary results")
    if args.output:
        csv = csv_conv(output_dir=args.output)
    else:
        csv = csv_conv()

    ihosts = db.get_all_hosts()
    iresults = {}
    for host in ihosts:
        iresults[host] = db.get_all_from_host(ip=host)
    csv.write_summary(hosts_dict=iresults)
    csv.write_full(hosts_dict=iresults)
    print(DONE, "Wrote intermediary results")
    # -----------------------------------------------------#

    #######################################################
    print(START, "STAGE 4: OS Scanning", len(hosts), "hosts")
    targets = convert_to_nmap_target(hosts=hosts)
    nwrap.os_scanning(target=targets)

    for f in nwrap.xml_files:
        for ip, it in xml_parser.parse_os_xml(xml_file=f).items():
            for i in range(len(it["name"])):
                db.insert_os(ip=ip, name=it["name"][i], accuracy=it["accuracy"][i])

    print(DONE, "STAGE 4 finished")

    #######################################################
    print(START, "STAGE 5: SSL Ciphers scanning on", len(hosts), "hosts")
    ctr = 1
    nwrap.empty_files()
    for ip, it in results.items():
        print(clr.BOLD_WHITE + "Host", str(ctr) + "/" + str(len(hosts)), clr.RESET)
        ctr += 1
        if it["ports"]:
            nwrap.SSL_cipher_scanning(target_ip=host, ports=it["ports"])
        else:
            print("No open ports detected")
    print(DONE, "STAGE 5 finished")

    #######################################################
    print(START, "STAGE 6: SSL Certs scanning on", len(hosts), "hosts")
    ctr = 1
    nwrap.empty_files()
    for ip, it in results.items():
        print(clr.BOLD_WHITE + "Host", str(ctr) + "/" + str(len(hosts)), clr.RESET)
        ctr += 1
        if it["ports"]:
            nwrap.SSL_cipher_scanning(target_ip=host, ports=it["ports"])
        else:
            print("No open ports detected")
    print(DONE, "STAGE 6 finished")

    if not (args.no_full_portscan):
        #######################################################
        print(START, "STAGE 7: Full port scan on", len(hosts), "hosts")
        nwrap.port_scanning(target=targets, full=True)

        for dt, item in nwrap.executed.items():
            db.insert_command(
                cmd=item["cmd"],
                status_code=item["status_code"],
                time=item["time"],
                datetime=dt,
            )
        nresults = {}
        for f in nwrap.xml_files:
            for key, el in xml_parser.parse_disco_ports_xml(xml_file=f).items():
                nresults[key] = el

        nr_ports = 0
        for ip, it in nresults.items():
            # update open ports
            db.update_host_open_ports(ip=ip, open_ports=len(it["ports"]))
            for i in range(len(it["ports"])):
                db.insert_port(ip=ip, port=it["ports"][i], reason=it["reason"][i])
                nr_ports += 1
        print(DONE, "STAGE 7 finished")

    print(START, "Writing CSV report")

    hosts = db.get_all_hosts()
    results = {}
    for host in hosts:
        results[host] = db.get_all_from_host(ip=host)
    csv.write_summary(hosts_dict=results)
    csv.write_full(hosts_dict=results)

    print(FIN, "Finished")


def read(args):
    if args.service:
        pass
    elif args.target:
        database = args.database
        read_target(target=args.target, database=database)

    print(FIN, "Finished")


def xml(args):
    xml_file = args.file
    print(clr.BOLD + "Reading from", xml_file + clr.RESET)
    if not (os.path.exists(xml_file)):
        print(clr.BOLD + clr.RED + '"' + xml_file + '"', "does not exist" + clr.RESET)
        sys.exit(1)

    """
    with open(xml_file, "r") as fd:
        lines = fd.readlines()
    for line in lines:
        print(line.split('\n')[0])
    """
    print()
    print(clr.BOLD + "Executed command:" + clr.RESET)
    try:
        cmd = xml_parser.get_command(xml_file)
    except Parse_exception as e:
        print(clr.RED + clr.BOLD + "Failed to parse", xml_file + clr.RESET)
        print("Reason:", e)
        sys.exit(1)

    print(clr.GREY + cmd + clr.RESET + "\n")

    hosts = xml_parser.get_hosts(xml_file)
    table = Table()
    for h, d in hosts.items():
        if (
            (not (args.target) or (h == args.target))
            and (
                not (args.service)
                or ("services" in d and args.service in d["services"])
            )
            and (not (args.port) or ("ports" in d and args.port in d["ports"]))
            and (
                not (args.os_type) or ("ostypes" in d and args.os_type in d["ostypes"])
            )
            and (
                not (args.product)
                or ("products" in d and args.product in d["products"])
            )
        ):
            print(clr.BOLD + "IP: " + h + clr.RESET)
            data = []
            headers = []
            for k, v in d.items():
                if type(v) == list:
                    headers.append(k)
                    data.append(v)
                else:
                    print(clr.DIM + k + ":", v + clr.RESET)

            if len(headers):
                for row in table.table(headers, data):
                    print(clr.DIM + row + clr.RESET)

    print(FIN, "Finished")


def merge(args):
    files = args.files
    if args.new_file in files:
        print(
            clr.RED + clr.BOLD + "File",
            args.new_file,
            "is part of the merge already" + clr.RESET,
        )
        sys.exit(1)
    try:
        xml_parser.merge(files, args.new_file)
        print("Wrote output to", args.new_file)
        print(FIN, "Finished")
    except Exception as e:
        print(clr.RED + clr.BOLD + "Failed to merge" + clr.RESET)
        print("Reason:", e)


def parse_args():
    parser = argparse.ArgumentParser()  # top level parser
    subparsers = parser.add_subparsers(help="The mode to run in")

    ## Scan parser
    scan_parser = subparsers.add_parser(
        "scan", help="Scan mode. Scan target(s) using the pre-defined Nmap scans"
    )
    scan_parser.add_argument(
        "target",
        help="Target(s) to scan. Can be in the format of a single IP or CIDR (192.168.0.0/24 for example)",
    )
    scan_parser.add_argument(
        "database",
        help="Database to store results into. Will create one if it does not exist",
    )
    scan_parser.add_argument(
        "-o",
        "--output",
        help="Output directory. Will write the nmap files into this dir, divided in subdirs.",
    )
    scan_parser.add_argument(
        "-i",
        "--version-intensity",
        help="Version intensity. Overwrites the default value of 6",
    )
    scan_parser.add_argument(
        "-t",
        "--threads",
        help="Maximum number of threads to run. Default is 1",
        type=int,
    )
    scan_parser.add_argument(
        "-nfp",
        "--no-full-portscan",
        help="Do no do a full portscan for all hosts. This could save a lot of time.",
        action="store_true",
    )
    scan_parser.set_defaults(func=scan)

    autoscan_parser = subparsers.add_parser(
        "autoscan",
        help="Autoscan mode. Autoscan local network using the pre-defined Nmap scans",
    )
    autoscan_parser.add_argument(
        "cidr",
        help="Subnet range to scan. Will result in scanning a network like 192.168.1.0/24 or 192.168.0.0/16 for example",
        choices=["16", "24"],
    )
    autoscan_parser.add_argument(
        "database",
        help="Database to store results into. Will create one if it does not exist",
    )
    autoscan_parser.add_argument(
        "-o",
        "--output",
        help="Output directory. Will write the nmap files into this dir, divided in subdirs.",
    )
    autoscan_parser.add_argument(
        "-i",
        "--version-intensity",
        help="Version intensity. Overwrites the default value of 6",
    )
    autoscan_parser.add_argument(
        "-t",
        "--threads",
        help="Maximum number of threads to run. Default is 1",
        type=int,
    )
    autoscan_parser.set_defaults(func=autoscan)

    ## Read parser
    read_parser = subparsers.add_parser(
        "read", help="Read mode. Read information on target(s), found during scan mode"
    )
    read_parser.add_argument(
        "-t",
        "--target",
        help="Target(s) to read information of. Quick way to get target information.",
    )
    read_parser.add_argument(
        "-s",
        "--service",
        help="List all targets with the specified service running, along with the port numbers",
    )
    read_parser.add_argument("database", help="Database to read from.")
    read_parser.set_defaults(func=read)

    # inter_parser = subparsers.add_parser('interactive', help='Interactive mode. Interactively request information from the database.')
    # inter_parser.set_defaults(func=interactive)
    xml_read_parser = subparsers.add_parser(
        "xml", help="Read information from a Nmap XML file"
    )
    xml_read_parser.add_argument("file", help="Nmap XML file to read")
    xml_read_parser.add_argument(
        "-t", "--target", help="Read results for specific target"
    )
    xml_read_parser.add_argument(
        "-s", "--service", help="Show only hosts with a specific service running"
    )
    xml_read_parser.add_argument(
        "-p", "--port", help="Show only hosts with a specific port opened"
    )
    xml_read_parser.add_argument(
        "-os", "--os-type", help="Show only hosts with a specific Operating System type"
    )
    xml_read_parser.add_argument(
        "-pr",
        "--product",
        help='Show only hosts with a specific product, such as "OpenSSH"',
    )
    xml_read_parser.set_defaults(func=xml)

    merge_parser = subparsers.add_parser(
        "merge", help="Merge multiple Nmap XML files into one"
    )
    merge_parser.add_argument(
        "files", help="Nmap XML files to merge", type=str, nargs="+"
    )
    merge_parser.add_argument(
        "-o",
        "--new-file",
        help="The file to write the results into",
        default="new.xml",
        const="newfile.xml",
        nargs="?",
        type=str,
    )
    merge_parser.set_defaults(func=merge)

    args = parser.parse_args()
    return args, parser


def main():
    version = "0.1.5"
    print(INIT, "Starting Nwrapy", version)

    args, parser = parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()


if __name__ == "__main__":
    main()
