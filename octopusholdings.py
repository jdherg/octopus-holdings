import json
import random
from flask import abort, Flask, render_template, send_from_directory

app = Flask(__name__)

def load_emoji_set_metadata(filename, emoji_set_paths):
    with open(filename, 'r') as f:
        emoji_set_metadata = json.load(f)
    for metadata in emoji_set_metadata.values():
        emoji_set_paths[metadata["external_path"]] = metadata["internal_path"]

def load_emoji_aliases(filename, emoji_aliases, folder):
    with open(filename, 'r') as f:
        emoji_dict = json.load(f)
    for emoji in emoji_dict.keys():
        emoji_path = "emoji_" + emoji + ".svg"
        if len(folder):
            emoji_path = folder + "/" + emoji_path
        for alias in emoji_dict[emoji]:
            emoji_aliases[alias] = emoji_path

emoji_set_paths = dict()
load_emoji_set_metadata('emoji_set_metadata.json', emoji_set_paths)

emoji_aliases = dict()
load_emoji_aliases('emoji_map.json', emoji_aliases, "noto_1")
load_emoji_aliases('custom_emoji_map.json', emoji_aliases, "")

@app.route('/')
@app.route('/<path:emojicode>')
def show_emoji(emojicode='tada'):
    emojistack = emojicode.split('/')
    if len(emojistack) == 1:
        emojistack.append('octopus')
    for i, emoji in enumerate(emojistack):
        if emoji == 'random':
            emoji = random.choice(list(emoji_aliases.keys()))
        emojistack[i] = emoji_aliases.get(emoji, 'noto/emoji_u2753.svg')
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
