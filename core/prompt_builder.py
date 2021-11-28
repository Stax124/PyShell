import json
import os
import re

from prompt_toolkit import HTML
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.shortcuts.prompt import prompt
from prompt_toolkit.shortcuts.utils import print_formatted_text
from prompt_toolkit.styles import Style

import promptvar
import segment_handler
import constants

_b = "\""
next_text = ""


def __dummy():
    return "dummy"


def next_usable(usable_list: list, start_index: int = 0) -> int:

    current_index = 1

    for usable in usable_list[start_index+1:]:

        if not usable[1]:
            return start_index+current_index
        else:
            current_index += 1


def plain_builder(fg, bg, text, prefix="", postfix="") -> str:
    # Generate html string with style if bg or fg is set independently

    prefix = handle_hex_colors(prefix)
    postfix = handle_hex_colors(postfix)

    include_style = bg or fg
    full_string = "<style " if include_style else ""

    if include_style:
        if bg:
            full_string += f"bg={_b}{bg}{_b} "
        if fg:
            full_string += f"fg={_b}{fg}{_b} "
        full_string += f">{prefix}{text}{postfix}</style>"
    else:
        full_string += f"{prefix}{text}{postfix}"

    return full_string


def diamond_builder(text, leading_diamond, trailing_diamond, fg=None, bg=None, prefix="", postfix="") -> str:

    leading_diamond = handle_hex_colors(leading_diamond)
    trailing_diamond = handle_hex_colors(trailing_diamond)

    # Generate html string with style if bg or fg is set independently
    include_style = bg or fg
    full_string = "<style " if include_style else ""

    if include_style:
        if fg:
            full_string += f"fg={_b}{bg}{_b} "
        full_string += f">{leading_diamond}</style>"
    else:
        full_string += f"{leading_diamond}"

    if include_style:
        full_string += f"<style "

        if bg:
            full_string += f"bg={_b}{bg}{_b} "
        if fg:
            full_string += f"fg={_b}{fg}{_b} "
        full_string += f">{prefix}{text}{postfix}</style>"
    else:
        full_string += f"{prefix}{text}{postfix}"

    if include_style:
        full_string += "<style "

        if fg:
            full_string += f"fg={_b}{bg}{_b} "
        full_string += f">{trailing_diamond}</style>"
    else:
        full_string += f"{trailing_diamond}"

    return full_string


def powerline_builder(last_segment, next_segment, powerline_symbol, text, fg=None, bg=None, prefix="", postfix="") -> str:

    prefix = handle_hex_colors(prefix)
    postfix = handle_hex_colors(postfix)

    if next_segment != None:
        if next_segment.get("background", ""):
            next_background = next_segment.get("background")
        else:
            next_background = None
    else:
        next_background = None

    include_style = bg or fg
    full_string = "<style " if include_style else ""

    if last_segment != None:
        full_string = ""

    if text == "":
        return ""

    if last_segment == None:
        if include_style:
            full_string += f"bg={_b}{bg}{_b} "
            full_string += f">{powerline_symbol}</style>"
        else:
            full_string += f"{powerline_symbol}"

    if include_style:
        full_string += f"<style "

        if bg:
            full_string += f"bg={_b}{bg}{_b} "
        if fg:
            full_string += f"fg={_b}{fg}{_b} "
        full_string += f"> {prefix}{text}{postfix} </style>"
    else:
        full_string += f" {prefix}{text}{postfix} "

    if include_style:
        full_string += "<style "

        if fg:
            full_string += f"fg={_b}{bg}{_b} "
        if next_background:
            full_string += f"bg={_b}{next_background}{_b} "
        full_string += f">{powerline_symbol}</style>"
    else:
        full_string += f"{powerline_symbol}"

    return full_string


def build_old(str):
    iprompt = ""

    pattern = re.compile(r"\$\{[^}]*\}")
    found = (re.findall(pattern, iprompt))

    for item in found:
        ipatternt = re.compile(r"[^$^{].+[^}]")
        ifound = re.findall(ipatternt, item)[0]

        found = promptvar.vars[ifound]
        if type(found) == type(__dummy) or type(found) == type(os.getcwd):
            found = found()

        iprompt = iprompt.replace(item, str(found))


