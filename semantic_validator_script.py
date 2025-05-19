from pyvalidator.format_validator import validate_semantic_format
from pyvalidator.semantic_validator import SemanticsValidator
from ruamel.yaml import YAML


schema_path = "./assets/schema/movies.yml"
semantic_path = "./assets/semantics/movies.yml"

validator = SemanticsValidator(schema_path)

format_errors = validate_semantic_format(semantic_path)
if not format_errors:
    semantic_errors = validator.validate_semantics(semantic_path)
else:
    print("Format Validation Failed")
