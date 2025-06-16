import re
from pyvalidator.format_validator import SemanticWrapper, GeneratedSemantics
from pprint import pprint
from typing import Dict, List

from ruamel.yaml import YAML
from pyvalidator.helpers import decipher_error_messages, print_decorated_section
import os
from io import StringIO

import yaml as pyyaml

class SemanticsValidator:
    
    def __init__(self):
        self.errors = []
        self.sources = {}
        
    # def get_schema_paths(self, semantics_file):
        

    def print_sources(self):
        pprint(self.sources)

    def _parse_sources(self):
        column_ids = []
        for key,source in self.sources.items():
            if source.get("columns",None):
                columns = list(source["columns"].keys())
                column_ids.extend(columns)
            
            if source.get("attributes", None):
                columns = list(source["attributes"].keys())
                column_ids.extend(columns)
            
            if source.get("metrics",None):
                columns = list(source["metrics"].keys())
                column_ids.extend(columns)
        return column_ids
        
                
    def extract_column_names(self, sql_query: str) -> List[str]:
        pattern = re.compile(r'\[([^\[\]]+)\]')
        tokens = pattern.findall(sql_query)
        return tokens

    def validate_references(self, section:str, references: List[str], valid_keys: List[str], context: str, key: str):
        for ref in references:
            if ref not in valid_keys:
                error = {
                    "loc": (section, key, context, ref),
                    "type": "invalid_reference",
                    "msg": f"Incorrect reference '{ref}' in {context} of '{key}'. Not found in schema."
                }
                self.errors.append(error)

    def _validate_item(self, item: Dict, reference_columns: List[str], section: str):
        for key, values in item.items():
            if values.get("include"):
                self.validate_references(section, values["include"], reference_columns, "include", key)

            if values.get("calculation"):
                columns = self.extract_column_names(values["calculation"])
                for col in columns:
                    if col not in reference_columns:
                        error = {
                            "loc": (section,key,"calculation", col),
                            "type": "invalid_reference",
                            "msg": f"Incorrect reference '{col}' in calculation of '{key}'. Not found in columns/attributes/metrics of any source ."
                        }
                        self.errors.append(error)

            if values.get("filter"):
                for filter_expr in values["filter"]:
                    columns = self.extract_column_names(filter_expr)
                    for col in columns:
                        if col not in reference_columns:
                            error = {
                                "loc": (section, key, "filter", col),
                                "type": "invalid_reference",
                                "msg": f"Incorrect reference '{col}' in filter of '{key}'. Not found in schema."
                            }
                            self.errors.append(error)
    
    def _get_sources(self, sources: dict, metadata_path:str):
        yaml = YAML()
        
        registry_path = os.path.join(metadata_path, "registry.yml")
        with open(registry_path) as f:
            registry = yaml.load(f)
            registries = registry.get("registered_yml", None)
        
        source_keys = list(sources.keys())
        
        parsed_sources = [
            {"prefix":source.partition(".")[0], "file_name": source.partition(".")[2]}
            for source in source_keys
        ]
        
        for parsed_source in parsed_sources:
            source_type = parsed_source.get("prefix", None)
            file_name = parsed_source.get("file_name",None)
            
            # if file_name in registries:
            source_path = os.path.join(metadata_path, source_type, file_name + ".yaml")
            
            try:
                with open(source_path) as f:
                    source_raw = yaml.load(f)
                    buf = StringIO()
                    yaml.dump(source_raw, buf)
                    source_raw = pyyaml.safe_load(buf.getvalue())
            except FileNotFoundError as e:
                self.errors.append(
                        {
                            "loc": ("source", f"{source_type}.{file_name}"),
                            "type": "file_not_found",
                            "msg": f"{e}"
                        }
                    )
                print_decorated_section(title="File Not Found", content=self.errors)
                continue

            source_key = f"{source_type}.{file_name}"
            
            specified_source = sources[source_key]
            filtered_source = {}
            filtered_columns = {}
            
            if source_type == "schema":
                columns = specified_source.get("columns", None)
                
                if columns == ["<all>"]:
                    self.sources.update(source_raw)
                
                else:
                    source_raw = source_raw[file_name]
                    for column in columns:
                        filtered_columns.update({column:source_raw["columns"].get(column, None)})

                    filtered_source.update({"subject_area":source_raw["subject_area"]})
                    filtered_source.update({"table_info":source_raw["table_info"]})
                    filtered_source.update({"columns":filtered_columns})
                    self.sources.update({file_name: filtered_source})
                    
                
            elif source_type == "semantics":
                attributes = specified_source.get("attributes", None)
                metrics = specified_source.get("metrics, None")
                
                if attributes:

                    if attributes == ["<all>"]:
                        self.sources.update(source_raw)
                    
                    else:
                        for column in attributes:
                            filtered_columns.append(source_raw["attributes"].get(column, None))
                            filtered_source.update({"attributes":filtered_columns})
                            
                if metrics:
                    filtered_columns = []
                    if metrics == ["<all>"]:
                        self.sources.update(source_raw)
                    
                    else:
                        for column in attributes:
                            filtered_columns.append(source_raw["metrics"].get(column, None))                   
                            filtered_metrics = {"metrics": filtered_columns}
                            filtered_source.update({"metrics": filtered_metrics})
                            
                filtered_source.update({"folder":source_raw["folder"]})
                filtered_source.update({"type":source_raw["type"]})
                filtered_source.update({"source":source_raw["source"]})
                self.sources.update({file_name: filtered_source})                    

                
            
            
            # else:
            #     self.errors.append(
            #         {
            #             "loc": ("source", f"{source_type}.{file_name}"),
            #             "type": "missing_in_registry",
            #             "msg": "File Missing in Registry. Also Check if there is a file for this source"                        
            #         }
            #     )
            
            
        
    
    def validate_semantics(self, registry_path:str, semantic_path: str):
        
        print_decorated_section(title="Validating Semantics Against Schema...")

        self.errors = []  # Reset errors
        
        with open(semantic_path) as f:
            yaml = YAML()
            yaml_file = yaml.load(f)
            
        
        key = list(yaml_file.keys())[0]
        
        generated_semantics = yaml_file.get(key)
        
        sources = generated_semantics.get("source",{})

        self._get_sources(sources, registry_path)
        
        source_columns = self._parse_sources()
        
        
        attributes = generated_semantics.get("attributes", {})
        metrics = generated_semantics.get("metrics", {})

        attribute_keys = list(attributes.keys())
        metrics_keys = list(metrics.keys())
        reference_columns = attribute_keys + metrics_keys + source_columns

        self._validate_item(attributes, reference_columns, "attributes")
        self._validate_item(metrics, reference_columns, "metrics")

        if self.errors:
            errors = decipher_error_messages(yaml_path=semantic_path, errors=self.errors)
            print_decorated_section(title="Semantics Validation Failed", content=errors)
            return errors
        else:
            print_decorated_section(title="Semantics successfully validated.")
            return None
