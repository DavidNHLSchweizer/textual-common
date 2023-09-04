from __future__ import annotations
from enum import Enum
import logging
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Label
from textual.message import Message

class VerifyResult(Enum):
    YES = 1
    NO = 2
    CANCEL = 3
    ALL =  4
    def as_bool(self):
        return self in [VerifyResult.YES, VerifyResult.ALL]
    @staticmethod
    def from_bool(value: bool)->VerifyResult:
        return VerifyResult.YES if value else VerifyResult.NO
            
class VerifyMessage(Message):
    def __init__(self, result: VerifyResult, originator_key: str):
        self.result = result
        self.originator_key = originator_key
        super().__init__()

class VerifyYesNoScreen(ModalScreen[bool]):
    def __init__(self, question: str, yes_button: str, no_button: str):
        self._question = question
        self._yes_button = yes_button
        self._no_button = no_button
        super().__init__()
    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self._question, id="question"),
            Button(self._yes_button, variant="error", id="yes"),
            Button(self._no_button, variant="success", id="no"),
            id="dialog",
        )
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

def verify_yes_no(originator_screen: Screen, question: str, yes_button: str, no_button: str, originator_key: str)->None:
    def __callback_verify(result: bool):
        originator_screen.post_message(VerifyMessage(VerifyResult.from_bool(result), originator_key))
    dialog = VerifyYesNoScreen(question, yes_button, no_button)
    originator_screen.app.push_screen(dialog, callback = __callback_verify)

