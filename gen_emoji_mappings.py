import json
import os
import re
import sys

noto = re.compile('(?<=emoji_)u.+(?=\.svg)')


def main():
    emoji_folder = sys.argv[1]
    shortcode_file = sys.argv[2]
    out_file = sys.argv[3]

    with open(shortcode_file, 'r') as f:
        shortcodes = json.load(f)
        shortcodes = {d["emoji"]: d for d in shortcodes if "emoji" in d}
    in_files = os.listdir(emoji_folder)
    in_cps = []
    for fname in in_files:
        si = noto.search(fname)
        if si:
            in_cps.append(si.group())
    in_emoji = []
    for cp in in_cps:
        cp = cp[1:].split('_')
        in_emoji.append("".join([chr(int(char, 16)) for char in cp]))
    # in_emoji = [chr(int(cp[1:], 16)) for cp in in_cps]
    mappings = {}
    for fname in in_files:
        vals = []
        if noto.search(fname):
                in_cps = noto.search(fname).group()
        emoji = "".join([chr(int(char, 16)) for char in in_cps[1:].split('_')])
        vals.append(emoji)
        vals.append(in_cps)
        vals.append(in_cps[1:])
        if emoji in shortcodes:
            vals.extend(shortcodes[emoji]["aliases"])
        mappings[in_cps] = vals
    with open(out_file, 'w') as f:
        json.dump(mappings, f, ensure_ascii=False, indent=1, sort_keys=True)

if __name__ == '__main__':
    main()
