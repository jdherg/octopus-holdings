import json
import random
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

with open('emoji_map.json', 'r') as f:
    emoji_dict = json.load(f)
    emoji_aliases = dict()
    for emoji in emoji_dict.keys():
        for alias in emoji_dict[emoji]:
            emoji_aliases[alias] = emoji


@app.route('/')
@app.route('/<path:emojicode>')
def show_emoji(emojicode='trophy'):
    if emojicode == 'random':
        emojicode = random.choice(list(emoji_aliases.keys()))
    emojicode=emojicode.replace(" ", "null")
    emojistack = [x.split('/') for x in emojicode.split('.')]
    print(emojistack)
    encodedemojistack = [[]]
    if (len(emojistack) == 1 and len(emojistack[0]) == 1):
        emojistack[0].append('octopus')
    maxlength = max([len(item) for item in emojistack])
    for i, sublist in enumerate(emojistack):
        encodedemojistack.append([])
        for j, emoji in enumerate(sublist):
            if emoji == 'random':
                emoji_ref = emoji_aliases.get(random.choice(list(emoji_aliases.keys())), 'u1f3c6')
            else:
                emoji_ref = emoji_aliases.get(emoji, 'u1f3c6')
            encodedemojistack[i].append(emoji_ref)
    return render_template('index.html', stack=encodedemojistack, longest=maxlength)


@app.route('/emoji/<filename>')
def emoji_src(filename):
    return send_from_directory('emoji', filename)


if __name__ == '__main__':
    app.debug = True
    app.run()
