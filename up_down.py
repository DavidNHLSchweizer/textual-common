import logging
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static,  Button, Input
from textual.validation import Number
from textual.containers import ScrollableContainer

class UpdownButton(Button): pass
class UpdownInput(Input): pass
class UpdownWidget(Static):
    def __init__(self, **kwdargs):
        self._disabled = False
        self._visible = False
        super().__init__(**kwdargs)
    def _get_name(self, what: str)->str:
        return f'{self.name}-{what}-'
    def compose(self) -> ComposeResult:
        yield UpdownButton("+", id = 'plus', name=self._get_name('PLUS'), variant = 'default')
        yield UpdownInput(id='input', name=self._get_name('INPUT'), validators=Number(minimum=1, maximum=999  ))
        yield UpdownButton("-", id = 'minus', name=self._get_name('MINUS'),variant = 'default')
    @property
    def disabled(self)->bool:
        return self._disabled
    @disabled.setter
    def disabled(self, value: bool):
        self._disabled = value
        for node in self.query():
            node.disabled = value
        self.__enable_buttons(self.input_value)        
    @property
    def visible(self)->bool:
        return self._visible
    @visible.setter
    def visible(self, value: bool):
        self._visible = value
        for node in self.query():
            node.visible = value
    @property
    def _input_widget(self)->Input:
        try:
            return self.query_one("#input", Input)
        except:
            return None
    @property
    def input_value(self)->int:
        try:
            return int(self._input_widget.value)
        except:
            return None
    @input_value.setter
    def input_value(self, value: int):
        self._input_widget.value = str(value)
        self.__enable_buttons(self.input_value)
    def __enable_buttons(self, value):
        try:
            minus =  self.query_one("#minus", UpdownButton)
        except:
            return
        if not minus or value is None:
            minus.disabled = True
        else:
            minus.disabled = value <= 1
    def on_mount(self)->None:
        if self.input_value is None:
            self.input_value = 1
        self.__enable_buttons(self.input_value)
        self._input_widget.focus()  
    def __process_button(self, button_id: str)->None:
        try:
            match button_id:
                case 'plus': self.input_value = self.input_value + 1
                case 'minus': self.input_value = self.input_value - 1
        except:
            self.input_value = 1   
    def on_button_pressed(self, event: Button.Pressed)->None:
        self.__process_button(event.button.id)
        event.stop()

if __name__ == "__main__":
    class TestApp(App):
        CSS_PATH = "pizza_panel.css"

        BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
        
        def compose(self) -> ComposeResult:
            yield Header()
            yield Footer()
            yield ScrollableContainer(UpdownWidget())

        def action_toggle_dark(self) -> None:
            """An action to toggle dark mode."""
            self.dark = not self.dark

    app = TestApp()
    app.run()