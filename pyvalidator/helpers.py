from ruamel.yaml import YAML
from typing import List, Dict
import types
import re
from ruamel.yaml.comments import CommentedMap


# def get_line_number(node):
#     if hasattr(node, 'start_mark'):
#         return node.start_mark.line + 1  # ruamel uses zero-based lines
#     if hasattr(node, 'lc'):
#         return node.lc.line + 1
#     return None




def decipher_error_messages(yaml_path :str,errors: List[Dict[str, str]]) -> List[str]:
    
    
    def get_top_level_line(key):
        line_num = 1  # fallback
        if hasattr(yaml_file, "lc") and isinstance(yaml_file, CommentedMap):
            try:
                line_num = yaml_file.lc.data.get(key, [0])[0] + 1
            except Exception:
                pass
        return line_num
    
    
    yaml = YAML()
    with open(yaml_path, 'r') as file:
        yaml_file = yaml.load(file)
    
    error_messages = []
    for error in errors:
        loc = error.get("loc", [])

        # Fix for 'types.GenericAlias' and other strange types
        if isinstance(loc, (type, types.GenericAlias)):
            loc = []

        # Defensive normalization
        if isinstance(loc, str):
            loc = [loc]
        elif not isinstance(loc, (list, tuple)):
            try:
                loc = list(loc)
            except Exception:
                loc = []

        msg = error.get("msg", "")
        _type = error.get("type", "")

        if _type == "missing":
            if len(loc) == 1:
                missing_key = loc[0]
                line_number = get_top_level_line(missing_key)
                error_messages.append(
                        f"Missing top-level element '{missing_key}' at or near line {line_number}"
                    )
                continue

            # else follow original deeper logic
            node = yaml_file
            keys = list(node.keys())
            node = node[keys[0]]

            parents = []
            for key in loc[:-1]:
                if not isinstance(node, dict):
                    node = None
                    break
                parents.append((node, key))
                node = node.get(key)

            line_number = None
            for parent, key in reversed(parents):
                if hasattr(parent, "lc") and isinstance(parent, CommentedMap):
                    try:
                        line_number = parent.lc.data[key][0] + 1
                        break
                    except (KeyError, IndexError, TypeError):
                        continue

            missing_element = loc[-1]
            parent_element = loc[-2] if len(loc) > 1 else None

            if line_number is not None:
                error_messages.append(
                        f"Missing element '{missing_element}' in '{parent_element}' at line {line_number}"
                    )
            else:
                error_messages.append(
                        f"Missing element '{missing_element}' in '{parent_element}' (line unknown)"
                    )

        elif re.match(r"^[\w]*_type", _type):
            if len(loc) == 1:
                key = loc[0]
                line_number = get_top_level_line(key)
                error_messages.append(
                        f"Invalid type for top-level '{key}' at or near line {line_number}: {msg}"
                    )
                continue

            node = yaml_file
            keys = list(node.keys())
            node = node[keys[0]]

            for key in loc[:-1]:
                node = node[key]

            try:
                line_number = node.lc.data[loc[-1]][0] + 1
            except (KeyError, IndexError, TypeError, AttributeError):
                line_number = None

            if line_number is not None:
                error_messages.append(
                        f"Invalid type for '{loc[-1]}' at line {line_number}: {msg}"
                    )
            else:
                error_messages.append(
                        f"Invalid type for '{loc[-1]}' (line unknown): {msg}"
                    )

        elif _type == "table_name_mismatch":
            if len(loc) == 1:
                key = loc[0]
                line_number = get_top_level_line(key)
                error_messages.append(f"{msg} at or near line {line_number}")
                continue

            node = yaml_file
            keys = list(node.keys())
            node = node[keys[0]]

            for key in loc[:-1]:
                node = node[key]

            key_for_line = loc[-1] if loc else keys[0]

            try:
                line_number = node.lc.data[key_for_line][0] + 1
            except (KeyError, IndexError, TypeError, AttributeError):
                line_number = None

            if line_number is not None:
                error_messages.append(f"{msg} at line number {line_number}")
            else:
                error_messages.append(f"{msg} at unknown line")

        else:
            if len(loc) == 1:
                key = loc[0]
                line_number = get_top_level_line(key)
                error_messages.append(f"{msg} at or near line {line_number}")
                continue

            node = yaml_file
            keys = list(node.keys())
            node = node[keys[0]]

            for key in loc[:-1]:
                node = node[key]

            try:
                line_number = node.lc.data[loc[-1]][0] + 1
            except (KeyError, IndexError, TypeError, AttributeError):
                line_number = None

            if line_number is not None:
                error_messages.append(f"{msg} at line number {line_number}")
            else:
                error_messages.append(f"{msg} at unknown line")
        
    return error_messages



def print_decorated_section(title: str, content = None):
    border = "=" * 60
    separator = "-" * 60
    print(f"\n{border}")
    print(f"{title.center(60)}")
    print(f"{separator}")
    if content:
        for line in content:
            print(f"  • {line}")
    print(f"{border}\n")



