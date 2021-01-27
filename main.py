#region Imports
import shlex
import os
import sys
import argparse
import subprocess
import math
import traceback
#endregion

#region Prompt-toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import ThreadedCompleter
from prompt_toolkit import HTML
#endregion

#region Core
from core import config as cfg
from core import default, path_completer
#endregion

#region Plugins
from yapsy.PluginManager import PluginManager
manager = PluginManager()
manager.setPluginPlaces(["plugins"])
manager.collectPlugins()
for plugin in manager.getAllPlugins():
    plugin.plugin_object.main()
#endregion

#region Parser
parser = argparse.ArgumentParser()
parser.add_argument("command", help="Execute following command", nargs="*")
parser.add_argument("-d", "--directory", help="Start in specified directory")

if not sys.stdin.isatty():
    args = parser.parse_args(sys.stdin.readlines())
else:
    args = parser.parse_args()
#endregion

def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    msg = ""
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            msg += output
    return msg

class c:
    header = '\033[95m'
    okblue = '\033[94m'
    okgreen = '\033[92m'
    warning = '\033[93m'
    fail = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

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
                    string = string.replace(value, self.config["aliases"].get(value))

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

    def loadconfig(self):
        self.config.load()

    def __init__(self, verbose=False):
        try:
            if args.directory:
                os.chdir(args.directory)
        except:
            pass

        self.config = cfg.Config(verbose=verbose)
        self.config.fallback = {
            "aliases": {}
        }
        self.manager = manager
        if not args.command:
            self.completer = ThreadedCompleter(path_completer.PathCompleter())
        else:
            self.completer = None
        
        super().__init__(completer=self.completer,
                         complete_while_typing=True,
                         auto_suggest=AutoSuggestFromHistory(),
                         search_ignore_case=True,
                         refresh_interval=0,
                         color_depth=ColorDepth.TRUE_COLOR,
                         editing_mode=EditingMode.VI)

    def resolver(self, userInput=None):
        global functions
        file = None

        if userInput == "":
            return

        userInput = self.envirotize(userInput)
        userInput = userInput.replace("\\", "\\\\")

        def start(userInput):
            result = None
            splitInput = shlex.split(userInput)

            try:
                result = functions[splitInput[0]](self,*splitInput[1:])
            except KeyError:
                try:
                    os.chdir(" ".join(splitInput))
                except:
                    try:
                        output = eval(userInput)
                        if type(output) not in [object, type(dir)]:
                            print(output)
                        else:
                            raise Exception
                    except:
                        result = run_command(" ".join(splitInput))

            if result != None:
                if file != None:
                    with open(file, "w") as f:
                        f.write(result)
                        f.close()
                else:
                    print(result)

        if len(userInput.split("&")) > 1:
            instances = userInput.split("&")
            for instance in instances:
                if len(instance.split(">")) > 1:
                    instance, file = instance.split(">")
                    file = str(file).strip()

                start(instance)
            return

        if len(userInput.split(">")) > 1:
            userInput, file = userInput.split(">")
            file = str(file).strip()

        start(userInput)

    def run(self):
        self.loadconfig()

        if args.command:
            self.resolver(" ".join(args.command))
            return

        while True:
            try:
                self.resolver(self.prompt(f"{os.getcwd()} $ "))
            except KeyboardInterrupt:
                sys.exit(0)


if __name__ == "__main__":
    from functions import functions

    app = Shell(verbose=True)
    app.run()