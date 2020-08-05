import json
import argparse
import python_jsonschema_objects as pjo


def update_dictionary(schema_obj):

    # Updating header:
    if "$schema" in schema_obj: 
        schema_obj["$schema"] = "http://json-schema.org/draft-04/schema#"

    # Looping through all keys and check if exclusive minimum exists:
    if 'exclusiveMinimum' in schema_obj:
        schema_obj['minimum'] = schema_obj['exclusiveMinimum']
        schema_obj['exclusiveMinimum'] = True

    if 'exclusiveMaximum' in schema_obj:
        schema_obj['maximum'] = schema_obj['exclusiveMaximum']
        schema_obj['exclusiveMaximum'] = True
        
    # For some reasing type objects are not properly defined:
    if ('type' in schema_obj) and isinstance(schema_obj['type'], dict):
        schema_obj['type']['type'] = 'string'
        
    # Looping through all keys recursively call function for all dictionaries:
    for key, value in schema_obj.items():   
        # If a value is a dictinorary:
        if isinstance(value, dict):
            schema_obj[key] = update_dictionary(value)
            
        # If a value is an array:
        obj_list = []
        if isinstance(value, list):
            for val in value:
                if isinstance(val, dict):
                    val = update_dictionary(val)
                obj_list.append(val)
                
            schema_obj[key] = obj_list

    # Returning updated object:
    return schema_obj


def main():
    # Parsing arguments:
    parser = argparse.ArgumentParser(description='This script converts json schema written in draft7 to draft4.')
    parser.add_argument('-i', '--draft7File', help='Draft-7 compatible json schema filename', required=True, type=str)
    parser.add_argument('-o', '--draft4File', help='Draft-4 compatible json schema filename', required=True, type=str)

    args = parser.parse_args()
    draft7File = args.draft7File
    draft4File = args.draft4File

    # Reading input file:
    print(f'[Info] Loading ({draft7File}) schema file.')
    with open(draft7File, 'r', encoding="ascii") as f:
        draft7_schema = json.load(f)

    # Convert schema:
    print(f'[Info] Converting draft-7 schema.')
    draft4_schema = update_dictionary(draft7_schema)

    # Testing schema:
    print(f'[Info] Testing the draft-4 schema on schema builder.')

    try:
        builder = pjo.ObjectBuilder(draft4_schema)
    except:
        raise

    with open(draft4File, 'w', encoding='ascii') as f:
        json.dump(draft4_schema, f, indent=2, ensure_ascii=True)
    return 1
    # Testing schema:
    print(f'[Info] Draft-4 file ({draft4File}) saved.')

if __name__ == '__main__':
    main()