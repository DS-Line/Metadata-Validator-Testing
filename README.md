# Go inside the Inteliome-Metadata-Validator
- cd Inteliome-Metadata-Validator
- python -m venv venv
- activate venv and install requirements.txt

# Run the Schema and Semantics Validator using the cmd below:
- python3 pyvalidator/test/schema_validator.py
- python3 pyvalidator/test/semantic_validator.py


- Configure Metadata Path for each script.
- Your file structure should look like this:
        metadata/
    ├── ddl/
    ├── schema/
    ├── semantics/
    └── registry.yml
