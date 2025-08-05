import json

def dict_to_obj(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, str):
            try:
                parsed_value = json.loads(value)
                if isinstance(parsed_value, dict):
                    dictionary[key] = dict_to_obj(parsed_value)
            except json.JSONDecodeError:
                pass
        elif isinstance(value, dict):
            dictionary[key] = dict_to_obj(value)
    return SimpleNamespace(**dictionary)