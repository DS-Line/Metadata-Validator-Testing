import re
from pyvalidator.format_validator import SemanticWrapper, GeneratedSemantics
from pprint import pprint
from typing import Dict, List

from ruamel.yaml import YAML
from pyvalidator.helpers import decipher_error_messages, print_decorated_section


class SemanticsValidator:
    
    def __init__(self, schema=None):
        if isinstance(schema, str):
            yaml = YAML()
            with open(schema, 'r') as f:
                self.schema = yaml.load(f)
        else:
            self.schema = schema
        self.errors = []

    def print_schema(self):
        pprint(self.schema)

    def parse_schema(self):
        schema_dict = dict()
        key = list(self.schema.keys())[0]
        schema = self.schema.get(key)
        schema_dict.update({"folder": key})
        column_ids = list(schema["columns"].keys())
        schema_dict.update({"column_ids": column_ids})
        return schema_dict

    def extract_column_names(self, sql_query: str) -> List[str]:
        pattern = re.compile(r'\[([^\[\]]+)\]')
        tokens = pattern.findall(sql_query)
        return tokens

    def validate_references(self, references: List[str], valid_keys: List[str], context: str, key: str):
        for ref in references:
            if ref not in valid_keys:
                error = {
                    "loc": (context, ref),
                    "type": "invalid_reference",
                    "msg": f"Incorrect reference '{ref}' in {context} of '{key}'. Not found in schema."
                }
                self.errors.append(error)

    def validate_item(self, item: Dict, schema_dict: Dict, reference_columns: List[str], section: str):
        for key, values in item.items():
            if values.get("include"):
                self.validate_references(values["include"], reference_columns, "include", key)

            if values.get("calculation"):
                columns = self.extract_column_names(values["calculation"])
                for col in columns:
                    if col not in (schema_dict["column_ids"] if section == "attributes" else reference_columns):
                        error = {
                            "loc": ("calculation", col),
                            "type": "invalid_reference",
                            "msg": f"Incorrect reference '{col}' in calculation of '{key}'. Not found in schema."
                        }
                        self.errors.append(error)

            if values.get("filter"):
                for filter_expr in values["filter"]:
                    columns = self.extract_column_names(filter_expr)
                    for col in columns:
                        if col not in reference_columns:
                            error = {
                                "loc": ("filter", col),
                                "type": "invalid_reference",
                                "msg": f"Incorrect reference '{col}' in filter of '{key}'. Not found in schema."
                            }
                            self.errors.append(error)

    def validate_semantics(self, semantic_path: str):
        
        print_decorated_section(title="Validating Semantics Against Schema...")

        self.errors = []  # Reset errors
        
        with open(semantic_path) as f:
            yaml = YAML()
            yaml_file = yaml.load(f)
        
        key = list(yaml_file.keys())[0]
        
        generated_semantics = yaml_file.get(key)

        
        schema_dict = self.parse_schema()
        attributes = generated_semantics.get("attributes", {})
        metrics = generated_semantics.get("metrics", {})

        attribute_keys = list(attributes.keys())
        metrics_keys = list(metrics.keys())
        reference_columns = attribute_keys + metrics_keys + schema_dict["column_ids"]

        self.validate_item(attributes, schema_dict, reference_columns, "attributes")
        self.validate_item(metrics, schema_dict, reference_columns, "metrics")

        if self.errors:
            errors = decipher_error_messages(yaml_path=semantic_path, errors=self.errors)
            print_decorated_section(title="Format Validation Failed", content=errors)
                
        else:
            print_decorated_section(title="Semantics successfully validated.")

