# region Imports
from functions import functions
import shlex
import os
import sys
import argparse
import subprocess
import math
import traceback
import ctypes
import platform
import re
from io import StringIO
# endregion

# region Prompt-toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import ThreadedCompleter, NestedCompleter, merge_completers, ExecutableCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit import HTML
# endregion

# region Core
from core import config as cfg
from core import default, path_completer, env_completer, promptvar
# endregion

# region Plugins
from yapsy.PluginManager import PluginManager
manager = PluginManager()
manager.setPluginPlaces(["plugins"])
manager.collectPlugins()
for plugin in manager.getAllPlugins():
    plugin.plugin_object.main()
# endregion

# region Parser
parser = argparse.ArgumentParser()
parser.add_argument("command", help="Execute following command", nargs="*")
parser.add_argument("-d", "--directory", help="Start in specified directory")
parser.add_argument("-v", "--verbose", action="store_true")

if not sys.stdin.isatty():
    args = parser.parse_args(sys.stdin.readlines())
else:
    args = parser.parse_args()
# endregion

# region CONSTATNTS
try:
    if platform.system() == "Windows":
        USER = os.environ["USERNAME"]
    else:
        USER = os.environ["USER"]
except:
    USER = "UNKNOWN"

try:
    if platform.system() == "Windows":
        DOMAIN = os.environ["USERDOMAIN"]
    else:
        DOMAIN = os.environ["NAME"]
except:
    DOMAIN = "UNKNOWN"
# endregion

if platform.system() == "Windows":
    pathext = os.environ["PATHEXT"].split(os.pathsep)

    def filter(name):
        for item in pathext:
            if item.lower() in name:
                return True

        return False
else:
    def filter(name):
        return os.access(name, os.X_OK)


def run_command(command, stdin: str = ""):
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE, shell=True, universal_newlines=True, encoding="utf-8")
    process.stdin.write(stdin)
    msg = ""
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            msg += output
    return msg


def isadmin() -> bool:
    "Ask if run with elevated privileges"
    try:
        _is_admin = os.getuid() == 0

    except AttributeError:
        _is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return _is_admin


# region varinject
promptvar.vars.update(
    {
        "DOMAIN": DOMAIN,
        "USER": USER,
        "PATH": os.getcwd,
        "ROOT": "#" if isadmin == True else "$"
    }
)
# endregion


