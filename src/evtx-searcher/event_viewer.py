# event_viewer.py

#region Imports

from glob import glob
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import (
    Center,
    HorizontalGroup,
    VerticalGroup,
    VerticalScroll,
)
from textual.css.query import NoMatches
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
    Tree,
)

#endregion

#region Widget Class

class EventViewer(VerticalScroll):
    """An event viewer widget."""

    BINDINGS = [
        ('c', 'close', 'Close viewer'),
    ]



    class EventsLoaded(Message):
        def __init__(self) -> None:
            super().__init__()



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
            ) -> None:

        self.records: list[dict] = []

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


    async def on_mount(self) -> None:
        try:
            self.query_one('#log').focus()
            self.show_records()
        
        except NoMatches:
            pass


    def compose(self) -> ComposeResult:

        yield HorizontalGroup(

            Tree(
                'Events',
                id='tree',
            ),

            RichLog(
                id='log',
            ),

            id='contents',
        )


    def action_close(self) -> None:
        self.remove()


    def on_tree_node_selected(self, message: Tree.NodeSelected):
        data = message.node.data

        if data is not None:
            index = int(data)

            log = self.query_one('#log')

            if isinstance(log, RichLog):
                log.clear()
                log.write(self.records[index])


    @work(exclusive=True, thread=True)
    def show_records(self) -> None:
        #self.notify('Got search results')

        log = self.query_one('#log')

        if isinstance(log, RichLog):
            log.clear()

            if len(self.records) > 0:
                log.write(self.records[0])

        tree = self.query_one('#tree')

        if isinstance(tree, Tree):
            tree.clear()
            tree.root.expand()

            for index, record in enumerate(self.records):
                date_time = record['Event']['System']['TimeCreated']['#attributes']['SystemTime']
                tree.root.add(
                    date_time,
                    index,
                )

        self.post_message(self.EventsLoaded())

#endregion
