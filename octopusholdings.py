import json
import random
from flask import abort, Flask, render_template, send_from_directory

app = Flask(__name__)

def load_asset_folder_whitelist(filename, folder_whitelist):
    with open(filename, 'r') as f:
        emoji_sets = json.load(f)
        for emoji_set in emoji_sets:
            folder_whitelist.add(emoji_set["rel_path"])

def load_emoji_aliases(filename, emoji_aliases, folder):
    with open(filename, 'r') as f:
        emoji_dict = json.load(f)
        for emoji in emoji_dict.keys():
            emoji_path = folder + "/" + "emoji_" + emoji + ".svg"
            for alias in emoji_dict[emoji]:
                emoji_aliases[alias] = emoji_path

emoji_aliases = dict()
load_emoji_aliases('emoji_map.json', emoji_aliases, "noto")
load_emoji_aliases('custom_emoji_map.json', emoji_aliases, "custom")

folder_whitelist = set()
load_asset_folder_whitelist('emoji_set_metadata.json', folder_whitelist)

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
    path, base = filepath.rsplit('/', 1)
    if path in folder_whitelist:
        return send_from_directory('emoji/' + path, base)
    else:
        abort(404)


if __name__ == '__main__':
    app.debug = True
    app.run()
