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

    last_fg = last_segment.get(
        "foreground", "") if last_segment != None else ""

    if last_segment == None:
        if include_style:
            if last_fg:
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


def build(d: dict):
    final_prompt = ""

    spacing = d.get("spacing", 1)
    blocks = d["blocks"]

    full = []

    for block in blocks:
        if block["type"] == "prompt" and block["alignment"] == "left":

            segments = block["segments"]

            last_segment = None
            current_segment = 0

            segment_text_list = []

            for segment in segments:
                text_inside, skip = segment_handler.handle_segment(
                    segment)

                segment_text_list.append((text_inside, skip))

            index = 0

            for segment in segments:

                text_inside = segment_text_list[index][0]
                skip = False

                properties = segment.get("properties", {})

                leading_diamond = segment.get("leading_diamond", "")
                trailing_diamond = segment.get("trailing_diamond", "")
                powerline_symbol = segment.get("powerline_symbol", "")
                fg = segment.get("foreground", "")
                bg = segment.get("background", "")
                prefix = properties.get("prefix", "")
                postfix = properties.get("postfix", "")

                # Color exceptions
                disabled_colors = ["transparent"]

                if bg in disabled_colors:
                    bg = ""
                if fg in disabled_colors:
                    fg = ""

                # Add spacing if needed
                final_prompt += f'{"" if final_prompt.__len__() > 0 else " "*spacing}'

                if segment["style"] == "plain":
                    final_prompt += plain_builder(fg=fg, bg=bg,
                                                  text=text_inside, prefix=prefix, postfix=postfix)
                if segment["style"] == "diamond":
                    if not skip:
                        final_prompt += diamond_builder(
                            text_inside, leading_diamond, trailing_diamond, fg, bg, prefix, postfix)

                if segment["style"] == "powerline":
                    _next = next_usable(segment_text_list, index)

                    final_prompt += powerline_builder(
                        last_segment, segments[_next] if _next != None else None, powerline_symbol, text_inside, fg, bg, prefix, postfix)

                last_segment = segment
                current_segment += 1
                index += 1
                full.append(text_inside)

    # print(final_prompt)

    return HTML(final_prompt)


if __name__ == "__main__":
    themes = ["agnoster.omp.json"]

    # for _,_,j in os.walk("themes"):
    #     themes = j

    for item in themes:

        print(item)
        filename = open("themes/"+item, "r")
        data = json.load(filename)

        print_formatted_text(build(data),
                             color_depth=ColorDepth.TRUE_COLOR)
