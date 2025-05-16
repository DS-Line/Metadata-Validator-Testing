from pyvalidator.format_validator import validate_schema_format
from pyvalidator.schema_validator import main as validate_schema_ddl


ddl_path = "./assets/DDL/movies.sql"
schema_path = "./assets/schema/movies.yml"

format_errors = validate_schema_format(schema_path)
ddl_errors = validate_schema_ddl(ddl_path, schema_path)

from pprint import pprint


# pprint(format_errors)
# pprint(ddl_errors)