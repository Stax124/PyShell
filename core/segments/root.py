import ctypes
import os


def isadmin() -> bool:
    """Ask if run with elevated privileges

    Returns:
        bool: Has admin privelage
    """

    try:
        _is_admin = os.getuid() == 0

    except AttributeError:
        _is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return _is_admin


def main(segment: dict):

    text = segment.get("properties", {}).get("root_icon", "")

    if isadmin():
        return text, False
    else:
        return "", True
