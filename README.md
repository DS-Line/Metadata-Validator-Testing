# Go inside the Inteliome-Metadata-Validator
- cd Inteliome-Metadata-Validator
- python -m venv venv
- activate venv and install requirements.txt

# Run the Schema and Semantics Validator using the cmd below:
- python3 pyvalidator/test/schema_validator.py
- python3 pyvalidator/test/semantic_validator.py


- You will be asked to enter the relative path for both ddl and schema (in case of schema validation) 
- Or, schema and semantics for semantics validation

- Make sure to use relative path (For e.g. assets/schema/schema.yml)