class Shell(PromptSession):
    def envirotize(self, string) -> str:
        "Applies Environment variables"
        import re

        def expandvars(string, default=None, skip_escaped=False):
            """Expand environment variables of form $var and ${var}.
            If parameter 'skip_escaped' is True, all escaped variable references
            (i.e. preceded by backslashes) are skipped.
            Unknown variables are set to 'default'. If 'default' is None,
            they are left unchanged.
            """
            def replace_var(m):
                return os.environ.get(m.group(2) or m.group(1), m.group(0) if default is None else default)
            reVar = (r'(?<!\\)' if skip_escaped else '') + \
                r'\$(\w+|\{([^}]*)\})'
            return re.sub(reVar, replace_var, string)

        values = self.config["aliases"].keys()
        if not "delalias" in string:
            for value in values:
                if string.find(value) != -1:
                    string = string.replace(
                        value, self.config["aliases"].get(value))

        splitInput = string.split()

        for i in splitInput:
            if i.find("%") != -1:
                spl = i.split("%")[1]
                env = os.environ[spl]
                splitInput[splitInput.index(i)] = splitInput[splitInput.index(
                    i)].replace(f"%{spl}%", env)

        rebuild = " ".join(splitInput)
        rebuild = expandvars(rebuild)

        if string != rebuild:
            string = rebuild

        return string

    def __init__(self, verbose=False):
        try:
            if args.directory:
                os.chdir(args.directory)
        except:
            pass

        self.config = cfg.Config(verbose=verbose, colored=True)
        self.config.load()
        self.config.fallback = {
            "aliases": {},
            "colored": True,
            "prompt": "┏━━(<user>${USER}</user> at <user>${DOMAIN}</user>)━[<path>${PATH}</path>]\n┗━<pointer>${ROOT}</pointer> ",
            "style": {
                # Default style
                "": "greenyellow",

                # Specific style
                "pointer": "#ff4500",
                "path": "aqua",
                "user": "#ff4500",

                # Completer
                "completion-menu.completion": "bg:#000000 #ffffff",
                "completion-menu.completion.current": "bg:#00aaaa #000000",
                "scrollbar.background": "bg:#88aaaa",
                "scrollbar.button": "bg:#222222"
            }
        }
        self.config.colored = self.config["colored"]
        self.style = Style.from_dict(self.config["style"])
        self.manager = manager
        self.file = None
        self.mode = "w"
        self.userInput = None

        if platform.system() == "Windows":
            self.histfile = os.environ["userprofile"] + \
                r"\.voidhistory"  # Rename this
        else:
            # Rename this ... alternative for linux or Unix based systems
            self.histfile = os.path.expanduser("~")+r"/.voidhistory"

        self.history = FileHistory(self.histfile)

        if not args.command:
            function_completer = NestedCompleter.from_nested_dict(
                dict.fromkeys(functions))
            pth_completer = path_completer.PathCompleter()
            environ_completer = env_completer.EnvCompleter(
                file_filter=filter)
            merged_completers = merge_completers(
                [function_completer, pth_completer, environ_completer])
            self.completer = ThreadedCompleter(merged_completers)
        else:
            self.completer = None

        super().__init__(completer=self.completer,
                         complete_while_typing=False,
                         auto_suggest=AutoSuggestFromHistory(),
                         search_ignore_case=True,
                         refresh_interval=0,
                         color_depth=ColorDepth.TRUE_COLOR,
                         editing_mode=EditingMode.VI,
                         style=self.style,
                         history=self.history)

    def resolver(self, userInput=None):
        global functions
        self.userInput = userInput
        self.file = None
        self.mode = "w"

        def pipe(uI):
            if len(uI.split(">")) == 2:
                self.userInput, _file = uI.split(">")
                self.mode = "w"
                self.file = str(_file).strip()

            if len(uI.split(">>")) == 2:
                self.userInput, _file = uI.split(">>")
                self.mode = "a"
                self.file = str(_file).strip()

        if userInput == "":
            return

        userInput = self.envirotize(userInput)
        userInput = userInput.replace("\\", "\\\\")

        def start(userInput):
            result = None
            splitInput = shlex.split(userInput, posix=False)

            old_stdout = sys.stdout
            sys.stdout = mypipe = StringIO()

            try:
                functions[splitInput[0]](self, *splitInput[1:])
                result = mypipe.getvalue()
                sys.stdout = old_stdout
            except KeyError:
                sys.stdout = old_stdout
                try:
                    os.chdir(" ".join(splitInput))
                except:
                    try:
                        output = eval(userInput)
                        if type(output) not in [object, type(dir)]:
                            result = output
                        else:
                            raise Exception
                    except:
                        result = run_command(userInput)

            if result != None:
                if self.file != None:
                    with open(self.file, self.mode, encoding="utf-8") as f:
                        f.write(result)
                        f.close()
                else:
                    print(result)

        if len(userInput.split("&")) > 1:
            instances = userInput.split("&")
            for instance in instances:
                pipe(instance)
                start(instance)
            return

        pipe(self.userInput)

        start(self.userInput)

    def run(self):
        if args.command:
            self.resolver(" ".join(args.command))
            return

        while True:
            try:
                iprompt = str(self.config["prompt"])
                pattern = re.compile(r"[$][{]\w*[}]")
                found = (re.findall(pattern, iprompt))
                for item in found:
                    ipatternt = re.compile(r"\w+")
                    ifound = re.findall(ipatternt, item)[0]

                    found = promptvar.vars[ifound]
                    if type(found) == type(isadmin) or type(found) == type(os.getcwd):
                        found = found()

                    iprompt = iprompt.replace(item, found)

                self.resolver(self.prompt(HTML(iprompt)))
            except KeyboardInterrupt:
                sys.exit(0)


def run():
    app = Shell(verbose=args.verbose)
    app.run()


if __name__ == "__main__":
    run()
