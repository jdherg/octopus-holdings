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
            emoji = emoji_resolver.random_emoji()
        emojistack[i] = emoji_resolver.resolve(emoji, desired_set)
    return render_template('index.html', stack=emojistack)


@app.route('/emoji/<path:filepath>')
def emoji_src(filepath):
    if emoji_resolver.resolve_to_internal_path(filepath):
        path, base = emoji_resolver.resolve_to_internal_path(filepath)
        return send_from_directory(path, base)
    abort(404)

if __name__ == '__main__':
    app.debug = True
    app.run()
