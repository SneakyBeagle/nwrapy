import xml.etree.ElementTree as ET
import os
import sys

class XML_Parser():

    def __init__(self):
        pass

    def parse_progress_xml(self, xml_file):
        """
        Find all taskprogress percentages and return the last one
        """
        perc=None
        perc = self.find_taskprogress(xml_file=xml_file)[-1]

        return perc

    def parse_disco_xml(self, xml_file):
        live_hosts = []
        xml_tree = ET.parse(xml_file)
        xml_root = xml_tree.getroot()
        for host in self.find_hosts(xml_file=xml_file):
            state = host.find('status').get('state')
            if state == "up":
                live_hosts.append(host.find('address').get('addr'))
        return live_hosts

    def parse_disco_ports_xml(self, xml_file):
        hosts={}
        for host in self.find_hosts(xml_file=xml_file):
            ip = host.find('address').get('addr')
            hosts[ip]={'ports':[], 'reason':[], 'service':[]}
            ports=self.find_ports(host=host)
            for port in ports:
                state=port.find('state').get('state')
                if state == 'open':
                    hosts[ip]['ports'].append(port.get('portid'))
                    try:
                        hosts[ip]['reason'].append(port.find('state').get('reason'))
                    except AttributeError:
                        hosts[ip]['reason'].append('none')
                    try:
                        hosts[ip]['service'].append(port.find('service').get('name'))
                    except AttributeError:
                        hosts[ip]['service'].append('none')
        
        return self.__replace_None(hosts=hosts)

    def parse_service_ports_xml(self, xml_file):
        hosts={}
        for host in self.find_hosts(xml_file=xml_file):
            ip = host.find('address').get('addr')
            hosts[ip]={'ports':[], 'name':[], 'product':[],
                       'version':[], 'extrainfo':[], 'ostype':[],
                       'method':[], 'script_id':[], 'script_output':[]}
            ports=self.find_ports(host=host)
            for port in ports:
                if self.is_open(port=port):
                    hosts[ip]['ports'].append(port.get('portid'))
                    service=port.find('service')
                    script=port.find('script')
                    hosts[ip]['name'].append(service.get('name'))
                    hosts[ip]['product'].append(service.get('product'))
                    hosts[ip]['version'].append(service.get('version'))
                    hosts[ip]['extrainfo'].append(service.get('extrainfo'))
                    hosts[ip]['ostype'].append(service.get('ostype'))
                    hosts[ip]['method'].append(service.get('method'))

                    try:
                        hosts[ip]['script_id'].append(script.get('id'))
                        hosts[ip]['script_output'].append(script.get('output'))
                    except AttributeError:
                        hosts[ip]['script_id'].append('none')
                        hosts[ip]['script_output'].append('none')

        return self.__replace_None(hosts=hosts)

    def parse_os_xml(self, xml_file):
        hosts={}
        for host in self.find_hosts(xml_file=xml_file):
            ip = host.find('address').get('addr')
            hosts[ip]={'name':[], 'accuracy':[]}
            oss=self.find_os(host=host)
            for os in oss:
                hosts[ip]['name'].append(os.get('name'))
                hosts[ip]['accuracy'].append(os.get('accuracy'))

        return self.__replace_None(hosts=hosts)

    def find_taskprogress(self, xml_file):
        xml_tree = ET.parse(xml_file)
        xml_root = xml_tree.getroot()
        return xml_root.findall('taskprogress')

    def find_hosts(self, xml_file):
        xml_tree = ET.parse(xml_file)
        xml_root = xml_tree.getroot()
        return xml_root.findall('host')

    def find_ports(self, host):
        t=host.findall('ports')
        if t:
            return host.findall('ports')[0].findall('port')
        return []

    def find_os(self, host):
        t=host.findall('os')
        if t:
            return host.findall('os')[0].findall('osmatch')
        return []

    def is_open(self, port):
        state=port.find('state').get('state')
        return state=='open'

    def __replace_None(self, hosts):
        for host,it in hosts.items():
            for key, el in it.items():
                for i in range(len(el)):
                    if hosts[host][key][i]==None:
                        hosts[host][key][i]='none'
        return hosts
        
xml_parser = XML_Parser()
