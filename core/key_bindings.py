from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.selection import SelectionState, SelectionType


keybindings = KeyBindings()


@keybindings.add("c-a")
def _(event: KeyPressEvent):
    "Select all text when control+a is pressed"

    event.app.current_buffer.selection_state = SelectionState(
        type=SelectionType.LINES)


@keybindings.add("c-c")
def _(event: KeyPressEvent):
    "Handle control+c as copy when text is selected, terminate otherwise"

    if not event.app.current_buffer.selection_state:
        event.app.exit(exception=KeyboardInterrupt, style="class:aborting")
    else:
        event.app.clipboard.set_data(event.app.current_buffer.copy_selection())


@keybindings.add("c-x")
def _(event: KeyPressEvent):
    "Set control+x as cut"

    event.app.clipboard.set_data(event.app.current_buffer.cut_selection())
