import json


def load_conductor_definitions(data_dir):
    definitions = {}

    # Load conductor definitions - disallow duplicated primary names
    for filename in data_dir.glob("*.json"):
        # Load definition from JSON
        try:
            with open(filename, 'r') as fp:
                definition = json.load(fp)
        except Exception as e:
            raise RuntimeError(f"Failed to load conductor definition from '{filename}': {e}!")

        name = definition["name"]
        if name in definitions:
            raise ValueError(f"Duplicated conductor identifier: {name}!")

        definitions[name] = definition

    # Go over loaded definitions and create copies for aliases.
    # Iterate over a shallow copy, because we are adding to the dict
    for definition in list(definitions.values()):
        for name in definition.get("aliases", []):
            if name in definitions:
                raise ValueError(f"Duplicated conductor alias: {name}!")
            definitions[name] = definition

    return definitions
