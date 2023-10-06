#!/usr/bin/env python3
import argparse

from convert_emf_images import read_emf_images, convert_emf_to_png
from remove_pattern_from_adoc import remove_text_matching_regex
from fix_angular_brackets import escape_double_angular_brackets
from recolor_notes import recolor_notes
from fix_the_biblio import add_anchor_to_biblio, add_link_to_biblio
from fix_image_captions_in_adoc import use_block_tag_for_img_and_move_caption_ahead
from fixquotesonkeywords import replace_quotes_on_keyword
from fix_square_bracket import escape_square_brackets
import util.helper_func as utils
import logging

logging.basicConfig(filename='my_log_file.log',level=logging.INFO)


def fix_asciidoc(input_file, output_file):
    directory = "../AASiD_1_Metamodel"

    logging.info("Read the initial asciidoc file...")
    with open(input_file, 'r', encoding="utf-8") as file:
        content = file.read()

    logging.info("Convert the emf images in Asciidoc document to png")
    images_to_convert = read_emf_images(directory + "/media")
    for image_name, image_path in images_to_convert:
        try:
            logging.info(f"Convert the emf image: {image_name}")
            convert_emf_to_png(image_path, image_path.replace(".emf", ".png"))
            # 2.2 Replace all occurrences of emf to png in asciidoc file
            content = content.replace(image_name, image_name.replace(".emf", ".png"))
        except Exception:
            logging.error(f"Could not convert the emf image: {image_name}")

    logging.info(f"Remove certain commonly occurring patterns in asciidoc file - check the script for list of patterns")
    content = remove_text_matching_regex(content)

    logging.info(f"Fix double angular brackets")
    content = escape_double_angular_brackets(content)

    logging.info(f"Style note boxes")
    content = recolor_notes(content)

    logging.info(f"Add anchors to bibliography")
    keys, content = add_anchor_to_biblio(content)

    logging.info(f"Connect the in-document references to bibliography")
    content = add_link_to_biblio(content, keys)

    logging.info(f"Fix image captions")
    content = use_block_tag_for_img_and_move_caption_ahead(content)

    logging.info(f"Fix the Quotes on keyword")
    content = replace_quotes_on_keyword(content)

    logging.info(f"Fix square brackets")
    content = escape_square_brackets(content)

    logging.info(f"Write fixed content to the output file: {output_file}")
    utils.write_file(output_file, content)


def main() -> None:
    """Execute the main routine."""
    parser = argparse.ArgumentParser("Reads an initial generated AsciiDoc file from Word, fixes some issues and writes a new fixed AsciiDoc file")
    parser.add_argument("-i", "--adoc_input", help="path to the initial generated AsciiDoc file", required=True)
    parser.add_argument("-o", "--adoc_output", help="path to the output file", required=True)
    parser.add_argument("-f", "--force", help="overwrite existing files", action="store_true")
    args = parser.parse_args()

    adoc_input = args.adoc_input
    adoc_output = args.adoc_output
    force = bool(args.force)

    if not adoc_input.exists():
        raise FileNotFoundError("Adoc file does not exist: {}".format(adoc_input))

    adoc_output.parent.mkdir(exist_ok=True, parents=True)

    if not force and adoc_output.exists():
        raise FileExistsError("Output path already exists and --force was not specified: {}".format(adoc_output))

    fix_asciidoc(adoc_input, adoc_output)

if __name__ == '__main__':
    main()
