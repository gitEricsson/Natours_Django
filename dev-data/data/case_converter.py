import json
import re

def camel_to_snake(name):
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', name).lower()

def convert_keys(obj):
    if isinstance(obj, list):
        return [convert_keys(item) for item in obj]
    elif isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = camel_to_snake(key)
            if new_key == "_id":
                new_key = "id"
            new_dict[new_key] = convert_keys(value)
        return new_dict
    else:
        return obj

def main():
    # Read the input JSON file
    with open('users.json', 'r') as file:
        data = json.load(file)

    # Convert the keys
    converted_data = convert_keys(data)

    # Write the converted data to a new JSON file
    with open('users_py.json', 'w') as file:
        json.dump(converted_data, file, indent=2)

if __name__ == "__main__":
    main()