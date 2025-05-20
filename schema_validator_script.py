from pyvalidator.format_validator import validate_schema_format
from pyvalidator.schema_validator import main as validate_schema_ddl


ddl_path = "./assets/DDL/infra_asset_details.sql"
schema_path = "./assets/schema/movies.yml"

format_errors = validate_schema_format(schema_path)
if not format_errors:
   ddl_errors = validate_schema_ddl(ddl_path, schema_path)
else:
    print("Correct Format for Schema before passing it to validate against DDL")