# change string from '<#hexvalue>text</> to <style fg="hexvalue">text</style>'
def handle_hex_colors(text):
    if text == "":
        return ""

    # (<#[0-9a-fA-F]{6}>)
    # (<#[0-9a-fA-F]{6}>)|(<[a-zA-Z]*>)|(<#[0-9a-fA-F]{6},[a-zA-Z]*>)|(<[a-zA-Z]*,#[0-9a-fA-F]{6}>)
    pattern = re.compile(
        r"(<#[0-9a-fA-F]{6}>)|(<[a-zA-Z]*>)|(<#[0-9a-fA-F]{6},[a-zA-Z]*>)|(<[a-zA-Z]*,#[0-9a-fA-F]{6}>)|(<[a-zA-Z]*,[a-zA-Z]*>)")
    found = re.findall(pattern, text)

    found = [i for i in list(found[0]) if i != ''] if found else []

    print(found) if found else ""

    for item in found:
        _item = item
        item = item.replace("<", "").replace(">", "").split(",")
        if len(item) == 2:
            fg = item[0]
            bg = item[1]
        elif len(item) == 1:
            fg = item[0]
            bg = None
        else:
            # Print error with red color
            print("[31mError: Invalid color format[0m", item)

        if fg.strip() in constants.disabled_colors:
            fg = None
        if bg:
            if bg.strip() in constants.disabled_colors:
                bg = None
                
        print(item, _item, (fg, bg))

        first = f"fg={_b}{fg}{_b}" if fg else ""
        second = f"bg={_b}{bg}{_b}" if bg else ""

        text = text.replace(_item, f"<style {first} {second}>")
        text = text.replace(f"</>", "</style>")

    return text


def build(d: dict):

    # TODO: Change segments to a list of segments instead of building the string

    final_prompt = ""

    spacing = d.get("spacing", 1)
    blocks = d["blocks"]

    full = []

    for block in blocks:
        if block["type"] == "prompt" and block["alignment"] == "left":

            if block.get("newline", False):
                final_prompt += "\n"

            segments = block["segments"]

            last_segment = None

            segment_text_list = []

            for segment in segments:
                text_inside, skip = segment_handler.handle_segment(
                    segment)

                segment_text_list.append((text_inside, skip))

            index = 0

            for segment in segments:

                text_inside = segment_text_list[index][0]

                if segment_text_list[index][1]:
                    index += 1
                    continue

                properties = segment.get("properties", {})

                leading_diamond = segment.get("leading_diamond", "")
                trailing_diamond = segment.get("trailing_diamond", "")
                powerline_symbol = segment.get("powerline_symbol", "")
                fg = segment.get("foreground", "")
                bg = segment.get("background", "")
                prefix = properties.get("prefix", "")
                postfix = properties.get("postfix", "")

                # Handle named colors that are not present in the prompt-toolkit library
                if fg in constants.colors:
                    fg = constants.colors[fg]
                if bg in constants.colors:
                    bg = constants.colors[bg]

                leading_diamond = handle_hex_colors(leading_diamond)
                trailing_diamond = handle_hex_colors(trailing_diamond)
                prefix = handle_hex_colors(prefix)
                postfix = handle_hex_colors(postfix)

                # Color exceptions
                if bg in constants.disabled_colors:
                    bg = ""
                if fg in constants.disabled_colors:
                    fg = ""

                # Get next usable segment
                _next = next_usable(segment_text_list, index)

                # Add spacing if needed
                # TODO fix spacing - it's not working
                postfix += " "*spacing if _next != None and final_prompt != "" else ""

                text_inside = handle_hex_colors(text_inside)

                if segment["style"] == "plain":
                    final_prompt += plain_builder(fg=fg, bg=bg,
                                                  text=text_inside, prefix=prefix, postfix=postfix)
                if segment["style"] == "diamond":
                    final_prompt += diamond_builder(
                        text_inside, leading_diamond, trailing_diamond, fg, bg, prefix, postfix)

                if segment["style"] == "powerline":
                    final_prompt += powerline_builder(
                        last_segment, segments[_next] if _next != None else None, powerline_symbol, text_inside, fg, bg, prefix, postfix)

                last_segment = segment
                index += 1
                full.append(text_inside)

    print(final_prompt)
    return HTML(final_prompt)


if __name__ == "__main__":
    for _, _, j in os.walk("themes"):
        themes = j

    themes.pop(themes.index("schema.json"))

    themes.sort()

    # themes = ["blue-owl.omp.json"]
    # themes = ["atomicBit.omp.json"]

    for item in themes:

        print(item)
        filename = open("themes/"+item, "r", encoding="utf-8")
        data = json.load(filename)

        print_formatted_text(build(data),
                             color_depth=ColorDepth.TRUE_COLOR)
