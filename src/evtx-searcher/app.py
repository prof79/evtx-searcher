# app.py

#region Imports

import asyncio
import json

from glob import glob
from pathlib import Path, PurePath
from typing import List, Literal, Optional

from textual import work
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.driver import Driver
from textual.message import Message
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Header,
    LoadingIndicator,
)

from evtx import PyEvtxParser

from event_viewer import EventViewer
from search_form import SearchForm

#endregion

#region App Class

class EvtxSearcher(App):
    """The application class of evtx-searcher."""

    CSS_PATH = 'app.tcss'

    BINDINGS = [
        ('d', 'toggle_dark', 'Toggle dark mode'),
        ('s', 'search', 'Search events'),
        ('q', 'quit', 'Quit application'),
    ]


    #EVENT_LIMIT = 250
    EVENT_LIMIT = 250000


    class SearchResult(Message):
        def __init__(self) -> None:
            super().__init__()
            #self.records = records


    def __init__(
                self,
                driver_class: type[Driver] | None = None,
                css_path: str | PurePath | List[str | PurePath] | None = None,
                watch_css: bool = False,
                ansi_color: bool = False,
                path: Path = Path.cwd(),
            ):

        super().__init__(driver_class, css_path, watch_css, ansi_color)

        self.path = path

        self.records: list[dict] = []


    def on_mount(self) -> None:
        self.title = 'EVTX SEARCHER'
        self.query_one('#events').display = False
        self.query_one('#progress').display = False


    def compose(self) -> ComposeResult:
        yield Header()
        yield LoadingIndicator(
            id='progress',
        )
        yield SearchForm(
            id='search_form',
            path=self.path,
        )
        yield EventViewer(
            id='events',
        )
        yield Footer()


    def try_query_one(self, selector: str) -> Optional[Widget]:
        try:
            return self.query_one(selector)
        
        except NoMatches:
            return None


    def action_toggle_dark(self) -> None:
        self.theme = 'textual-light' if self.theme == 'textual-dark' else 'textual-dark'


    def action_search(self) -> None:
        try:
            search_form = self.query_one('#search_form')

            self.notify('Search form already open.')
        
        except NoMatches:
            search_form = SearchForm(
                id='search_form',
                path=self.path,
            )

            self.mount(search_form)


    def on_search_form_submitted(self, event: SearchForm.Submitted) -> None:
        self.notify(f'Starting search for event {event.event_id} ...')

        self.query_one('#progress').display = True

        viewer = self.try_query_one('#events')

        if viewer is not None:
            viewer.display = False

        self.search_event(event.event_id)


    def on_evtx_searcher_search_result(self, message: SearchResult) -> None:
        if viewer := self.try_query_one('#events'):
            if isinstance(viewer, EventViewer):
                if len(self.records) == 0:
                    self.notify('No events found.', severity='warning')
                viewer.records = self.records
                viewer.show_records()


    def on_event_viewer_events_loaded(self, message: EventViewer.EventsLoaded):
        #self.notify(f'Parent got events loaded from event viewer')

        viewer = self.try_query_one('#events')

        if viewer is not None:
            viewer.display = True

        self.query_one('#progress').display = False


    @work(exclusive=True, thread=True)
    def search_event(self, event_id: int) -> None:

        files = glob(str(self.path / '*.evtx'))

        for file in files:

            # Clear existing search results
            self.records = []

            parser = PyEvtxParser(file)

            for record in parser.records_json():
                event = json.loads(record['data'])

                if event['Event']['System']['EventID'] == event_id:
                    self.records.append(event)

                if len(self.records) > self.EVENT_LIMIT:
                    self.notify(
                        f'Limit of {self.EVENT_LIMIT} events reached, aborting search ...',
                        severity='warning',
                    )
                    break

        self.post_message(self.SearchResult())

#endregion
