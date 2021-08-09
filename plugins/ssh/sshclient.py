import argparse
import os
import socket
import traceback
import subprocess

from functions import functions
from prompt_toolkit.shortcuts import (checkboxlist_dialog, input_dialog,
                                      message_dialog, radiolist_dialog)
from prompt_toolkit.shortcuts.dialogs import yes_no_dialog
from yapsy.IPlugin import IPlugin


def sshclient(shell, *querry):
    style = shell.dialog_style

    def check_ssh(server_ip, port=22):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.connect((server_ip, port))
        except Exception:
            print(traceback.format_exc())
            return False
        else:
            test_socket.close()
        return True

    fparser = argparse.ArgumentParser(prog="sshclient")
    fparser.add_argument("mode", help="Select what you want to do",
                         type=str, default="connect", choices=["connect", "add", "remove"])
    try:
        fargs = fparser.parse_args(querry)
    except SystemExit:
        return

    try:
        if not "sshconnections" in shell.config.config:
            shell.config.config["sshconnections"] = {}

        if fargs.mode == "connect":
            if len(shell.config.config["sshconnections"]) <= 0:
                message_dialog(
                    title="SSH Client",
                    text="No SSH Connections found",
                    style=style
                ).run()
                return

            else:
                result = radiolist_dialog(
                    title="Connect",
                    text="Select SSH host",
                    values=[(i, str(i))
                            for i in shell.config.config["sshconnections"].keys()],
                    style=style
                ).run()
                if result:
                    target = shell.config.config["sshconnections"][result]
                    call = f'ssh -p {target["port"]} {("-i %s" % target["private_key"]) if target["private_key"] else ""} {target["username"]}@{target["ip"]}'
                    os.system(call)

        elif fargs.mode == "add":
            name = input_dialog(title="Name",
                                text="Please, enter name for SSH connection", style=style).run()
            if not name:
                return

            username = input_dialog(title="Username",
                                    text="Username for SSH connection", style=style).run()
            if not username:
                return

            ip_address = input_dialog(title="IP",
                                      text="IP address for SSH connection", style=style).run()
            if not ip_address:
                return

            port = input_dialog(title="Port",
                                text="Port for SSH connection", style=style).run()
            if not port:
                return

            while True:
                private_key = input_dialog(title="SSH Key",
                                           text="Input path to your key (or leave blank if you do not have one)", style=style).run()

                if private_key == "":
                    break
                elif os.path.isfile(private_key):
                    break
                else:
                    message_dialog(title="Error",
                                   text="File not found... Try again", style=style).run()

            if not check_ssh(ip_address, port=int(port)):
                if not yes_no_dialog(
                        title="SSH Client",
                        text="SSH Connection cannot be established, continue ?",
                        yes_text="Continue",
                        no_text="Exit").run():
                    return
            else:
                message_dialog(title="Connected",
                               text="Connection can be established", style=style).run()

            shell.config.config["sshconnections"][name] = {
                "username": username,
                "ip": ip_address,
                "port": port,
                "private_key": private_key
            }

            message_dialog(title="Added",
                           text=f"Name: {name}\nUsername: {username}\nIP: {ip_address}\nPort: {port}\nPrivate key: {private_key}", style=style).run()

            shell.config.save()

        elif fargs.mode == "remove":
            selected = checkboxlist_dialog(
                title="Remove SSH connection",
                values=[(i, i) for i in shell.config.config["sshconnections"]],
                style=style
            ).run()

            for item in selected:
                del shell.config.config["sshconnections"][item]

            shell.config.save()
    except:
        print(traceback.format_exc())


class PluginOne(IPlugin):
    def main(self):
        functions["sshclient"] = sshclient
