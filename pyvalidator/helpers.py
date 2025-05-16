from ruamel.yaml import YAML
from typing import List, Dict
import re


# def get_line_number(node):
#     if hasattr(node, 'start_mark'):
#         return node.start_mark.line + 1  # ruamel uses zero-based lines
#     if hasattr(node, 'lc'):
#         return node.lc.line + 1
#     return None

    
def decipher_error_messages(errors: List[Dict[str, str]],schema=None, schema_path=None,) -> List[str]:
    
    yaml = YAML()
    if schema_path:
        with open(schema_path, 'r') as file:
            yaml_file = yaml.load(file)
    else:
        yaml_file = schema
    
    error_messages = []
    for error in errors:
        loc = list(error.get("loc", []))
        msg = error.get("msg", "")
        _type = error.get("type", "")
        
        if _type == "missing":
            node = yaml_file
            keys = list(node.keys())
            node = node[keys[0]]
            for key in loc[:-1]:
                node = node.key
            line_number = node.start_mark.line
            missing_element = loc[-1]
            parent_element = loc[-2] if len(loc) > 1 else None
            error_messages.append(f"Missing element '{missing_element}' in '{parent_element}' at line {line_number + 1}")
        
        if re.match(r"^[\w]*_type", _type):
            node = yaml_file
            keys = list(node.keys())
            node = node[keys[0]]
            for key in loc[:-1]:
                node = node[key]
            line_number = node.lc.data[loc[-1]][0] + 1 
            error_messages.append(f"Invalid type for '{loc[-1]}' at line {line_number + 1}: {msg}")
            
        if _type == "table_name_mismatch":
            node = yaml_file
            keys = list(node.keys())
            node = node[keys[0]]
            line_number = node.lc.data[0] + 1 
            error_messages.append(f"{msg} at line number {line_number}")
            
        else:
            node = yaml_file
            keys = list(node.keys())
            node = node[keys[0]]
            for key in loc[:-1]:
                node = node[key]
            line_number = node.lc.data[loc[-1]][0] + 1 
            error_messages.append(f"{msg} at line number {line_number}")
    
    return error_messages