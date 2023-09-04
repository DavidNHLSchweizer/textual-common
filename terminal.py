import datetime
from typing import Iterable, Protocol
from textual import work
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Log, Static
from textual.message import Message
import logging

from button_bar import ButtonBar, ButtonDef

class TerminalWrite(Message):
    def __init__(self, line: str) -> None:
        self.line = line
        super().__init__()
class RunScript(Protocol):
    def __call__(self, **kwdargs)->bool:
        pass

class TerminalForm(Static):
    def compose(self)->ComposeResult:
        yield Log()
        yield ButtonBar([ButtonDef('Save Log', variant= 'primary', id='save_log'),
                         ButtonDef('Close', variant ='success', id='close')])
    @property
    def terminal(self)->Log:
        return self.query_one(Log)
    
class TerminalScreen(Screen):
    DEFAULT_CSS = """
        TerminalScreen {
            align: center middle;
            background: black 50%;
        }
        TerminalForm {
            width: 90%;
            height: 90%;
        }
        TerminalForm Log {
            background: black;
            color: lime;
            border: round white;      
            min-height: 20;
            min-width: 80; 
        }
        TerminalScreen ButtonBar Button {
            max-width: 20;
            outline: solid yellowgreen;
        }
    """
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

if __name__=="__main__":
    from textual.widgets import Header, Footer
    from textual.app import App

    global_terminal: TerminalScreen = None
    def testscript(**kwdargs)->bool:
        global_terminal.post_message(TerminalWrite(f'params {kwdargs}'))   
        for i in range(1,kwdargs.pop('N')):
            if i % 300 == 0:
                global_terminal.post_message(TerminalWrite(f'dit is {i}'))            
                logging.debug(f'dit is {i}')
        return False

    class TestApp(App):
        BINDINGS= [('r', 'run', 'Run terminal')]

        def __init__(self, **kwdargs):
            self.terminal_active = False
            super().__init__(**kwdargs)
        def compose(self) -> ComposeResult:
            yield Header()
            yield Footer()
        @property
        def terminal(self)->TerminalScreen:
            if not hasattr(self, '_terminal'):
                self._terminal = self.get_screen('terminal')
                global global_terminal 
                global_terminal = self._terminal
            return self._terminal
        def on_mount(self):
            self.install_screen(TerminalScreen(), name='terminal')
        def callback_run_terminal(self, result: bool):
            logging.debug(f'callback from terminal {result}')
            self.terminal_active = False    
        async def activate_terminal(self)->bool:
            logging.debug(f'activate run terminal {self.terminal_active}')
            if self.terminal_active:
                return False
            await self.app.push_screen('terminal', self.callback_run_terminal)
            self.terminal_active = True
            self.terminal.clear()
            return True
        async def action_run(self):
            if await self.activate_terminal():
                self.terminal.write(f'INITIALIZE RUN {datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y, %H:%M:%S")}')
                self.terminal.run(testscript, N=50000)                

if __name__ == "__main__":
    logging.basicConfig(filename='terminal.log', filemode='w', format='%(module)s-%(funcName)s-%(lineno)d: %(message)s', level=logging.DEBUG)
    app = TestApp()
    app.run()
