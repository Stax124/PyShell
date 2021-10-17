import platform


def main(segment: dict):
    properties = segment.get('properties', {})
    macos = segment.get('macos', "")
    windows = segment.get('windows', "")
    linux = segment.get('linux', "")

    if platform.system() == "Darwin":
        return macos, False
    elif platform.system() == "Windows":
        return windows, False
    elif platform.system() == "Linux":
        return linux, False
    else:
        return "", True
