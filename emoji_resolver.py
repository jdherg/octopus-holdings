import json

def load_emoji_set_metadata(filename):
    emoji_set_priority = list()
    emoji_set_config = dict()
    emoji_set_paths = dict()
    with open(filename, 'r') as f:
        emoji_set_metadata = json.load(f)
    emoji_set_priority.extend(emoji_set_metadata["priority"])
    for emoji_set_name, config in emoji_set_metadata["config"].items():
        emoji_set_config[emoji_set_name] = config
        emoji_set_paths[config["external_path"]] = config["internal_path"]
    return emoji_set_priority, emoji_set_config, emoji_set_paths

def load_emoji_aliases(set_config):
    with open(set_config["alias_map"], 'r') as f:
        emoji_dict = json.load(f)
    set_aliases = dict()
    for emoji in emoji_dict.keys():
        emoji_path = set_config["prefix"] + emoji[1:] + ".svg"
        if set_config["external_path"]:
            emoji_path = set_config["external_path"] + "/" + emoji_path
        for alias in emoji_dict[emoji]:
            set_aliases[alias] = emoji_path
    return set_aliases

emoji_set_priority, emoji_set_config, emoji_set_paths = load_emoji_set_metadata(
    'emoji_set_metadata.json')

emoji_aliases = dict()
for emoji_set_name in reversed(emoji_set_priority):
    emoji_aliases[emoji_set_name] = load_emoji_aliases(
        emoji_set_config[emoji_set_name])

def is_emoji_set(candidate):
    return candidate in emoji_aliases.keys()

def resolve(alias, desired_set=None):
    if desired_set and is_emoji_set(desired_set):
        return emoji_aliases[desired_set].get(alias) or resolve(alias)
    for set_name in emoji_set_priority:
        if alias in emoji_aliases[set_name]:
            return emoji_aliases[set_name].get(alias)
    return resolve("question")
