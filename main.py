import yaml
from validator.schema_validator import SchemaValidator

def main():
    file_path = "./assets/schema/infra_asset_details.yml"
    
    validator = SchemaValidator()
    with open(file_path,"r") as f:
        schema = yaml.safe_load(f)
    
    validator.validate(schema)
    
    
if __name__ == "__main__":
    main()
    