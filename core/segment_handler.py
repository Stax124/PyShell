from os import getcwd
import utils
import importlib
from segments import root

def handle_segment(segment) -> tuple[str, bool]:
    text_inside = ""
    skip = False

    module = importlib.import_module("."+segment["type"], package="segments")
    text_inside, skip = module.main(segment)

    return text_inside, skip
