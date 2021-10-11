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


def __dummy():
    return "dummy"


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


def powerline_builder(last_segment, powerline_symbol, text, fg=None, bg=None, prefix="", postfix="") -> str:
    include_style = bg or fg
    full_string = "<style " if include_style else ""

    if text == "":
        return ""

    last_fg = last_segment.get(
        "foreground", "") if last_segment != None else ""

    if include_style:
        if fg:
            full_string += f"fg={_b}{bg}{_b} "
        if last_fg:
            full_string += f"bg={_b}{last_fg}{_b} "
        full_string += f">{powerline_symbol}</style>"
    else:
        full_string += f"{powerline_symbol}"

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

            for segment in segments:
                text_inside = ""
                skip = False

                properties = segment.get("properties", {})

                leading_diamond = segment.get("leading_diamond", "")
                trailing_diamond = segment.get("trailing_diamond", "")
                powerline_symbol = segment.get("powerline_symbol", "")
                fg = segment.get("foreground", "")
                bg = segment.get("background", "")
                prefix = properties.get("prefix", "")
                postfix = properties.get("postfix", "")
                text = properties.get("text", "")

                # Color exceptions
                disabled_colors = ["transparent"]

                if bg in disabled_colors:
                    bg = ""
                if fg in disabled_colors:
                    fg = ""

                text_inside, skip = segment_handler.handle_segment(
                    segment)

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
                    final_prompt += powerline_builder(
                        last_segment, powerline_symbol, text_inside, fg, bg, prefix, postfix)

                last_segment = segment
                full.append(text_inside)

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
