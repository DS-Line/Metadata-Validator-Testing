from pyvalidator.format_validator import validate_semantic_format
from pyvalidator.semantic_validator import SemanticsValidator
from ruamel.yaml import YAML
from logger.log import create_logger
import os

yaml = YAML()
logger = create_logger()

metadata_path = "./assets/"
registry_path = os.path.join(metadata_path,"registry.yml")

with open(registry_path,'r') as f:
   registry = yaml.load(f)
   registries = registry.get("registered_yml", None)


for registry in registries:
    schema_path = os.path.join(metadata_path,"schema",registry + ".yml")
    semantic_path = os.path.join(metadata_path, "semantics",registry + ".yml")
    
    validator = SemanticsValidator()

    format_errors = validate_semantic_format(semantic_path)
    if not format_errors:
        semantic_errors = validator.validate_semantics(metadata_path, semantic_path)
    else:
        for msg in format_errors:
            logger.error("Semantic: %s|%s",registry, msg )
        print("Correct Format Before passing it to validate against schema")

    
    if semantic_errors:
        for msg in semantic_errors:
            logger.error("Semantic: %s|%s",registry, msg )      