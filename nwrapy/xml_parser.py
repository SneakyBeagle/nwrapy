import xml.etree.ElementTree as ET
import os
import sys
import glob


class Parse_exception(Exception):
    """ """


class XML_Parser:
    def __init__(self):
        pass

    def parse_progress_xml(self, xml_file):
        """
        Find all taskprogress percentages and return the last one
        """
        perc = None
        perc = self.find_taskprogress(xml_file=xml_file)[-1]

        return perc

    def merge(self, files, output_file):
        """ """
        for f in files:
            assert f.endswith(".xml"), str(f) + " does not end with .xml"

        root = ET.Element("nmaprun")

        for xml_file in files:
            xml_tree = ET.parse(xml_file)
            xml_root = xml_tree.getroot()

            if not (root):
                root = xml_root
            else:
                root.attrib["args"] += " && " + xml_root.attrib["args"]
                root.attrib["start"] += " && " + xml_root.attrib["start"]
                root.attrib["startstr"] += " && " + xml_root.attrib["startstr"]
            hosts = xml_root.findall("host")
            ahosts = root.findall("host")
            for i in range(len(hosts)):
                new_host = hosts[i]
                append_host = True
                ip = new_host.find("address").get("addr")
                for j in range(len(ahosts)):
                    aip = ahosts[j].find("address").get("addr")
                    if ip == aip:
                        append_host = False
                if append_host:
                    root.append(new_host)

        new_tree = ET.ElementTree(root)
        with open(output_file, "wb") as fd:
            new_tree.write(fd)

    def get_command(self, xml_file):
        try:
            xml_tree = ET.parse(xml_file)
            xml_root = xml_tree.getroot()
            cmd = xml_root.get("args")
            return cmd
        except ET.ParseError:
            raise Parse_exception("Could not parse " + str(xml_file))

    def get_hosts(self, xml_file):
        hosts = {}
        for host in self.find_hosts(xml_file=xml_file):
            state = host.find("status").get("state")
            if state == "up":
                ip = host.find("address").get("addr")
                try:
                    hostname = host.find("hostnames").find("hostname").get("name")
                except AttributeError:
                    hostname = "None"
                portnrs = []
                services = []
                products = []
                versions = []
                extrainfo = []
                ostypes = []
                scripts = []
                methods = []
                ports = self.find_ports(host=host)
                for port in ports:
                    state = port.find("state").get("state")
                    if state == "open":
                        portnrs.append(port.get("portid"))
                        service = port.find("service")
                        services.append(str(service.get("name")))
                        products.append(str(service.get("product")))
                        versions.append(str(service.get("version")))
                        extrainfo.append(str(service.get("extrainfo")))
                        ostypes.append(str(service.get("ostype")))
                        try:
                            scripts.append(str(port.find("script").get("output")))
                        except AttributeError:
                            scripts.append("None")
                        # methods.append(str(service.get('method')))
                hosts[ip] = {}
                if len(hostname):
                    hosts[ip]["hostname"] = hostname
                if len(portnrs):
                    hosts[ip]["ports"] = portnrs
                    hosts[ip]["services"] = services
                    hosts[ip]["products"] = products
                    hosts[ip]["versions"] = versions
                    hosts[ip]["extrainfo"] = extrainfo
                if len(ostypes):
                    hosts[ip]["ostypes"] = ostypes
                if len(scripts):
                    hosts[ip]["scripts"] = scripts
                # hosts[ip]['methods']=methods

        return hosts

    def parse_disco_xml(self, xml_file):
        live_hosts = []
        xml_tree = ET.parse(xml_file)
        xml_root = xml_tree.getroot()
        for host in self.find_hosts(xml_file=xml_file):
            state = host.find("status").get("state")
            if state == "up":
                live_hosts.append(host.find("address").get("addr"))
        return live_hosts

    def parse_disco_ports_xml(self, xml_file):
        hosts = {}
        for host in self.find_hosts(xml_file=xml_file):
            ip = host.find("address").get("addr")
            hosts[ip] = {"ports": [], "reason": [], "service": []}
            ports = self.find_ports(host=host)
            for port in ports:
                state = port.find("state").get("state")
                if state == "open":
                    hosts[ip]["ports"].append(port.get("portid"))
                    try:
                        hosts[ip]["reason"].append(port.find("state").get("reason"))
                    except AttributeError:
                        hosts[ip]["reason"].append("none")
                    try:
                        hosts[ip]["service"].append(port.find("service").get("name"))
                    except AttributeError:
                        hosts[ip]["service"].append("none")

        return self.__replace_None(hosts=hosts)

    def parse_service_ports_xml(self, xml_file):
        hosts = {}
        for host in self.find_hosts(xml_file=xml_file):
            ip = host.find("address").get("addr")
            hosts[ip] = {
                "ports": [],
                "name": [],
                "product": [],
                "version": [],
                "extrainfo": [],
                "ostype": [],
                "method": [],
                "script_id": [],
                "script_output": [],
            }
            ports = self.find_ports(host=host)
            for port in ports:
                if self.is_open(port=port):
                    hosts[ip]["ports"].append(port.get("portid"))
                    service = port.find("service")
                    script = port.find("script")
                    hosts[ip]["name"].append(service.get("name"))
                    hosts[ip]["product"].append(service.get("product"))
                    hosts[ip]["version"].append(service.get("version"))
                    hosts[ip]["extrainfo"].append(service.get("extrainfo"))
                    hosts[ip]["ostype"].append(service.get("ostype"))
                    hosts[ip]["method"].append(service.get("method"))

                    try:
                        hosts[ip]["script_id"].append(script.get("id"))
                        hosts[ip]["script_output"].append(script.get("output"))
                    except AttributeError:
                        hosts[ip]["script_id"].append("none")
                        hosts[ip]["script_output"].append("none")

        return self.__replace_None(hosts=hosts)

    def parse_os_xml(self, xml_file):
        hosts = {}
        for host in self.find_hosts(xml_file=xml_file):
            ip = host.find("address").get("addr")
            hosts[ip] = {"name": [], "accuracy": []}
            oss = self.find_os(host=host)
            for os in oss:
                hosts[ip]["name"].append(os.get("name"))
                hosts[ip]["accuracy"].append(os.get("accuracy"))

        return self.__replace_None(hosts=hosts)

    def find_taskprogress(self, xml_file):
        xml_tree = ET.parse(xml_file)
        xml_root = xml_tree.getroot()
        return xml_root.findall("taskprogress")

    def find_hosts(self, xml_file):
        try:
            xml_tree = ET.parse(xml_file)
            xml_root = xml_tree.getroot()
            return xml_root.findall("host")
        except ET.ParseError:
            raise Parse_exception("Could not parse " + str(xml_file))

    def find_ports(self, host):
        t = host.findall("ports")
        if t:
            return host.findall("ports")[0].findall("port")
        return []

    def find_os(self, host):
        t = host.findall("os")
        if t:
            return host.findall("os")[0].findall("osmatch")
        return []

    def is_open(self, port):
        state = port.find("state").get("state")
        return state == "open"

    def __replace_None(self, hosts):
        for host, it in hosts.items():
            for key, el in it.items():
                for i in range(len(el)):
                    if hosts[host][key][i] == None:
                        hosts[host][key][i] = "none"
        return hosts


xml_parser = XML_Parser()
