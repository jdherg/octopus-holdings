import json
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

with open('emoji_map.json', 'r') as f:
    emoji_dict = json.load(f)
    emoji_aliases = dict()
    for emoji in emoji_dict.keys():
        for alias in emoji_dict[emoji]:
            emoji_aliases[alias] = emoji


@app.route('/')
@app.route('/<emojicode>')
def show_emoji(emojicode="u1f3c6"):
    print(emojicode, len(emojicode))
    emojicode = emoji_aliases.get(emojicode, "u1f3c6")
    return render_template('index.html', code=emojicode)


@app.route('/emoji/<filename>')
def emoji_src(filename):
    return send_from_directory('emoji', filename)

if __name__ == '__main__':
    app.debug = True
    app.run()
