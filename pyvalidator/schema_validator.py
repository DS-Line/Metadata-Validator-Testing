import yaml
from typing import List, Dict
from pyvalidator.format_validator import SchemaWrapper, GeneratedSchema, TableInfo, Column
from simple_ddl_parser import DDLParser
from pprint import pprint
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError
import sys



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
    
    def validate_schema(self, generated_schema: Dict):
        errors = []  # collect errors here
        
        schema_key = list(generated_schema.keys())[0]
        schema = generated_schema[schema_key]
        
        try:
            schema = GeneratedSchema(**schema)
        except Exception as e:
            errors.append(f"Schema parsing error: {e}")
            # If schema itself can't parse, stop validation here
            self._print_errors(errors)
            return
        
        schema_table_name = schema.table_info[0].table

        if schema_table_name != self.ddl[0]["table_name"]:
            errors.append(f"Table name mismatch: {schema_table_name} not in DDL")
        
        schema_columns = {col.column: col for col in schema.columns.values()} 
        ddl_primary_keys = self.ddl[0]["primary_key"]
        
        for ddl_col in self.ddl[0]['columns']:
            ddl_col_name = ddl_col['name']
            ddl_col_type = ddl_col['type'].upper()

            if ddl_col_name not in schema_columns:
                errors.append(f"DDL column '{ddl_col_name}' not found in schema.")
                continue

            schema_col_type = schema_columns[ddl_col_name].type.upper()
            if not self.types_are_equivalent(ddl_col_type, schema_col_type):
                errors.append(f"Type mismatch for column '{ddl_col_name}': DDL type '{ddl_col_type}', Schema type '{schema_col_type}'.")

            if ddl_col_name in ddl_primary_keys:
                if not schema.columns[ddl_col_name].primary_key:
                    errors.append(f"'{ddl_col_name}' not stated as primary key in Schema")
            else:
                if schema.columns[ddl_col_name].primary_key:
                    errors.append(f"'{ddl_col_name}' stated as primary key in Schema which isn't a primary key")
            
            if schema_columns[ddl_col_name].fetch:
                if schema_columns[ddl_col_name].type.upper() == "NUMBER":
                    errors.append(f"Invalid fetch value for '{ddl_col_name}': Column type is NUMBER")

        if errors:
            self._print_errors(errors)
        else:
            print("Schema successfully validated against DDL.")
    
    def _print_errors(self, errors: List[str]):
        print("Schema validation errors found:")
        for err in errors:
            print(f"  - {err}")

                
                
                
def main(ddl_path, schema_path):
    
    print("Validating schema against DDL...")
    
    with open(ddl_path, 'r') as f:
        ddl = f.read() 
    
    ddl_validator = SchemaValidator(ddl)

    yaml = YAML()

    try:
        with open(schema_path,'r') as f:
            yaml_file = yaml.load(f)  
    except DuplicateKeyError as e:
        print(f"Duplicate Key found: {e}") 
    
    ddl_validator.validate_schema(yaml_file)
        



