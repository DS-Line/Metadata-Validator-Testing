import re
from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import List, Dict, Optional, Generic, TypeVar, Type            
import sys
import yaml    


import logging
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError 
from ruamel.yaml.comments import CommentedMap

from pyvalidator.helpers import decipher_error_messages, print_decorated_section


class TableInfo(BaseModel):
    table: str
    joins: List[str]
    
    
    @field_validator('joins')
    @classmethod
    def _validate_joins_format(cls, joins):
        if not joins:
            return joins
        
        for condition in joins:
            pattern = r'^[\w]+\.[\w]+\s*=\s*[\w]+\.[\w]+$'
            if not isinstance(condition,str) or not re.match(pattern,condition):
                raise ValueError(
                    f'Invalid join condition format: "{condition}". Expected format: "table.column = table.column"'
                )
        return joins
    
    @field_validator('table')
    @classmethod
    def _empty_table(cls,table_name):
        if table_name.strip() == "":
            raise ValueError("Empty table name in table_info")
        return table_name
    
    
class Column(BaseModel):
    name: str
    type: str
    column: str
    desc: str
    primary_key: Optional[bool] = None
    foreign_key: Optional[bool] = None
    table : Optional[str] = None
    fetch: Optional[bool] = None
    

class GeneratedSchema(BaseModel):
    subject_area: str
    table_info: List[TableInfo]
    columns: Dict[str, Column]
    
    
    # tables_in_schema = {table.table for table in table_info}
    
    
    @model_validator(mode="after")
    def _check_unique_column_id(self):
        columns = list(self.columns.keys())
        column_ids = set()
        for column_id in columns:
            if column_id not in column_ids:
                column_ids.add(column_id)
            else:
                raise ValueError("Columns ids not unique")
        return self   
    
    @model_validator( mode="after")
    def _check_column_name_format(self):
        columns = self.columns
        # columns = values.get("columns",{})
        pattern = r'[a-zA-Z_][a-zA-Z0-9_]*$'
        for column_id, column in columns.items():
            if not re.match(pattern, column_id):
                raise ValueError(f"Column name: {column_id} not matching with the column name format")  
        return self
        
    @model_validator(mode="after")
    def _validate_table_reference(self):
        tables_set = set()
        tables = self.table_info
        for table in tables:
            tables_set.add(table.table)
        
        columns = self.columns
        for column_id, column in columns.items():
            if column.table != None:
                if type(column.table) == str:
                    reference = column.table
                    if reference not in tables_set:
                        raise ValueError(f"{column['table']} reference missing")
                elif type(column.table) == list:
                    for reference in column['table']:
                        if reference not in tables_set:
                            raise ValueError(f"{column['table']} reference missing")
        return self 
    

GeneratedSchemaType = TypeVar('GeneratedSchemaType', bound=GeneratedSchema)

class SchemaWrapper(BaseModel, Generic[GeneratedSchemaType]):
    root: Dict[str, GeneratedSchemaType]

    
    
    
    
    
    
    
    
class SourceColumns(BaseModel):
    columns: List[str]




class Attributes(BaseModel):
    name: str
    synonym: Optional[List[str]] = None 
    description: str
    include: Optional[List[str]] = None  
    output_consideration: Optional[str] = None 
    relevant_attributes: Optional[List[str]] = None 



class Metrics(BaseModel):
    name: str
    synonym: Optional[List[str]] = None
    description: Optional[str] = None
    calculation: Optional[str] = None
    granularity: Optional[List[str]] = None
    include: Optional[List[str]] = None
    function: Optional[str] = None
    



# SourceType = TypeVar("SourceType", bound=Source)
class GeneratedSemantics(BaseModel):
    folder: str
    type: str
    source: Optional[Dict[str,SourceColumns]] = None
    attributes: Dict[str, Attributes]
    metrics: Dict[str, Metrics]
    
    
GeneratedSemanticsType = TypeVar("GeneratedScemanticsType", bound= GeneratedSemantics)
class SemanticWrapper(BaseModel, Generic[GeneratedSemanticsType]):
    root: Dict[str, GeneratedSemanticsType]
    


def schema_main(schema_path):
    
    print_decorated_section(title="Validating Schema Format")
    
    yaml = YAML()
    
    with open(schema_path, 'r') as file:
        yaml_file = yaml.load(file)
    
    # Extract key from the yaml file    
    keys = list(yaml_file.keys())
    yaml_file = yaml_file[keys[0]]
    
    # wrapping schema into the schema wrapper
    try:
        schema = GeneratedSchema(**yaml_file)
    except ValidationError as error:
        error = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in error.errors()]
        return error
    
def validate_schema_format(schema_path:str):
    output = schema_main(schema_path=schema_path)
    if output is not None:
        errors = decipher_error_messages(yaml_path=schema_path, errors=output)
        print_decorated_section(title="Format Validation Failed", content=errors)
        return errors
        
    else:
        print_decorated_section(title="Format Validation Passed")
    

def semantic_main(semantic_path):
    yaml = YAML()

    print_decorated_section(title="Validating Formats in Semantics")
    # semantic_path = "assets/semantics/movies.yml"
    with open(semantic_path, 'r') as file:
        try:
            yaml_file = yaml.load(file)
        except DuplicateKeyError as e:
            print_decorated_section(title="Duplicate Key found", content=[f"Duplicate Key found: {e}"])
        
        
    
    keys = list(yaml_file.keys())
    yaml_file = yaml_file[keys[0]]
    
    try:
        semantic = GeneratedSemantics(**yaml_file)
        print_decorated_section(title="Format Validation Passed")
    except ValidationError as error:
        error = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in error.errors()]
        return error
    
    
def validate_semantic_format(semantic_path:str):
    output = semantic_main(semantic_path=semantic_path)
    if output is not None:
        errors = decipher_error_messages(yaml_path=semantic_path, errors=output)
        print_decorated_section(title="Format Validation Failed", content=errors)
        return errors
            
    else:
        print_decorated_section(title="Format Validation Passed")
            
            
if __name__ == "__main__":
    validate_semantic_format(semantic_path="./assets/semantics/movies.yml")