from dataclasses import dataclass, asdict, field
from typing import List, Union

@dataclass
class Action:
    action:str

@dataclass
class SetFieldValueAction(Action):
    field_name:str 
    value:str

@dataclass
class Button:
    type:str
    caption:str 
    target: str 
    actions:List[Union[Action,dict]] = field(default_factory=list)

@dataclass
class Message:
    type: str
    text: str
    buttons: List[Button] = field(default_factory=list)

    def add_button(self, button: Button):
        self.buttons.append(button)

@dataclass
class QuickReply:
    type: str
    caption: str
    target: str

@dataclass
class Content:
    type: str
    messages: List[Message] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    quick_replies: List[QuickReply] = field(default_factory=list)

    def add_message(self, message: Message):
        self.messages.append(message)

    def add_action(self, action: Action):
        self.actions.append(action)

    def add_quick_reply(self, quick_reply: QuickReply):
        self.quick_replies.append(quick_reply)

@dataclass
class DynamicBlockV2:
    content:Content
    version: str = "v2"
    
    def build(self):
        return asdict(self)

