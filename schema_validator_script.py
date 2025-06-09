from pyvalidator.format_validator import validate_schema_format
from pyvalidator.schema_validator import main as validate_schema_ddl
from ruamel.yaml import YAML
import os
from logger.log import create_logger

logger = create_logger()
yaml = YAML()

metadata_path = "./assets/adventure_metadata"

ddl_path = os.path.join(metadata_path,"ddl")
schema_path = os.path.join(metadata_path,"schema")
registry_path = os.path.join(metadata_path,"registry.yml")

with open(registry_path,'r') as f:
   registries = yaml.load(f)
   
for registry in registries:
   ind_schema_path = os.path.join(schema_path,registry +".yaml")
   ind_ddl_path = os.path.join(ddl_path,registry + ".sql")

   format_errors = validate_schema_format(ind_schema_path)
   if not format_errors:
      ddl_errors = validate_schema_ddl(ind_ddl_path, ind_schema_path)
   else:
      for msg in format_errors:
         logger.error("Schema: %s | %s", registry, msg)
      
      print("Correct Format for Schema before passing it to validate against DDL")

   if ddl_errors:
      for msg in ddl_errors:
         logger.error("Schema: %s | %s", registry, msg)
