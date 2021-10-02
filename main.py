# region Imports
from pygit2 import Repository
from prompt_toolkit.shortcuts.dialogs import yes_no_dialog
from yapsy.PluginManager import PluginManager
from functions import functions
import shlex
import os
import sys
import getpass
import argparse
import subprocess
import math
import datetime
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
path = os.path.dirname(__file__)

manager = PluginManager()
manager.setPluginPlaces([path])
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
    USER = getpass.getuser()
except:
    USER = "UNKNOWN"

try:
    DOMAIN = platform.node()
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


# region Git


def getcurrentrepo():
    """Get branch of git repository in current folder

    Returns:
        str: branch of git repository
    """

    try:
        return Repository(r'.').head.shorthand
    except:
        return ""
# endregion


def timenow():
    """Get current time

    Returns:
        str: `Hour:Minute:Second`
    """

    return datetime.datetime.now().strftime(r"%H:%M:%S")


def communicate(command: str, stdin: str = ""):
    """Execute command in shell and return stdout with returncode

    Args:
        command (str): Command for shell
        stdin (str, optional): Set stdin for this command. Defaults to "".

    Returns:
        tuple: (stdout, return_code)
    """

    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE, shell=True, universal_newlines=True, encoding="utf-8")
    process.stdin.write(stdin)
    output = process.communicate()[0]

    try:
        return (output, process.returncode)
    except:
        return (output, None)


def run_command(command: str):
    """Run command, if it fails, print 'Not found'

    Args:
        command (str): Command for shell

    Returns:
        int | None: return_code or None
    """

    try:
        return os.system(command)

    except:
        print("Not found")

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


