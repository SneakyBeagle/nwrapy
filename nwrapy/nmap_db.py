from nwrapy.db import DB

import os

class NMAP_DB(DB):
    """
    CreepyCrawler SQLite3 database implementation class
    """

    def db_init(self, db_name):
        """
        Initialise the database, by creating/connecting to it and creating the needed tables 
        if not already existing.
        """
        self._init(db_name=db_name)
        self.tables=self.get_tables()
        self.create_nmap_tables()
        self.initialised=True

    def read_init(self, db_name):
        """
        """
        if not(db_name.endswith('.db')):
               db_name=db_name+'.db'
        if os.path.exists(db_name):
            self._init(db_name=db_name)
            self.tables=self.get_tables()
            self.initialised=True
        else:
            raise ValueError(db_name+" does not exist")
               

    def insert_subnet(self, ip, hosts_up=0):
        subnet = '.'.join(ip.split('.')[0:3])+'.0/24'

        cursor=self.select(table_name='subnets',
                           column_names=['subnet_id'],
                           where="ip_cidr='"+subnet +"'")
        exists=False
        for row in cursor:
                exists=True

        if not exists:
            self.insert(table_name='subnets',
                        column_names=['ip_cidr', 'hosts_up'],
                        values=[self.str(subnet), str(hosts_up)])

    def insert_host(self, ip, status='up', open_ports=0, reason='none', vendor='unknown',
                    hostname='none', icmp_echo="no-response", icmp_netmask="no-response",
                    icmp_timestamp="no-response"):
        subnet_id = self.get_subnet_id(ip=ip)

        if self.host_exists(ip=ip):
            pass
        else:
            self.update_hosts_up(subnet_id=subnet_id)
        
            self.insert(table_name='hosts',
                        column_names=['ip', 'status', 'open_ports',
                                      'reason', 'vendor', 'hostname',
                                      'icmp_echo', 'icmp_netmask',
                                      'icmp_timestamp',
                                      'subnet_id'],
                        values=[self.str(ip), self.str(status), str(open_ports),
                                self.str(reason), self.str(vendor), self.str(hostname),
                                self.str(icmp_echo), self.str(icmp_netmask),
                                self.str(icmp_timestamp),
                                str(subnet_id)])

    def insert_command(self, cmd, status_code, time, datetime):
        self.insert(table_name='commands',
                    column_names=['command', 'status_code', 'time', 'datetime'],
                    values=[self.str(cmd), str(status_code), str(time), self.str(datetime)])

    def insert_port(self, ip, port, reason='none', service_id='-1'):
        host_id=self.get_host_id(ip=ip)

        if self.port_host_exists(ip=ip, port=port):
            pass
        else:
            self.insert(table_name='ports',
                        column_names=['port', 'reason',
                                      'service_id', 'host_id'],
                        values=[str(port), self.str(reason),
                                str(service_id), str(host_id)])

    def insert_service(self, ip, port, name, product='none', version='none',
                       extrainfo='none', ostype='none', method='none',
                       script_id='none', script_output='none'):
        port_id=self.get_port_id(ip=ip,port=port)

        exists=False
        try:
            # if exists
            service_id=self.get_service_id_port(port_id=port_id)
            if not(str(service_id)=='-1'):
                exists=True
        except ValueError:
            # if does not exist
            exists=False
        if exists:
            pass
        else:
            self.insert(table_name='services', 
                        column_names=['name', 'product', 'version',
                                      'extrainfo', 'ostype', 'method'],
                        values=[self.str(name), self.str(product), self.str(version),
                                self.str(extrainfo), self.str(ostype), self.str(method)])
            
            service_id=self.get_service_id(name=name, product=product, version=version)
        self.update_service_port(service_id=service_id, port_id=port_id)
        self.insert_script(port_id=port_id, id_=script_id, output=script_output)

    def insert_script(self, port_id, id_, output):
        if id_=='none':
            return
        try:
            self.get_script_id(port_id=port_id, id_=id_)
            return
        except ValueError:
            self.insert(table_name='scripts',
                        column_names=['id', 'output', 'port_id'],
                        values=[self.str(id_), self.str(output), str(port_id)])

    def insert_os(self, ip, name, accuracy):
        if name=='none':
            return

        host_id=self.get_host_id(ip=ip)
        self.insert(table_name='os',
                    column_names=['name', 'accuracy', 'host_id'],
                    values=[self.str(name), str(accuracy), str(host_id)])        


    def update_host_open_ports(self, ip, open_ports):
        host_id=self.get_host_id(ip=ip)
        self.update(table_name='hosts', column_name='open_ports',value=str(open_ports),
                    where="host_id="+str(host_id))
    
    def update_hosts_up(self, subnet_id):
        hosts_up=str(int(self.get_hosts_up(subnet_id=subnet_id))+1)
        self.update(table_name='subnets',column_name='hosts_up',value=hosts_up,
                    where="subnet_id="+str(subnet_id))

    def update_service_port(self, service_id, port_id):
        port_id=str(port_id)
        self.update(table_name='ports', column_name='service_id', value=str(service_id),
                    where="port_id="+port_id)
        
                        
    def host_exists(self, ip):
        cursor=self.select(table_name='hosts',
                           column_names=['host_id'],
                           where="ip='"+ip +"'")
        exists=False
        for row in cursor:
            if row[0]:
                exists=True
                break
        return exists

    def port_host_exists(self, ip, port):
        exists=False
        host_id=self.get_host_id(ip=ip)
        cursor=self.select(table_name='ports',
                           column_names=['port_id'],
                           where="host_id="+str(host_id)+" AND port="+str(port))
        for row in cursor:
            if row[0]:
                exists=True

        return exists

    def get_script_id(self, port_id, id_):
        cursor=self.select(table_name='scripts',
                           column_names=['script_id'],
                           where="port_id="+str(port_id)+" AND id="+self.str(id_))

        script_id=None
        for row in cursor:
            if row[0]:
                script_id=row[0]

        if not(script_id):
            raise ValueError("Could not find script_id for "+str(id_))
        return script_id
    
    def get_host_id(self, ip):
        cursor=self.select(table_name='hosts',
                           column_names=['host_id'],
                           where="ip='"+ip+"'")
        host_id=None
        for row in cursor:
            if row[0]:
                host_id=row[0]

        if not(host_id):
            raise ValueError("Could not find host_id for "+ip)
        return host_id

    def get_port_id(self, ip, port):
        host_id=self.get_host_id(ip=ip)
        cursor=self.select(table_name='ports',
                           column_names=['port_id'],
                           where="host_id='"+str(host_id)+"' AND port="+str(port))
        port_id=None
        for row in cursor:
            if row[0]:
                port_id=row[0]

        if not(port_id):
            raise ValueError("Could not find port_id for "+ip+":"+str(port))
        return port_id

    def get_service_id_port(self, port_id):
        cursor=self.select(table_name='ports',
                           column_names=['service_id'],
                           where="port_id='"+str(port_id)+"'")
        service_id=None
        for row in cursor:
            if row[0]:
                service_id=row[0]

        if not(service_id):
            raise ValueError("Could not find service_id for "+str(port_id)+"")

        return service_id

    def get_service_id(self, name, product, version):
        cursor=self.select(table_name='services',
                           column_names=['service_id'],
                           where="name="+self.str(name)+" AND product="+\
                           self.str(product)+" AND version="+self.str(version))
        service_id=None
        for row in cursor:
            if row[0]:
                service_id=row[0]

        if not(service_id):
            raise ValueError("Could not find service_id for "+name+", "+product+", "+version)

        return service_id

    def assert_subnets(self, hosts):
        for host in hosts:
            self.insert_subnet(ip=host)
        
    def get_hosts_up(self, subnet_id):
        cursor=self.select(table_name='subnets',
                           column_names=['hosts_up'],
                           where="subnet_id="+str(subnet_id))
        hosts_up=0
        for row in cursor:
            hosts_up=row[0]

        return hosts_up

    def get_all_hosts(self):
        hosts=[]
        cursor=self.select(table_name='hosts',
                           column_names=['ip'])
        for row in cursor:
            hosts.append(row[0])
        return hosts

    def get_all_subnets(self):
        subnets=[]
        cursor=self.select(table_name='subnets',
                           column_names=['ip_cidr'])
        for row in cursor:
            subnets.append(row[0])
        return subnets

    def get_hosts_from_subnet(self, subnet):
        subnet_id=self.get_subnet_id(ip=subnet)
        hosts=[]
        cursor=self.select(table_name='hosts',
                           column_names=['ip'],
                           where="subnet_id="+str(subnet_id))
        for row in cursor:
            hosts.append(row[0])
        return hosts

    def get_subnet_id(self, ip):
        subnet = '.'.join(ip.split('.')[0:3])+'.0/24'

        cursor=self.select(table_name='subnets',
                           column_names=['subnet_id'],
                           where="ip_cidr='"+subnet +"'")
        
        subnet_id=None
        for row in cursor:
            subnet_id=row[0]
            break
        
        return subnet_id

    def get_port_ids_host(self, host_id):
        port_ids=[]
        cursor=self.select(table_name='ports',
                           column_names=['port_id'],
                           where="host_id="+str(host_id))
        for row in cursor:
            port_ids.append(row[0])
        return port_ids

    def get_all_from_service(self, service_id):
        cursor=self.select(table_name='services',
                           column_names=['*'],
                           where="service_id="+str(service_id))
        return cursor

    def get_os(self, host_id):
        cursor=self.select(table_name='os',
                           column_names=['*'],
                           where="host_id="+str(host_id))
        return cursor
            
    def get_all_from_port(self, port_id):
        pass

    def get_all_from_host(self, ip):
        ignore=['host_id', 'subnet_id', 'port_id', 'service_id',
                'script_id', 'port', 'os_id']

        ## HOST INFO
        host_id=self.get_host_id(ip=ip)
        cursor=self.select(table_name='hosts',
                           column_names=['*'],
                           where='ip='+self.str(ip))
        
        host_cols=self.get_column_names(table_name='hosts')
        os_cols=self.get_column_names(table_name='os')

        host_info={}
        for row in cursor:
            i=0
            for col in row:
                if not(host_cols[i] in ignore):
                    host_info[host_cols[i]]=col
                i+=1

        host_info['os']=[]
        ctr=0
        limit=3
        for row in self.get_os(host_id=host_id):
            i=0
            for col in row:
                if not(os_cols[i] in ignore):
                    host_info['os'].append({os_cols[i]:col})
                if i>limit:
                    break
                i+=1
            ctr+=1
            if ctr>=limit:
                break

        ## PORT INFO
        port_info={}
        port_cols=self.get_column_names(table_name='ports')
        port_ids=self.get_port_ids_host(host_id=host_id)
        service_ids=[]
        for port_id in port_ids:
            cursor=self.select(table_name='ports',
                               column_names=['*'],
                               where='port_id='+str(port_id))
            for row in cursor:
                port=row[1]
                port_info[port]={}
                i=0
                for col in row:
                    if not(port_cols[i] in ignore):
                        port_info[port][port_cols[i]]=col
                    if port_cols[i]=='service_id':
                        service_ids.append(col)
                        service_cols=self.get_column_names(table_name='services')
                        c=self.get_all_from_service(service_id=col)
                        for r in c:
                            j=0
                            for scol in r:
                                if not(service_cols[j] in ignore):
                                    port_info[port][service_cols[j]]=scol
                                j+=1
                    i+=1
        

        results={}
        results['host']={}
        for key, el in host_info.items():
            results['host'][key]=el
            
        results['host']['ports']=[]
        for key, el in port_info.items():
            results['host']['ports'].append({key:el})
        return results

    def get_all(self):
        results={}
        subnets = self.get_all_subnets()

        for s in subnets:
            results[s]={}
            for host in self.get_hosts_from_subnet(subnet=s):
                results[s]=self.get_all_from_host(ip=host)

        return results

    def get_column_names(self, table_name):
        cursor=self.get_columns(table_name=table_name)

        columns=[]
        for row in cursor:
            columns.append(row[1])

        return columns
                            
    def create_nmap_tables(self):
        self.create_cmd_table()
        self.create_subnet_table()
        self.create_host_table()
        self.create_services_table()
        self.create_scripts_table()
        self.create_ports_table()
        self.create_os_table()

    def create_cmd_table(self):
        """
        """
        if not('commands' in self.tables):
            self.create_table(table_name='commands',
                              column_names=['command_id', 'command',
                                            'status_code', 'time',
                                            'datetime'],
                              column_types=['INTEGER', 'char(500)',
                                            'INTEGER', 'FLOAT',
                                            'char(50)'],
                              pk_index=0, notnull=[0])
        
    def create_host_table(self):
        """
        """
        if not('hosts' in self.tables):
            self.create_table(table_name='hosts',
                              column_names=['host_id', 'ip', 'status',
                                            'open_ports', 'reason',
                                            'vendor', 'hostname',
                                            'icmp_echo','icmp_netmask',
                                            'icmp_timestamp', 'subnet_id'],
                              column_types=['INTEGER', 'char(50)', 'char(50)',
                                            'INTEGER', 'char(50)',
                                            'char(100)', 'char(100)',
                                            'char(20)', 'char(20)',
                                            'char(20)', 'INTEGER'],
                              pk_index=0, notnull=[0])

    def create_subnet_table(self):
        """
        """
        if not('subnets' in self.tables):
            self.create_table(table_name='subnets',
                              column_names=['subnet_id', 'ip_cidr',
                                            'hosts_up'],
                              column_types=['INTEGER', 'char(50)',
                                            'INTEGER'],
                              pk_index=0, notnull=[0])

    def create_services_table(self):
        """
        """
        if not('services' in self.tables):
            self.create_table(table_name='services',
                              column_names=['service_id', 'name',
                                            'product', 'version',
                                            'extrainfo', 'ostype',
                                            'method'],
                              column_types=['INTEGER', 'char(50)',
                                            'char(100)', 'char(100)',
                                            'char(100)', 'char(100)',
                                            'char(100)'],
                              pk_index=0, notnull=[0])
                        
    def create_scripts_table(self):
        """
        """
        if not('scripts' in self.tables):
            self.create_table(table_name='scripts',
                              column_names=['script_id', 'id',
                                            'output', 'port_id'],
                              column_types=['INTEGER', 'char(50)',
                                            'char(100)', 'INTEGER'],
                              pk_index=0, notnull=[0])

    def create_ports_table(self):
        """
        """
        if not('ports' in self.tables):
            self.create_table(table_name='ports',
                              column_names=['port_id', 'port',
                                            'reason', 'service_id',
                                            'host_id'],
                              column_types=['INTEGER', 'INTEGER',
                                            'char(100)', 'INTEGER',
                                            'INTEGER'],
                              pk_index=0, notnull=[0])

    def create_os_table(self):
        """
        """
        if not('os' in self.tables):
            self.create_table(table_name='os',
                              column_names=['os_id', 'name',
                                            'accuracy', 'host_id'],
                              column_types=['INTEGER', 'char(100)',
                                            'INTEGER','INTEGER'],
                              pk_index=0, notnull=[0])

    def str(self, var):
        return "'"+str(self.clean(var))+"'"
                    
db=NMAP_DB()
