import yaml
from typing import List, Dict
from pyvalidator.format_validator import SchemaWrapper, GeneratedSchema, TableInfo, Column
from simple_ddl_parser import DDLParser
from pprint import pprint
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError
import sys
from pyvalidator.helpers import decipher_error_messages, print_decorated_section



def parse_ddl_to_metadata(ddl:str):
    return DDLParser(ddl).run(output_mode="hql")



class SchemaValidator():
    
    TYPE_EQUIVALENTS = {
        "NUMBER": {"DECIMAL", "FLOAT", "NUMBER", "DOUBLE", "NUMERIC"},
        "INT": {"INT", "INTEGER", "BIGINT", "SMALLINT"},
        "VARCHAR": {"VARCHAR", "TEXT", "STRING", "CHAR"},
        "DATE": {"DATE", "DATETIME", "TIMESTAMP"}
    }
    
    def __init__(self, ddls=None):
        self.ddl = parse_ddl_to_metadata(ddls)
    
    def print_ddl(self):
        pprint(self.ddl)
        
    def types_are_equivalent(self, ddl_type: str, schema_type: str) -> bool:
        ddl_type = ddl_type.upper()
        schema_type = schema_type.upper()
        for equivalents in self.TYPE_EQUIVALENTS.values():
            if ddl_type in equivalents and schema_type in equivalents:
                return True
        return ddl_type == schema_type  # fallback: exact match
    
    def validate_schema(self, schema_path: str):
        errors = []  # collect errors here
        
        
        with open(schema_path) as f:
            yaml = YAML()
            generated_schema = yaml.load(f)
        
        schema_key = list(generated_schema.keys())[0]
        schema = generated_schema[schema_key]
        
        try:
            schema = GeneratedSchema(**schema)
        except Exception as e:
            errors.append(f"Schema parsing error: {e}")
            # If schema itself can't parse, stop validation here
            return
        
        schema_table_name = schema.table_info[0].table

        if schema_table_name != self.ddl[0]["table_name"]:
            error = {
                "loc": ('table_info'),
                "type" : "table_name_mismatch",
                "msg": f"Schema table name '{schema_table_name}' does not match DDL table name '{self.ddl[0]['table_name']}'"
            }
            errors.append(error)
        
        schema_columns = {col.column: col for col in schema.columns.values()} 
        ddl_primary_keys = self.ddl[0]["primary_key"]
        
        for schema_col_name in schema_columns.keys():
            if schema_col_name not in {col['name'] for col in self.ddl[0]['columns']}:
                error = {
                    "loc": ('columns', schema_col_name),
                    "type": "column_extra_in_schema",
                    "msg": f"Schema column '{schema_col_name}' not found in DDL."
                }
                errors.append(error)
        
        
        for ddl_col in self.ddl[0]['columns']:
            ddl_col_name = ddl_col['name']
            ddl_col_type = ddl_col['type'].upper()

            if ddl_col_name not in schema_columns:
                error = {
                    "loc": ('columns', ddl_col_name),
                    "type" : "column_not_found",
                    "msg": f"DDL column '{ddl_col_name}' not found in schema."
                }
                errors.append(error)
                continue

            schema_col_type = schema_columns[ddl_col_name].type.upper()
            if not self.types_are_equivalent(ddl_col_type, schema_col_type):
                error = {
                    "loc": ('columns', ddl_col_name),
                    "type" : "type_mismatch",
                    "msg": f"Type mismatch for column '{ddl_col_name}': DDL type '{ddl_col_type}', Schema type '{schema_col_type}'"}
                errors.append(error)

            if ddl_col_name in ddl_primary_keys:
                if not schema.columns[ddl_col_name].primary_key:
                    error = {
                        "loc": ('columns', ddl_col_name),
                        "type" : "primary_key_mismatch",
                        "msg": f"DDL primary key '{ddl_col_name}' not found in schema."
                    }
                    errors.append(error)
            else:
                if schema.columns[ddl_col_name].primary_key:
                    error = {
                        "loc": ('columns', ddl_col_name),
                        "type" : "primary_key_mismatch",
                        "msg": f"Schema primary key '{ddl_col_name}' not found in DDL."
                    }
                    errors.append(error)
            
            if schema_columns[ddl_col_name].fetch:
                if schema_columns[ddl_col_name].type.upper() == "NUMBER":
                    error = {
                        "loc": ('columns', ddl_col_name),
                        "type" : "invalid_fetch",
                        "msg": f"Invalid fetch value for '{ddl_col_name}': Column type is NUMBER"
                    }
                    errors.append(error)

        if errors:
            errors = decipher_error_messages(yaml_path=schema_path,errors=errors)
            print_decorated_section(title="Schema Validation Errors", content=errors)
        else:
            print_decorated_section(title="Schema Validation Passed")
    

                
                
                
def main(ddl_path, schema_path):

    print_decorated_section(title="Validating Schema against DDL")
    
    with open(ddl_path, 'r') as f:
        ddl = f.read() 
    
    ddl_validator = SchemaValidator(ddl)

    yaml = YAML()

    try:
        with open(schema_path,'r') as f:
            yaml_file = yaml.load(f)  
    except DuplicateKeyError as e:
        print_decorated_section(title= "Duplicate Key Error", content=[f"Duplicate Key found: {e}"])
        
    
    ddl_validator.validate_schema(schema_path)
        



if __name__ == "__main__":
    main("./assets/DDL/movies.sql", "./assets/schema/movies.yml")