from __future__ import annotations
from enum import Enum
import logging
from typing import Iterable
from textual.app import App, ComposeResult

from textual.message_pump import MessagePump
from textual.containers import Grid, Horizontal, Vertical, Center
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import Button, Label, Static

from textual.message import Message

from button_bar import ButtonBar, ButtonDef


# class VerifyResult(Enum):
#     YES = 1
#     NO = 2
#     CANCEL = 3
#     ALL =  4
#     def as_bool(self):
#         return self in [VerifyResult.YES, VerifyResult.ALL]
#     @staticmethod
#     def from_bool(value: bool)->VerifyResult:
#         return VerifyResult.YES if value else VerifyResult.NO
            
class DialogMessage(Message):
    def __init__(self, result_str: str, originator_key: str):
        self.result_str = result_str
        self.originator_key = originator_key
        super().__init__()

# class VerifyMessage(Message):
#     def __init__(self, result: VerifyResult, originator_key: str):
#         self.result = result
#         self.originator_key = originator_key

class DialogForm(Static):
    DEFAULT_CSS = """   
        DialogForm {
            align: center middle;
            # width: 80;
            height: 11;
            border: thick $surface 50%;
            background: rgb(224,33,138);
        }
        DialogForm Label{
            column-span: 2;
            height: 1fr;
            width: 1fr;
            content-align: center middle;
        }
    """    
    def __init__(self, label_str: str, buttons: Iterable[ButtonDef]): 
        self._label_str = label_str
        self._buttons = buttons
        super().__init__()
    def compose(self) -> ComposeResult:
        with Center():
            yield Label(self._label_str)
            yield ButtonBar(self._buttons)
    def on_mount(self):
        w = (80 / len(self._buttons))-1
        logging.debug(f'{w=}')
        for button in self.query(Button):
            button.styles.width = w

class DialogScreen(ModalScreen[str]):
    DEFAULT_CSS = """   
        DialogScreen {
            align: center middle;
            background: rgb(224,33,138) 50%;
        }
        DialogScreen DialogForm{
            align: center middle;
            width: 90;
            height: 11;
            border: thick $surface 50%;
        }
    """
    def __init__(self, label_str: str, buttons: Iterable[ButtonDef], originator_key: str):
        self._label_str = label_str
        self._buttons = buttons
        self.originator_key = originator_key
        self.dialog_result  = None
        super().__init__()
    def compose(self) -> ComposeResult:
        yield DialogForm(self._label_str, self._buttons)
    def run(self, originator: MessagePump)->str:
        def __callback_verify(result: str):
            originator.post_message(DialogMessage(result, self.originator_key))
        self.dialog_result  = None
        self.app.push_screen(self, callback = __callback_verify)                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.label)
        event.stop()

def run_dialog(originator: MessagePump, screen: DialogScreen)->str:
    return screen.run(originator)

def message(originator: MessagePump, message: str, originator_key='message'):
    run_dialog(originator, DialogScreen(message, [ButtonDef('OK', variant='primary')], originator_key=originator_key))
               
def verify(originator: MessagePump, question: str, originator_key='verify')->str:
    return run_dialog(originator, DialogScreen(question, [ButtonDef('Ja', variant='success'), ButtonDef('Nee', variant='error')], originator_key=originator_key))

# class VerifyYesNoScreen(DialogScreen):
#     def __init__(self, question: str, yes_button: str, no_button: str): #, id = 'YesNo'):
#         logging.debug(f'in here:')
#         butlist = [yes_button, no_button]
#         super().__init__(!question, butlist) #, id=id)
#         logging.debug(f'out here:')
#     def compose(self) -> ComposeResult:
#         logging.debug('yielding 123...')
#         yield from super()
    
if __name__ == "__main__":
    from textual.widgets import Header, Footer
    logging.basicConfig(filename='verify.log', filemode='w', format='%(module)s-%(funcName)s-%(lineno)d: %(message)s', level=logging.DEBUG)
    class TestApp(App):
        BINDINGS = [("v", "verify", "Verify")]
        
        def compose(self) -> ComposeResult:
            yield Header()
            yield Footer()
    
        async def action_verify(self) -> None:
            """An action to test verify."""
            result = verify(self, 'Wat is daarop uw antwoord?')
            logging.debug(f'returned: {result}')            

        def on_dialog_message(self, event: DialogMessage):
            logging.debug(f'resultaat: {event.result_str} {event.originator_key}')
            match event.originator_key:
                case 'verify':
                    message(self, f'resultaat: {event.result_str} {event.originator_key}')

    app = TestApp()
    app.run()