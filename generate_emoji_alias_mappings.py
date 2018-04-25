import json
import os
import re
import sys

NOTO_SVG_FILENAME = re.compile('(?<=emoji_)u.+(?=\.svg)')


def main():
    emoji_svg_folder = sys.argv[1]
    emoji_metadata_filename = sys.argv[2]
    output_filename = sys.argv[3]

    with open(emoji_metadata_filename, 'r') as emoji_metadata_file:
        emoji_metadata = json.load(emoji_metadata_file)
        emoji_metadata = {entry["emoji"]: entry
                          for entry in emoji_metadata
                          if "emoji" in entry}
    svg_filenames = os.listdir(emoji_svg_folder)
    emoji_to_alias_mappings = {}
    for svg_filename in svg_filenames:
        aliases = []
        if NOTO_SVG_FILENAME.search(svg_filename):
            svg_codepoint = NOTO_SVG_FILENAME.search(svg_filename).group()
            emoji = "".join([chr(int(char, 16)) for char in svg_codepoint[1:].split('_')])
            aliases.append(emoji)
            aliases.append(svg_codepoint)
            aliases.append(svg_codepoint[1:])
            if emoji in emoji_metadata:
                aliases.extend(emoji_metadata[emoji]["aliases"])
            # Noto filenames don't include the variation selector-16 (\ufe0f)
            # but gemoji does. The first miss may be because of that.
            elif emoji + "\ufe0f" in emoji_metadata:
                aliases.extend(emoji_metadata[emoji + "\ufe0f"]["aliases"])
            emoji_to_alias_mappings[svg_codepoint] = aliases
    with open(output_filename, 'w') as output_file:
        json.dump(emoji_to_alias_mappings, output_file,
                  ensure_ascii=False, indent=1, sort_keys=True)

if __name__ == '__main__':
    main()
