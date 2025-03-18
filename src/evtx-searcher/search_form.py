# panel.py

#region Imports

from glob import glob
from pathlib import Path
from time import sleep

from textual import work
from textual.app import ComposeResult
from textual.containers import (
    Center,
    HorizontalGroup,
    VerticalGroup,
    VerticalScroll,
)
from textual.message import Message
from textual.widget import Widget
from textual.widgets import (
    Button,
    Input,
    Label,
    LoadingIndicator,
    Pretty,
    RichLog,
    Rule,
    Static,
    TextArea,
)

#endregion

#region Panel Class

class SearchForm(VerticalScroll):
    """The .evtx search form."""

    def __init__(
                self,
                *children: Widget,
                name: str | None = None,
                id: str | None = None,
                classes: str | None = None,
                disabled: bool = False,
                can_focus: bool | None = None,
                can_focus_children: bool | None = None,
                can_maximize: bool | None = None,
                path: Path,
            ) -> None:

        self.path = path

        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            can_focus=can_focus,
            can_focus_children=can_focus_children,
            can_maximize=can_maximize,
        )



    class Submitted(Message):

        def __init__(self, event_id: int) -> None:
            super().__init__()
            self.event_id = event_id



    def on_mount(self) -> None:
        self.query_one('#id_input').focus()


    def compose(self) -> ComposeResult:

        yield VerticalGroup(

            HorizontalGroup(
                Label('Path:'),
                Input(
                    str(self.path),
                    id='path_input',
                    classes='input',
                    disabled=True,
                ),
            ),

            HorizontalGroup(
                Label('Event ID:'),
                Input(
                    str(4624),
                    id='id_input',
                    classes='input',
                ),
            ),

            Center(
                Button('OK', id='ok'),
            ),

            id='contents',
        )


    def on_button_pressed(self, _: Button.Pressed) -> None:

        id_input = self.query_one('#id_input')

        if isinstance(id_input, Input):
            try:
                event_id = int(id_input.value)

                self.post_message(
                    self.Submitted(event_id)
                )

                self.remove()

            except ValueError:
                self.notify(
                    f'Invalid event ID: {id_input.value}',
                    severity='error',
                )

#endregion
