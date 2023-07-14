import sqlite3
import os
import json
import sys

class Model:
    def __init__(self, **set_columns):
        for column in set_columns:
            setattr(self, column, set_columns[column])

class Column:
    def __init__(self, datatype: str, *, null: bool = False, primary: bool = False, unique: bool = False, autoincrement: bool = False, default = None, foreign_key = None):
        if datatype == "int":
            datatype = "integer"
        datatype = datatype.upper()

        if datatype not in ["NULL", "INTEGER", "REAL", "TEXT", "BLOB"]:
            raise Exception(f"Invalid datatype {datatype}")

        self.datatype = datatype
        self.nullable = null
        self.primary_key = primary
        self.unique = unique
        self.default = default
        self.foreign_key = foreign_key

        if self.primary_key:
            if self.datatype != "INTEGER":
                raise Exception(f"PRIMARY KEYs must be INTEGERs, not {self.datatype}s.")

            self.nullable = False
            self.unique = True
            self.autoincrement = True

            if self.default:
                raise Exception(f"PRIMARY KEYs must not have a DEFAULT. DEFAULT of '{self.default}' was given.")
        
            if self.foreign_key:
                raise Exception(f"PRIMARY KEYs must not have a FOREIGN KEY association.")
            
class Database:
    def __init__(self, db_file: str, *columns: list[Column]):
        if os.path.isfile(db_file):
            con = sqlite3.connect(db_file)
            cur = con.cursor()

            old_sql_fetched = cur.execute("SELECT sql FROM sqlite_master;").fetchall()

            cur.close()
            con.close()

            old_creations = [table_creation for table_creation, in old_sql_fetched if table_creation is not None]

            # IMPORTANT NOTE: this currently only works for tables with CAPITAL sql code and in the good indent format

            old_tables = {}
            for table_code in old_creations:
                # executed for each table
                code_lines = table_code.splitlines()
                table_name = code_lines[0].split("CREATE TABLE ")[1].split("(")[0]
                
                old_tables[table_name] = {}
                foreign_keys = {}

                for line in code_lines[1:-1]:
                    # executed for each column
                    line = line.strip().replace(",", "")

                    if "FOREIGN KEY" in line:
                        # not a column, fix foreign key
                        line_split = line.split("REFERENCES")
                        local_column = line_split[0].strip().split("(")[1].replace(")", "")
                        foreign_column = line_split[1].strip().replace(")", "").replace("(", ".")
                        foreign_keys[local_column] = foreign_column

                    else:
                        line_split = line.split(" ", 1)
                        column_name = line_split[0]
                        column_attributes = line_split[1]
                        column_attributes_split = column_attributes.split(" ")
                        column_attributes_lower = column_attributes.lower()
                        column_attributes_lower_split = column_attributes_lower.split(" ")

                        old_tables[table_name][column_name] = {}
                        
                        if "not null" in column_attributes_lower:
                            column_attributes.replace("not null", "")
                            null_this = False
                        else:
                            null_this = True

                        old_tables[table_name][column_name]["datatype"] = column_attributes_split[0].upper()
                        old_tables[table_name][column_name]["nullable"] = null_this
                        
                        if "primary key" in column_attributes_lower:
                            old_tables[table_name][column_name]["primary_key"] = True
                        
                        if "unique" in column_attributes_lower:
                            old_tables[table_name][column_name]["unique"] = True
                        
                        if "default" in column_attributes_lower:
                            default_kw_pos = column_attributes_lower_split.index("default")
                            default_value = column_attributes_split[default_kw_pos + 1]
                            old_tables[table_name][column_name]["default"] = default_value

                # fix foreign key associations
                for local_column in foreign_keys.keys():
                    old_tables[table_name][local_column]["foreign_key"] = foreign_keys[local_column]

            with open("test.json", "w") as f:
                json.dump(old_tables, f, indent=4)

            