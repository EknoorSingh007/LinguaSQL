import os, json
from jsonschema import validate, ValidationError

SCHEMA_DIR = os.path.join(os.getcwd(), "backend", "schema", "schemas")

def list_schemas():
    return [os.path.splitext(f)[0] for f in os.listdir(SCHEMA_DIR) if f.endswith(".json")]

def load_schema(collection):
    path = os.path.join(SCHEMA_DIR, f"{collection}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Schema file {path} does not exist")
    
    with open(path) as f:
        return json.load(f)

def save_schema(collection, schema):
    path = os.path.join(SCHEMA_DIR, f"{collection}.json")
    with open(path, "w") as f:
        json.dump(schema, f, indent=2)

def validate_document(collection, document):
    schema = load_schema(collection)
    validate(instance=document, schema=schema)