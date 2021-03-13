import os
import re
from typing import Callable, Iterable, List, Optional
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document


class EnvCompleter(Completer):
    """
    Complete for Path variables.

    :param get_paths: Callable which returns a list of directories to look into
                      when the user enters a relative path.
    :param file_filter: Callable which takes a filename and returns whether
                        this file should show up in the completion. ``None``
                        when no filtering has to be done.
    :param min_input_len: Don't do autocompletion when the input string is shorter.
    """

    def __init__(
        self,
        only_directories: bool = False,
        get_paths: Optional[Callable[[], List[str]]] = None,
        file_filter: Optional[Callable[[str], bool]] = None,
        min_input_len: int = 0,
        expanduser: bool = False,
    ) -> None:

        self.paths = os.environ["PATH"].split(os.pathsep)
        self.only_directories = only_directories
        self.get_paths = get_paths or (lambda: self.paths)
        self.file_filter = file_filter or (lambda _: True)
        self.min_input_len = min_input_len
        self.expanduser = expanduser

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text = document.text_before_cursor
        _text = text
        try:
            if "'" in text:
                text = text.split("'")
            if '"' in text:
                text = text.split('"')
            else:
                text = text.split()
            if _text.endswith(" "):
                text = ""
            else:
                text = text[-1]
        except:
            text = document.text_before_cursor

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

        if text.find("%") != -1:
            try:
                spl = text.split("%")[1]
                env = os.environ[spl]
                text = text.replace(f"%{spl}%", env)
            except:
                pass

        text = expandvars(text)

        # Complete only when we have at least the minimal input length,
        # otherwise, we can too many results and autocompletion will become too
        # heavy.
        if len(text) < self.min_input_len:
            return

        try:
            # Do tilde expansion.
            if self.expanduser:
                text = os.path.expanduser(text)

            # Directories where to look.
            dirname = os.path.dirname(text)
            if dirname:
                directories = [
                    os.path.dirname(os.path.join(p, text)) for p in self.get_paths()
                ]
            else:
                directories = self.get_paths()

            # Start of current file.
            prefix = os.path.basename(text)

            # Get all filenames.
            filenames = []
            for directory in directories:
                # Look for matches in this directory.
                if os.path.isdir(directory):
                    for filename in os.listdir(directory):
                        if filename.startswith(prefix):
                            filenames.append((directory, filename))

            # Sort
            filenames = sorted(filenames, key=lambda k: k[1])

            # Yield them.
            for directory, filename in filenames:
                completion = filename[len(prefix):]
                full_name = os.path.join(directory, filename)

                if os.path.isdir(full_name):
                    # For directories, add a slash to the filename.
                    # (We don't add them to the `completion`. Users can type it
                    # to trigger the autocompletion themselves.)
                    filename = filename+"/"
                elif self.only_directories:
                    continue

                if not self.file_filter(full_name):
                    continue

                yield Completion(completion, 0, display=filename)
        except OSError:
            pass
