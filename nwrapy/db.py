import sqlite3
import sys
from threading import Lock

class DB():

    def __init__(self):
        """
        """
        pass

    def _init(self, db_name):
        self._lock=Lock()
        self.db_name=self.__init_name(name=db_name)
        try:
            self.conn=sqlite3.connect(self.db_name)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(1)
            
    def __init_name(self, name):
        """
        Initialise the database name
        """
        if not(type(name)==str):
            name=str(name)
        if not(name.endswith('.db')):
            name+='.db'
            
        return name
        
    def query(self, query):
        with self._lock:
            try:
                cursor = self.conn.execute(query)
            except Exception as e:
                print('Could not execute query:', query, file=sys.stderr)
                print('Error:', e, file=sys.stderr)
                sys.exit(1)

        return cursor

    def create_table(self, table_name: str, column_names: list,
                     column_types: list, pk_index:int=0,
                     notnull:list=[0]):
        if not(len(column_types)==len(column_names)):
            raise ValueError("Different number of column types and column names")
        
        query='CREATE TABLE '+table_name+' ('

        clmns=[]
        for index in range(len(column_names)):
            line=column_names[index]+' '+column_types[index]
            if index==pk_index:
                line+=' PRIMARY KEY AUTOINCREMENT'
            if index in notnull:
                line+=' NOT NULL'
            #if not(column_names[index]==column_names[-1]):
            #    line+=','
            clmns.append(line)

        clmns=', '.join(clmns)
        query+=clmns+');'
        self.query(query=query)

    def insert(self, table_name: str, column_names: list, values: list):
        if not(len(column_names)==len(values)):
            raise ValueError("Different number of column names and values")

        query='INSERT INTO '+table_name+' ('+', '.join(column_names)+')' \
            +' VALUES ('+', '.join(values)+');'
        self.query(query=query)
        self.conn.commit()

    def update(self, table_name: str, column_name: str, value: str, where: str):
        query='UPDATE '+table_name+' SET '+column_name+'='+value+' WHERE '+where
        self.query(query=query)
        self.conn.commit()

    def select(self, table_name:str, column_names:list, where:str=None):
        query='SELECT '+','.join(column_names)+' FROM '+table_name
        if where:
            query+=' WHERE '+where

        cursor=self.query(query=query)
        return cursor

    def show_tables(self):
        query='''SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%';'''
        rows=self.query(query=query)
        for row in rows:
            for name in row:
                print(name)
                rs = self.get_columns(table_name=name)
                for r in rs:
                    print(r)

    def get_tables(self):
        query='''SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%';'''
        rows=self.query(query=query)
        names=[]
        for row in rows:
            for name in row:
                names.append(name)
        return names

    def get_columns(self, table_name):
        query="PRAGMA table_info('"+table_name+"');"
        res=self.query(query=query)
        return res

    def clean(self, string):
        repl={"'":" "}
        for k,v in repl.items():
            string=string.replace(k,v)
        return string

if __name__=='__main__':
    db = DB(db_name='test.db')
    
    db.create_table(table_name='targets',
                    column_names=['target_id', 'domain', 'protocol', 'description'],
                    column_types=['int', 'char(50)', 'char(50)', 'char(100)'],
                    pk_index=0, notnull=[0])
    db.create_table(table_name='links_internal',
                    column_names=['url', 'origin', 'status', 'target_id'],
                    column_types=['char(400)', 'char(400)', 'int', 'int'])
    db.create_table(table_name='links_external',
                    column_names=['url', 'origin', 'status', 'target_id'],
                    column_types=['char(400)', 'char(400)', 'int', 'int'])
    db.create_table(table_name='subdomains',
                    column_names=['domain', 'origin', 'target_id'],
                    column_types=['char(400)', 'char(400)', 'int'])
    db.show_tables()
