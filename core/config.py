import datetime
import traceback
import platform
import os
import json


class c:
    header = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    warning = '\033[93m'
    fail = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'


class Config():
    "Class for maintaining configuration information and files"

    def print_timestamp(self, *_str):
        if self.colored:
            print(
                f"{c.bold}[{c.end}{c.warning}{datetime.datetime.now().strftime('%H:%M:%S')}{c.end}{c.bold}]{c.end}", *_str)
        else:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}]", *_str)

    def load(self):
        if self.verbose:
            if self.colored:
                self.print_timestamp(f"{c.bold}Loading config...{c.end}")
            else:
                self.print_timestamp(f"Loading config...")
        try:
            self.config = json.load(open(self.CONFIG, encoding="utf-8"))
            type(self.config.keys())
        except:
            if self.verbose:
                if self.colored:
                    self.print_timestamp(
                        f"{c.warning}Config is unavailable or protected.{c.end} {c.bold}Loading fallback...{c.end}")
                else:
                    self.print_timestamp(
                        f"Config is unavailable or protected. Loading fallback...")
            self.config = self.fallback
            if self.verbose:
                if self.colored:
                    self.print_timestamp(f"{c.bold}Fallback loaded{c.end}")
                else:
                    self.print_timestamp(f"Fallback loaded")
            try:
                if self.verbose:
                    if self.colored:
                        self.print_timestamp(
                            f"{c.bold}Creating new config file:{c.end} {c.green}{self.CONFIG}{c.end}")
                    else:
                        self.print_timestamp(
                            f"Creating new config file: {self.CONFIG}")
                self.save()
            except Exception as e:
                self.print_timestamp(traceback.format_exc())
                if self.verbose:
                    if self.colored:
                        self.print_timestamp(
                            f"{c.fail}Error writing config file, please check if you have permission to write in this location:{c.end} {c.bold}{self.CONFIG}{c.end}")
                    else:
                        self.print_timestamp(
                            f"Error writing config file, please check if you have permission to write in this location: {self.CONFIG}")
                return

        if self.verbose:
            if self.colored:
                self.print_timestamp(f"{c.bold}Config loaded{c.end}")
            else:
                self.print_timestamp(f"Config loaded")

    def __init__(self, verbose=False, colored=True):
        if platform.system() == "Windows":
            self.CONFIG = os.environ["userprofile"] + \
                r"\.voidshell"  # Rename this
        else:
            # Rename this ... alternative for linux or Unix based systems
            self.CONFIG = os.path.expanduser("~")+r"/.voidshell"
        self.config = {}
        self.colored = colored
        self.verbose = verbose
        self.fallback = {}

    def save(self):
        try:
            with open(self.CONFIG, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except:
            self.print_timestamp(f"Unable to save data to {self.CONFIG}")

    def json_str(self):
        return json.dumps(self.config)

    def __repr__(self):
        return self.config

    def __getitem__(self, name: str):
        try:
            return self.config[name]
        except:
            if self.verbose:
                if self.colored:
                    self.print_timestamp(
                        f"{c.bold}{name}{c.end} {c.warning}not found in config, trying to get from fallback{c.end}")
                else:
                    self.print_timestamp(
                        f"{name} not found in config, trying to get from fallback")
            self.config[name] = self.fallback[name]
            self.save()
            return self.fallback[name]

    def __setitem__(self, key: str, val):
        self.config[key] = val

    def __delitem__(self, key: str):
        self.config.pop(key)


if __name__ == "__main__":
    config = Config()
    config.load()
