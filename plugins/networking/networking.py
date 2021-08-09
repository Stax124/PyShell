from yapsy.IPlugin import IPlugin
from functions import functions
import argparse
import threading
from core.constants import c, known_port_names, known_ports
import os
import core.utils

def tcp_scanner(shell, *querry):
    fparser = argparse.ArgumentParser(prog="tcp-scan")
    fparser.add_argument(
        "--target", help="Remote target to scan", type=str, default="127.0.0.1")
    fparser.add_argument("--threads", type=int,
                            help="Number of threads", default=250)
    fparser.add_argument("--port", "-p", type=int, help="Port to scan")
    try:
        fargs = fparser.parse_args(querry)
    except SystemExit:
        return

    import socket
    import time
    from queue import Queue

    threading_lock = threading.Lock()
    target = socket.gethostbyname(fargs.target)
    q = Queue()

    def portscanTCP(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            con = s.connect((target, known_ports[port-1]))
            with threading_lock:
                print(f'TCP {target} {known_ports[port-1]} is open ({known_port_names.get(str(known_ports[port-1]), "unknown")})')
            con.close()
        except:
            pass

    def threader():
        worker = q.get()
        portscanTCP(worker)
        q.task_done()

    for i in range(len(known_ports)):
        t = threading.Thread(target=threader)
        t.setName("TCP-Scanner-"+str(i))
        t.start()

    start = time.time()

    if fargs.port:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((target, fargs.port))
            print(f'TCP {target} {fargs.port} is open')
            print(f'TCP {target} {fargs.port} is open ({known_port_names.get(str(fargs.port),"unknown")})')
            s.close()
        except:
            s.close()
    else:
        for worker in range(1, 1001):
            q.put(worker)

    q.join()
    end = time.time()
    print(f"It took: {end-start} seconds")

def wifipassword(shell, *querry) -> None:
    "Get password of wifi network (Windows only)"
    os.system("netsh wlan show profiles")
    networkName = input("Network name > ")
    os.system(f"netsh wlan show profiles {networkName} key=clear")

def downloadeta(shell, *querry):
    fparser = argparse.ArgumentParser(prog="downloadeta")
    fparser.add_argument("target", help="Targeted download size")
    fparser.add_argument("speed", help="Speed of your connection")
    try:
        fargs = fparser.parse_args(querry)
    except SystemExit:
        return

    out = []
    mdict = {
        "KB": "1000",
        "MB": "1000000",
        "GB": "1000000000",
        "TB": "1000000000000",
        "PB": "1000000000000000",
    }
    for item in [fargs.target, fargs.speed]:
        for multiplier in ["KB", "MB", "GB", "TB", "PB"]:
            if str(item).find(multiplier) != -1:
                item = item.replace(multiplier, "")
                m = mdict.get(multiplier)
                out.append(float(item) * float(m))
    target = out[0]
    speed = out[1]

    print(core.utils.time_reformat(target / speed))
    return

class PluginOne(IPlugin): 
    def main(self):
        functions["tcp-scanner"] = tcp_scanner
        functions["wifipassword"] = wifipassword
        functions["downloadeta"] = downloadeta