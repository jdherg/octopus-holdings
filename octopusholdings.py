import json
import random
from flask import abort, Flask, render_template, send_from_directory

app = Flask(__name__)

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

def resolve(alias):
    for set_name in emoji_set_priority:
        if alias in emoji_aliases[set_name]:
            return emoji_aliases[set_name].get(alias)
    return resolve("question")

@app.route('/')
@app.route('/<path:emojicode>')
def show_emoji(emojicode='tada'):
    emojistack = emojicode.split('/')
    if len(emojistack) == 1:
        emojistack.append('octopus')
    for i, emoji in enumerate(emojistack):
        if emoji == 'random':
            emoji = random.choice(list(emoji_aliases.keys()))
        emojistack[i] = resolve(emoji)
    return render_template('index.html', stack=emojistack)


@app.route('/emoji/<path:filepath>')
def emoji_src(filepath):
    if filepath.find('/') == -1:
        path, base = ("", filepath)
    else:
        path, base = filepath.rsplit('/', 1)
    if path in emoji_set_paths:
        return send_from_directory(emoji_set_paths[path], base)
    else:
        abort(404)


if __name__ == '__main__':
    app.debug = True
    app.run()
