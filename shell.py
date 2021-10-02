import platform
import os
import pip

from pyupdater.client import Client
from client_config import ClientConfig

# Information for pyupdater
APP_NAME = 'PyShell'
APP_VERSION = '0.0.1'

# Callback for pyupdater for displaying progress


def print_status_info(info):
    total = info.get(u'total')
    downloaded = info.get(u'downloaded')
    status = info.get(u'status')
    print(downloaded, total, status)


# Initialize pyupdater client
client = Client(ClientConfig())
client.refresh()

client.add_progress_hook(print_status_info)

# Do update check
app_update = client.update_check(APP_NAME, APP_VERSION)

# If update is available, download it
if app_update is not None:
    app_update.download()

# Restart the app
if app_update.is_downloaded():
    app_update.extract_restart()

# Try to initialize the app
try:
    import main
except Exception as e:
    cwd = os.getcwd()
    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)

    if platform.system() == "Windows":
        directory = ".\\plugins"
    else:
        directory = "./plugins"

    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(directory):
        listOfFiles += [os.path.join(dirpath, file)
                        for file in filenames if file == "requirements.txt"]

    plugin_requirements = []
    for file in listOfFiles:
        for _requirement in open(file, "r", encoding="utf-16").readlines():
            plugin_requirements.append(_requirement.replace("\n", ""))

    requirements = [i.replace("\n", "") for i in open(
        "requirements.txt", "r", encoding="utf-16").readlines()]

    print(f"Main requirements: {requirements}")
    print(f"Found plugin requirements: {plugin_requirements}")

    if input("Proceed with installation ? ( y / n ) ").strip() == "y":
        requirements.extend(plugin_requirements)
        pip.main(["install"] + requirements)

    os.chdir(cwd)

finally:
    import main
    main.run()
