from yapsy.IPlugin import IPlugin
from functions import functions

def default(shell, *querry):
    print("Hello world")

class PluginOne(IPlugin): 
    def main(self):
        functions["example"] = default