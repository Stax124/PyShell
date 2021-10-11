from pygit2.repository import Repository


def getcurrentrepo():
    """Get branch of git repository in current folder

    Returns:
        str: branch of git repository
    """

    try:
        return Repository(r'.').head.shorthand
    except:
        return ""


def main(segment: dict):
    return (getcurrentrepo(), False) if getcurrentrepo() else ("", True)
