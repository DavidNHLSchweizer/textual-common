from asyncio import create_task
import asyncio
from typing import Iterable, Protocol
from textual import work
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Log, Static
from textual.message import Message
import logging

class TerminalWrite(Message):
    def __init__(self, line: str) -> None:
        self.line = line
        super().__init__()
class RunScript(Protocol):
    def __call__(self, **kwdargs)->bool:
        pass

class TerminalButtons(Static):
    def compose(self)->ComposeResult:
        with Horizontal():
            yield Button('Save Log', variant= 'primary', id='save_log')
            yield Button('Close', variant ='success', id='close') 
            # yield Button('Cancel', variant = 'error', id='cancel')

class TerminalForm(Static):
    def compose(self)->ComposeResult:
        yield Log()
        yield TerminalButtons()
    @property
    def terminal(self)->Log:
        return self.query_one(Log)

    
class TerminalScreen(Screen):
    def __init__(self, **kwdargs):
        self._running = False
        super().__init__(**kwdargs)
    def compose(self) -> ComposeResult:
        yield TerminalForm()
    @property
    def terminal(self)->Log:
        return self.query_one(TerminalForm).terminal
    def __script_wrapper(self, script: RunScript, **kwdargs):
        logging.debug(f'running {kwdargs}')
        result = script(**kwdargs)
        self.post_message(TerminalWrite(f'READY {result}'))
    @work(exclusive=True, thread=True)
    async def run(self, script: RunScript, **kwdargs)->bool:
        try:
            self._running = True
            self.__script_wrapper(script, **kwdargs)
        finally:
            self._running = False
    def clear(self):
        self.terminal.clear()
    def write(self, s: str):
        self.terminal.write(s)
    def write_line(self, s: str):
        self.terminal.write_line(s)
    def write_lines(self, lines:Iterable[str]):
        self.terminal.write_lines(lines)
    def close(self):
        if not self._running:
            self.dismiss(True)
    def save_log(self, filename: str):
        with open(filename, 'w') as file:
            for line in self.terminal.lines:
                file.write(line +'\n')
    def on_button_pressed(self, message: Button.Pressed):
        match message.button.id:
            case 'save_log': self.save_log('bell.txt')
            case 'close': self.close()
            # case 'cancel': dit werkt niet echt, want de thread loopt gewoon door al wordt het "gecanceld"...
            #     self.write_line('cancelling')
            #     cancelled = self.workers.cancel_group(self, 'default')
            #     self.write_line(str(cancelled))
        message.stop()
    def on_terminal_write(self, msg: TerminalWrite):
        self.write_line(msg.line)
        self.refresh()
