import platform
import os
import pip


try:
    import main
except Exception as e:
    print(e)

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
            plugin_requirements.append(_requirement)

    requirements = [i.replace("\n", "") for i in open(
        "requirements.txt", "r", encoding="utf-16").readlines()]

    print(f"Main requirements: {requirements}")
    print(f"Found plugin requirements: {plugin_requirements}")

    if input("Proceed with installation ? ( y / n ) ").strip() == "y":
        requirements.extend(plugin_requirements)
        pip.main(["install"] + requirements)

finally:
    import main
    main.run()
