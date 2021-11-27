import os


def main(segment: dict):

    prop = segment.get("properties")
    home_icon = prop.get("home_icon", "~")
    folder_icon = prop.get("folder_icon", "folder")
    style = prop.get("style", "folder")

    if style == "folder":
        text = os.path.dirname(os.getcwd())
    else:
        text = os.getcwd()

    return text, False
