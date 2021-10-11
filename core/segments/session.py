import getpass
import platform


def main(segment: dict):
    text = ""

    properties = segment.get('properties', {})

    user_info_separator = properties.get('user_info_separator', '@')
    display_user = properties.get('display_user', True)
    display_host = properties.get('display_host', True)

    try:
        USER = getpass.getuser()
    except:
        USER = "UNKNOWN"

    try:
        DOMAIN = platform.node()
    except:
        DOMAIN = "UNKNOWN"

    if display_user and display_host:
        text = "{}{}{}".format(USER, user_info_separator, DOMAIN)
    elif display_user:
        text = USER
    elif display_host:
        text = DOMAIN
    else:
        text = ""
        return text, True

    return text, False
