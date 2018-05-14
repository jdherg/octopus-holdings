import os
from flask import abort, Flask, render_template, send_from_directory
import emoji_resolver

app = Flask(__name__)
OCTOPUS_HOLDINGS_ENV=os.environ.get("OCTOPUS_HOLDINGS_ENV")

@app.route('/')
@app.route('/<path:emojicode>')
def show_emoji(emojicode='tada'):
    in_stack = emojicode.split('/')
    current_desired_set = None
    processed_stack = list()
    # Process commands. (Just desired emoji set for now.)
    for token in in_stack:
        if emoji_resolver.is_emoji_set(token):
            current_desired_set = token
        else:
            if token == 'random':
                token = emoji_resolver.random_emoji()
            processed_stack.append((token, current_desired_set))
    # Fill in defaults.
    if not processed_stack:
        processed_stack.append(("tada", current_desired_set))
    if len(processed_stack) == 1:
        processed_stack.append(("octopus", current_desired_set))
    # Turn it into paths.
    emojistack = [emoji_resolver.resolve(alias, desired_set)
                  for alias, desired_set in processed_stack]
    return render_template('index.html', stack=emojistack,
                           env=OCTOPUS_HOLDINGS_ENV)

@app.route('/emoji/<path:filepath>')
def emoji_src(filepath):
    if emoji_resolver.resolve_to_internal_path(filepath):
        path, base = emoji_resolver.resolve_to_internal_path(filepath)
        return send_from_directory(path, base)
    abort(404)

if __name__ == '__main__':
    if not OCTOPUS_HOLDINGS_ENV:
        OCTOPUS_HOLDINGS_ENV="LOCAL"
    app.debug = True
    app.run()
