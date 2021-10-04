from functions import functions
import os
import sys
import json
import platform
import argparse
import threading
import subprocess


def _config(shell, *querry):
    if querry == ():
        print(json.dumps(shell.config.config, indent=4))


def _plugins(shell, *querry):
    for plugin in shell.manager.getAllPlugins():
        print(plugin.name)


def _platform(shell, *querry):
    print(platform.system())


def _executable(shell, *querry):
    print(sys.executable)


def _whoami(shell, *querry):
    try:
        if platform.system() == "Windows":
            USER = os.environ["USERNAME"]
        else:
            USER = os.environ["USER"]
    except:
        USER = "UNKNOWN"

    print(USER)


def _domain(shell, *querry):
    try:
        if platform.system() == "Windows":
            USERDOMAIN = os.environ["USERDOMAIN"]
        else:
            USERDOMAIN = os.environ["NAME"]
    except:
        USERDOMAIN = "UNKNOWN"

    print(USERDOMAIN)


def _pwd(shell, *querry):
    print(os.getcwd())


def _read(shell, *querry):
    fparser = argparse.ArgumentParser(prog="read")
    fparser.add_argument("filename", help="Target filename")
    fparser.add_argument("-n", dest="number",
                         help="Number of lines", default=-1, type=int)
    try:
        fargs = fparser.parse_args(querry)
    except SystemExit:
        return

    file = open(fargs.filename, encoding="utf-8")
    if fargs.number == -1:
        print(file.read())
    else:
        for i in range(fargs.number):
            content = file.readline(i)
            print(content)
    file.close()


def _clear(shell, *querry):
    if platform.system() == "Windows":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)


def _theads(shell, *querry):
    print(
        f"Active threads: {threading.activeCount()}\n")
    for t in threading.enumerate():
        print("{:<30} {:<30}".format(
            t.name, "active" if t.is_alive() else "stopped"))
    return


def _exit(shell, *querry):
    sys.exit(0)


def _cd(shell, *querry, command=True):
    try:
        os.chdir(os.path.expanduser(" ".join(querry)))
    except OSError:
        if command:
            print("Path does not exist")
        else:
            raise OSError


functions["config"] = _config
functions["cd"] = _cd
functions["platform"] = _platform
functions["executable"] = _executable
functions["whoami"] = _whoami
functions["domain"] = _domain
functions["pwd"] = _pwd
functions["read"] = _read
functions["clear"] = _clear
functions["cls"] = _clear
functions["threads"] = _theads
functions["exit"] = _exit
functions["plugins"] = _plugins
