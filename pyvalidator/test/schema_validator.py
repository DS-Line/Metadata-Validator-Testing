import os
import subprocess
import sys
from pathlib import Path

# Paths
FORMAT_VALIDATOR = "pyvalidator/format_validator_for_test.py"
# SCHEMA_VALIDATOR = "pyvalidator/schema_validator.py"

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, "..", ".."))  # go up two levels

sys.path.insert(0, repo_root)

from pyvalidator.schema_validator import main as schema_validator_main



def run_script(script, yaml_file):
    try:
        result = subprocess.run(
            ["python", script, yaml_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def print_header(title):
    print("=" * 70)
    print(title)
    print("=" * 70)
    

def resolve_path(input_path: str) -> str:
    if os.path.isabs(input_path):
        return input_path
    # Otherwise, resolve relative to current working directory
    return os.path.abspath(os.path.join(os.getcwd(), input_path))

def print_divider():
    print("-" * 70)

def main():
    print("📂 Enter relative paths like 'assets/ddl/movies.sql'")
    user_ddl = input("Enter path to DDL file (press Enter for default): ").strip()
    user_schema = input("Enter path to schema file (press Enter for default): ").strip()

    ddl_path = user_ddl or "assets/DDL/movies.sql"
    schema_path = user_schema or "assets/schema/movies.yml"

    ddl_path = resolve_path(ddl_path)
    schema_path = resolve_path(schema_path)
    yaml_file = Path(schema_path)

    if not yaml_file.exists():
        print(f"❌ File not found: {yaml_file}")
        return

    print_header(f"🧪 Validating: {yaml_file.name}")

    # Run format validator
    ret_format, out_format, err_format = run_script(FORMAT_VALIDATOR, str(yaml_file))
    if ret_format != 0:
        print("❌ Format Validation Failed:")
        print(err_format or out_format)
        return

    print("✅ Format Validation Passed")

    # Run schema validator
    schema_validator_main(ddl_path=ddl_path, schema_path=schema_path)

    print_divider()


if __name__ == "__main__":
    main()
