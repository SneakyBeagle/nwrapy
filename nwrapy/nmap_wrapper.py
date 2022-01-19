from nwrapy.colours import clr

import shlex
import subprocess
import sys
import os
import time
from datetime import datetime
from threading import Thread


class Nmap_Wrapper:
    """ """

    def __init__(self, *args, **kwargs):
        self.uid = os.environ.get("SUDO_UID")
        self.guid = os.environ.get("SUDO_GID")
        self.disco_options = ""
        self.portscan_options = ""
        self.probe_options = ""
        self.os_options = ""
        self.xml_files = []
        self.executed = {}

        if "disco_options" in kwargs:
            self.disco_options = kwargs["disco_options"]
            if type(self.disco_options) == list:
                self.disco_options = " ".join(self.disco_options)
        if "portscan_options" in kwargs:
            self.portscan_options = kwargs["portscan_options"]
            if type(self.portscan_options) == list:
                self.portscan_options = " ".join(self.portscan_options)
        if "full_portscan_options" in kwargs:
            self.full_portscan_options = kwargs["full_portscan_options"]
            if type(self.full_portscan_options) == list:
                self.full_portscan_options = " ".join(self.full_portscan_options)
        if "probe_options" in kwargs:
            self.probe_options = kwargs["probe_options"]
            if type(self.probe_options) == list:
                self.probe_options = " ".join(self.probe_options)
        if "os_options" in kwargs:
            self.os_options = kwargs["os_options"]
            if type(self.os_options) == list:
                self.os_options = " ".join(self.os_options)
        if "ssl_cipher_options" in kwargs:
            self.ssl_cipher_options = kwargs["ssl_cipher_options"]
            if type(self.ssl_cipher_options) == list:
                self.ssl_cipher_options = " ".join(self.ssl_cipher_options)
        if "ssl_cert_options" in kwargs:
            self.ssl_cert_options = kwargs["ssl_cert_options"]
            if type(self.ssl_cert_options) == list:
                self.ssl_cert_options = " ".join(self.ssl_cert_options)
        if "output_dir" in kwargs:
            self.basedir = kwargs["output_dir"]
            if not os.path.isdir(self.basedir):
                os.mkdir(self.basedir)
            self.xml_dir = os.path.join(self.basedir, "xml_files")
        else:
            self.basedir = os.path.join(os.getcwd(), "nwrapy_output")
            if not os.path.isdir(self.basedir):
                os.mkdir(self.basedir)
            self.xml_dir = os.path.join(self.basedir, "xml_files")

        if not os.path.isdir(self.xml_dir):
            os.mkdir(self.xml_dir)
            
        if not (self.uid == None):
            os.chown(self.basedir, int(self.uid), int(self.guid))
            os.chown(self.xml_dir, int(self.uid), int(self.guid))

        stdout, stderr = self.execute(cmd=["which", "nmap"])
        stdout = stdout.split("\n")[0]
        if stderr:
            print(
                clr.RED + "[!] nmap was not found:", stderr, clr.RESET, file=sys.stderr
            )
            sys.exit(1)
        else:
            # print('Nmap was found: ', stdout)
            self.nmap = stdout

    def host_discovery(self, target):
        """ """
        self.executed = {}
        self.xml_files = []
        self.send_icmp_echo(target=target)
        self.send_icmp_netmask(target=target)
        self.send_icmp_timestamp(target=target)
        self.send_tcp_syn(target=target)

    def port_scanning(self, target, full=False):
        """ """
        self.executed = {}
        self.xml_files = []
        if full:
            self.tcp_syn_full_port_scan(target=target)
        else:
            self.tcp_syn_port_scan(target=target)

    def service_scanning(self, target_ip, ports):
        self.service_scan(target=target_ip, ports=ports)

    def os_scanning(self, target):
        self.executed = {}
        self.xml_files = []
        self.os_scan(target=target)

    def SSL_cipher_scanning(self, target_ip, ports):
        print("Not implemented yet")

    def SSL_cert_scanning(self, target_ip, ports):
        print("Not implemented yet")

    def empty_files(self):
        self.executed = {}
        self.xml_files = []

    def send_icmp_echo(self, target):
        self.execute_nmap(
            target=target,
            cmd="{nmap} -n -sn -PE -vv {options} {target} -oX {xml_file}",
            xml_file="icmp_echo_host_disco.xml",
            options=self.disco_options,
        )

    def send_icmp_netmask(self, target):
        self.execute_nmap(
            target=target,
            cmd="{nmap} -n -sn -PM -vv {options} {target} -oX {xml_file}",
            xml_file="icmp_netmask_host_disco.xml",
            options=self.disco_options,
        )

    def send_icmp_timestamp(self, target):
        self.execute_nmap(
            target=target,
            cmd="{nmap} -n -sn -PP -vv {options} {target} -oX {xml_file}",
            xml_file="icmp_timestamp_host_disco.xml",
            options=self.disco_options,
        )

    def send_tcp_syn(self, target):
        self.execute_nmap(
            target=target,
            cmd="{nmap} -PS21,22,23,25,80,113,445 -PA80,113,443 -n -sn -T4 -vv {options} {target} -oX {xml_file}",
            xml_file="tcp_syn_host_disco.xml",
            options=self.disco_options,
        )

    def tcp_syn_port_scan(self, target):
        self.execute_nmap(
            target=target,
            cmd="{nmap} --top-ports 1000 -n -Pn -sS -T4 --min-parallelism 100 -min-rate 64 -vv {options} {target} -oX {xml_file}",
            xml_file="top_1000_portscan.xml",
            options=self.portscan_options,
        )

    def tcp_syn_full_port_scan(self, target):
        self.execute_nmap(
            target=target,
            cmd="{nmap} -p- -n -Pn -sS -T4 --min-parallelism 100 -min-rate 128 -vv {options} {target} -oX {xml_file}",
            xml_file="full_portscan.xml",
            options=self.full_portscan_options,
        )

    def service_scan(self, target, ports):
        if type(ports) == list:
            ports = ",".join(ports)
        self.execute_nmap(
            target=target,
            cmd="{nmap} -n -Pn -sV --script banner -T4 -vv {options} {target} -oX {xml_file}",
            xml_file="{target}_service_scan.xml",
            options=self.probe_options + f" -p {ports}",
        )

    def os_scan(self, target):
        self.execute_nmap(
            target=target,
            cmd="{nmap} -n -Pn -O -T4 --min-parallelism 100 --min-rate 64 -vv {options} {target} -oX {xml_file}",
            xml_file="os_scan.xml",
            options=self.os_options,
        )

    def execute_nmap(self, target, cmd, xml_file, options):
        xml_file = os.path.join(
            self.xml_dir, xml_file.format(target=target).replace("/", "_")
        )
        self.xml_files.append(xml_file)
        nmap = self.nmap
        cmd = cmd.format(nmap=nmap, options=options, target=target, xml_file=xml_file)
        cmd = shlex.split(cmd)
        self.stdout, self.stderr = None, None
        t = Thread(target=self.execute, args=(cmd,))
        t.start()
        while t.is_alive():
            print("Waiting to finish", end="\r")
            time.sleep(0.001)
        t.join()
        if not (self.uid == None):
            os.chown(xml_file, int(self.uid), int(self.guid))
        # return self.execute(cmd=cmd)
        return self.stdout, self.stderr

    def execute(self, cmd: list):
        print("Executing:\n\t" + clr.FAINT_WHITE, " ".join(cmd) + clr.RESET)
        start = time.time()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        end = time.time()
        t = "%.4f" % (end - start)
        print("Time:", t + "s      ")
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        if stderr:
            print(clr.RED + str(stderr) + clr.RESET)
        self.executed[str(datetime.now())] = {
            "cmd": " ".join(cmd),
            "status_code": str(process.returncode),
            "time": t,
        }
        self.stdout, self.stderr = stdout, stderr
        return stdout, stderr

    def get_subnets(ips):
        subnets = []
        for ip in ips:
            segs = ip.split(".")
            subnets.append(".".join(segs[0:3]))
            subnets = list(dict.fromkeys(subnets))
        return subnets
