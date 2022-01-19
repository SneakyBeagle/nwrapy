import csv
import os


class csv_conv:
    def __init__(self, *args, **kwargs):
        self.uid = os.environ.get("SUDO_UID")
        self.guid = os.environ.get("SUDO_GID")
        if "output_dir" in kwargs:
            self.basedir = kwargs["output_dir"]
        else:
            self.basedir = os.path.join(os.getcwd(), "nwrapy_output")

        if not os.path.isdir(self.basedir):
            os.mkdir(self.basedir)
        self.csv_dir = os.path.join(self.basedir, "csv_files")
        if not os.path.isdir(self.csv_dir):
            os.mkdir(self.csv_dir)

        if not (self.uid == None):
            os.chown(self.basedir, int(self.uid), int(self.guid))
            os.chown(self.csv_dir, int(self.uid), int(self.guid))

        self.sum_cols = [
            "IP",
            "status",
            "open_ports",
            "OS",
            "ports",
            "icmp_echo",
            "icmp_netmask",
            "icmp_timestamp",
        ]
        self.cols = [
            "IP",
            "OS",
            "port",
            "service",
            "product",
            "version",
            "extra",
            "icmp_echo",
            "icmp_netmask",
            "icmp_timestamp",
        ]

    def list_to_csv(self, l):
        return " ".join(l)

    def get_key_val_dict(self, d, key):
        """
        Get the value of a specified key from a dict. Works recursively
        """
        value = None
        for k, val in d.items():
            if k == key:
                return val
            if type(val) == dict:
                value = self.get_key_val_dict(val, key)
        return self.__clean(value)

    def get_key_type_dict(self, d, type_):
        """
        Get the first key of a specified type from a dict. Works recursively
        """
        key = None
        for k, val in d.items():
            if type(k) == type_:
                return k
            if type(val) == dict:
                key = self.get_key_val_dict(val, key)
        return key

    def os_row(self, os_list):
        os_l = []
        for os_ in os_list:
            name = self.get_key_val_dict(d=os_, key="name")
            if name:
                os_l.append(name)
        os_ = " / ".join(os_l)
        return os_

    def write_summary(self, hosts_dict):
        csv_file = os.path.join(self.csv_dir, "summary.csv")
        with open(csv_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(self.sum_cols)
            for ip, d in hosts_dict.items():
                row = []
                row.append(ip)
                row.append(self.get_key_val_dict(d=d, key="status"))
                row.append(self.get_key_val_dict(d=d, key="open_ports"))

                osname = self.get_key_val_dict(d=d, key="os")
                row.append(self.os_row(os_list=osname))

                ports = self.get_key_val_dict(d=d, key="ports")
                port_l = []
                for p in ports:
                    for k, v in p.items():
                        port_l.append(str(k))
                ports = " / ".join(port_l)
                row.append(ports)
                row.append(self.get_key_val_dict(d=d, key="icmp_echo"))
                row.append(self.get_key_val_dict(d=d, key="icmp_netmask"))
                row.append(self.get_key_val_dict(d=d, key="icmp_timestamp"))
                writer.writerow(row)

        if not (self.uid == None):
            os.chown(csv_file, int(self.uid), int(self.guid))

    def write_full(self, hosts_dict):
        csv_file = os.path.join(self.csv_dir, "report.csv")
        with open(csv_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow(self.cols)
            for ip, d in hosts_dict.items():
                port_l = self.get_key_val_dict(d=d, key="ports")
                osname = self.get_key_val_dict(d=d, key="os")
                os_ = self.os_row(os_list=osname)
                for p in port_l:
                    port_n = 0
                    for k, v in p.items():
                        port_n = k
                    service = self.get_key_val_dict(d=p, key="name")
                    product = self.get_key_val_dict(d=p, key="product")
                    version = self.get_key_val_dict(d=p, key="version")
                    extra = self.get_key_val_dict(d=p, key="extrainfo")
                    row = [ip, os_, port_n, service, product, version, extra]
                    row.append(self.get_key_val_dict(d=d, key="icmp_echo"))
                    row.append(self.get_key_val_dict(d=d, key="icmp_netmask"))
                    row.append(self.get_key_val_dict(d=d, key="icmp_timestamp"))
                    writer.writerow(row)
                writer.writerow([])

        if not (self.uid == None):
            os.chown(csv_file, int(self.uid), int(self.guid))

    def __clean(self, string):
        if type(string) == str:
            repl = {",": "/"}

            for k, v in repl.items():
                string = string.replace(k, v)

        return string