# Dictionary for use in prompt
promptvar.vars.update(
    {
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
)


class Shell(PromptSession):
    """Shell class with plugin support
    
    >>> app = Shell(verbose=args.verbose)
    >>> app.run()
    """
    
    def envirotize(self, string: str) -> str:
        """Applies environment variables and aliases

        Args:
            string (str): Input string

        Returns:
            str: Evaluated string
        """

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
            "prompt": "<base>┏━━(</base><user>${USER}</user> <base>at</base> <user>${DOMAIN}</user><base>)━[</base><path>${PATH}</path><base>]━[</base><style fg='${green-yellow}'>${REPO}</style><base>]━[</base><style fg='yellow'>${TIME}</style><base>]\n┗━</base><pointer>${ROOT}</pointer> ",
            "style": {
                # Default style
                "": "",

                # Specific style
                "base": "#1a8cff",
                "pointer": "#ff4500",
                "path": "aqua",
                "user": "#ff4500",

                # Completer
                "completion-menu.completion": "bg:#000000 #ffffff",
                "completion-menu.completion.current": "bg:#00aaaa #000000",
                "scrollbar.background": "bg:#88aaaa",
                "scrollbar.button": "bg:#222222"
            },
            "dialog_style": {
                "dialog": "bg:#88ff88",
                "dialog frame-label": "bg:#ffffff #000000",
                "dialog.body": "bg:#000000 #00ff00",
                "dialog shadow": "bg:#00aa00",
            }
        }
        self.config.colored = self.config["colored"]
        self.style = Style.from_dict(self.config["style"])
        self.dialog_style = Style.from_dict(self.config["dialog_style"])
        self.manager = manager
        self.file = None
        self.mode = None
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
            pth_completer = path_completer.PathCompleter(expanduser=True)
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

    def update_return_code(self, return_code: int):
        promptvar.vars.update({"RETURNCODE": return_code})

    def resolver(self, userInput=None):
        """Process string as command

        Args:
            userInput (str, optional): String, that will be evaluated. Defaults to None.

        Returns:
            None
        """

        global functions
        self.userInput = userInput
        self.file = None
        self.mode = None

        if self.userInput == "":
            return

        def filepipe(uI):
            if len(uI.split(">")) == 2:
                self.userInput, _file = uI.split(">")
                self.mode = "w"
                self.file = str(_file).strip()
                return True

            if len(uI.split(">>")) == 2:
                self.userInput, _file = uI.split(">>")
                self.mode = "a"
                self.file = str(_file).strip()
                return True

            return False

        self.userInput = self.envirotize(userInput)
        self.userInput = self.userInput.replace("\\", "\\\\")

        def start(userInput, stdin: str = "", catch=False):
            result = None
            splitInput = shlex.split(userInput, posix=False)

            if catch == True:
                old_stdout = sys.stdout
                sys.stdout = mypipe = StringIO()

            try:
                return_code = 0 if functions[splitInput[0]](
                    self, *splitInput[1:]) == None else 1
                if catch == True:
                    result = mypipe.getvalue()
                    sys.stdout = old_stdout
            except IndexError:
                return_code = 1
                pass
            except KeyError:
                if catch == True:
                    sys.stdout = old_stdout
                try:
                    return_code = 0 if functions["cd"](
                        self, *splitInput[1:], command=False) == None else 1
                except:
                    try:
                        output = eval(userInput)
                        if type(output) not in [object, type(dir), type(__class__)]:
                            result = output
                            return_code = 0
                        else:
                            return_code = 1
                            raise Exception
                    except:
                        if not catch:
                            return_code = run_command(userInput)
                            result = None
                        else:
                            result, return_code = communicate(
                                userInput, stdin=stdin)

            if result != None:
                if self.file != None:
                    with open(self.file, self.mode, encoding="utf-8") as f:
                        f.write(result)
                        f.close()
                else:
                    if not catch:
                        print(result)

            return result, return_code

        if len(self.userInput.split(";")) > 1:
            instances = self.userInput.split(";")
            ret = 0
            for instance in instances:
                catch = filepipe(instance)
                _, ret = start(instance, catch=catch)

            self.update_return_code(ret)
            return

        if len(self.userInput.split("&&")) > 1:
            instances = self.userInput.split("&&")
            ret = 0
            for instance in instances:
                if ret == 0:
                    catch = filepipe(instance)
                    _, ret = start(instance, catch=catch)
                else:
                    self.update_return_code(ret)
                    return
            self.update_return_code(ret)
            return

        if len(self.userInput.split("||")) > 1:
            instances = self.userInput.split("||")
            ret = 1
            for instance in instances:
                if ret != 0:
                    catch = filepipe(instance)
                    _, ret = start(instance, catch=catch)
                else:
                    self.update_return_code(ret)
                    return
            self.update_return_code(ret)
            return

        if len(self.userInput.split("|")) > 1:
            instances = self.userInput.split("|")

            _std = ""
            for instance in instances:
                filepipe(instance)
                _std, return_code = start(instance, _std, catch=True)
            print(_std)
            self.update_return_code(return_code)
            return

        catch = filepipe(self.userInput)

        _, return_code = start(self.userInput, catch=catch)
        self.update_return_code(return_code)

    def run(self):
        """Start infinite shell loop or execute passed command"""

        if args.command:
            self.resolver(" ".join(args.command))
            return

        while True:
            try:
                iprompt = str(self.config["prompt"])
                pattern = re.compile(r"\$\{[^}]*\}")
                found = (re.findall(pattern, iprompt))
                for item in found:
                    ipatternt = re.compile(r"[^$^{].+[^}]")
                    ifound = re.findall(ipatternt, item)[0]

                    found = promptvar.vars[ifound]
                    if type(found) == type(isadmin) or type(found) == type(os.getcwd):
                        found = found()

                    iprompt = iprompt.replace(item, str(found))

                self.resolver(self.prompt(HTML(iprompt)))
            except KeyboardInterrupt or EOFError:
                pass
            except SystemExit:
                exit(0)
            except:
                result = yes_no_dialog(
                    title="Error occured", text=traceback.format_exc(chain=False), yes_text="Continue", no_text="Exit", style=self.dialog_style).run()
                if not result:
                    sys.exit(0)


def run():
    app = Shell(verbose=args.verbose)
    app.run()


if __name__ == "__main__":
    run()
