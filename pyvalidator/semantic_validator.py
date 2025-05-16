from pyvalidator.format_validator import SemanticWrapper, GeneratedSemantics
from pprint import pprint
from typing import Dict


class SemanticsValidator():
    
    def __init__(self, schema = None):
        self.schema = schema
        
    
    def print_schema(self):
        pprint(self.schema)
        
        
    def parse_schema(self):
        schema = self.schema
        schema_dict = dict()
        
        key = list(schema.keys())[0]
        schema = schema.get(key)
        
        schema_dict.update({"folder": key})
        
        column_ids = [col for col in list(schema["column"].keys())]
        
        schema_dict.update({"column_ids": column_ids})
        
        return schema_dict
            
        
        
        
        
        
        
    def validate_semantics(self, generated_semantics: Dict):
        schema_dict = self.parse_schema()
        
        