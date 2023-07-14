import sqlite3
import os

class Column:
    def __init__(self, name: str, type_: object = str, *, primary_key: bool = False, can_be_null: bool = True, default = None, unique: bool = False, reference):
        self.name = name
        self.type = type_

        self.attributes = []
        if primary_key:
            self.attributes.append("PRIMARY KEY")
        if not can_be_null:
            self.attributes.append("NOT NULL")
        if unique:
            self.attributes.append("UNIQUE")
        if default:
            self.attributes.append(f"DEFAULT '{default}'")

        if reference:
            if isinstance(reference, Column):
                if hasattr(reference, "table"):
                    self.reference = f"{reference.table}({reference.name})"
                else:
                    raise Exception("Column objects given as references must be part of a Table")
            elif isinstance(reference, tuple):
                if len(reference) == 2:
                    self.reference = f"{reference[0]}({reference[1]})"
                else:
                    raise Exception("References passed as tuples must have a length of 2 and be in the format of (table, column)")
            else:
                raise Exception("References must be given as Column objects or tuples of length 2")
        else:
            self.reference = None

    def __repr__(self):
        return f"{self.name} {self.type} {' '.join(self.attributes)}"


class _Tables:
    def __init__(self, *tables):
        for table in tables:
            self.__setattr__(table, table)

    def append(self, table):
        self.__setattr__(table, table)

class Database:
    def __init__(self, name: str, *, path: str = None, force_new: bool = False):
        if not path:
            path = name + ".db"

        self._path = path
        self.new_db = True

        if os.path.exists(path):
            if force_new:
                os.remove(path)
            else:
                self.new_db = False
        
        self.tables = _Tables()

        self._con = self.connect()

    def _execute(self, command: str, *, ignore_err: bool = False):
        cur = self._con.cursor()
        
        if ignore_err:
            try:
                cur.execute(command)
            except:
                ret = False
            else:
                ret = True
        else: 
            cur.execute(command)
            ret = True

        cur.close()
        return ret

    def connect(self):
        self.close(ignore_closed=True)
        self._con = sqlite3.connect(self._path)
        return True
    
    def close(self):
        try:
            self._con.close()
        except:
            return False
        
        return True

    def create_table(self, name: str, *, columns: list[Column], ignore_existing: bool = False):
        self.tables.append(name)

        command = f"CREATE TABLE {name}("
        for column in columns:
            command += column + ","
            if column.reference:
                command += f"FOREIGN KEY({column.name}) REFERENCES {column.reference},"
        command += ");"

        ignore_err = ignore_existing

        return self._execute(command, ignore_err=ignore_err)

    def select(self, table: str, )
        
        
