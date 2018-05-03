import json
import random
from flask import abort, Flask, render_template, send_from_directory
import emoji_resolver

app = Flask(__name__)

@app.route('/')
@app.route('/<path:emojicode>')
def show_emoji(emojicode='tada'):
    emojistack = emojicode.split('/')
    desired_set = None
    if emoji_resolver.is_emoji_set(emojistack[0]):
        desired_set = emojistack.pop(0)
        if not emojistack:
            emojistack.append("tada")
    if len(emojistack) == 1:
        emojistack.append('octopus')
    for i, emoji in enumerate(emojistack):
        if emoji == 'random':
            emoji = random.choice(list(emoji_aliases.keys()))
        emojistack[i] = emoji_resolver.resolve(emoji, desired_set)
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
