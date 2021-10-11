import ctypes
import datetime
import getpass
import os
import platform

from pygit2 import Repository


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


def getcurrentrepo():
    """Get branch of git repository in current folder

    Returns:
        str: branch of git repository
    """

    try:
        return Repository(r'.').head.shorthand
    except:
        return ""


def timenow():
    """Get current time

    Returns:
        str: `Hour:Minute:Second`
    """

    return datetime.datetime.now().strftime(r"%H:%M:%S")


try:
    USER = getpass.getuser()
except:
    USER = "UNKNOWN"

try:
    DOMAIN = platform.node()
except:
    DOMAIN = "UNKNOWN"

variables = {
    "RETURNCODE": 0,
    "DOMAIN": DOMAIN,
    "USER": USER,
    "PATH": os.getcwd,
    "ROOT": "#" if isadmin == True else "$",
    "REPO": getcurrentrepo,
    "TIME": timenow,
    "SYSTEM": platform.system,
    "WIN32EDITION": platform.win32_edition,
    "WIN32VER": platform.win32_ver,
    "MACOSVER": platform.mac_ver,
    "MACHINETYPE": platform.machine,
    "PLATFORM": platform.platform,
    "CPUCOUNT": os.cpu_count,
    "LOGIN": os.getlogin,
    "PID": os.getpid
}
