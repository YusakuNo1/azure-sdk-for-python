from typing import Dict, Type
from azure.ai.inference.models import ChatRequestMessage, SystemMessage, UserMessage, AssistantMessage, ToolMessage
from .core import Prompty
from .utils import load, prepare
# from .parsers import RoleMap


class RoleMap:
    _ROLE_MAP: Dict[str, Type[ChatRequestMessage]] = {
        "system": SystemMessage,
        "user": UserMessage,
        "human": UserMessage,
        "assistant": AssistantMessage,
        "ai": AssistantMessage,
        "function": ToolMessage,
    }
    ROLES = _ROLE_MAP.keys()

    @classmethod
    def get_message_class(cls, role: str) -> Type[ChatRequestMessage]:
        return cls._ROLE_MAP[role]


class PromptConfig:
    def __init__(self, prompty: Prompty) -> None:
        self.prompty = prompty
        self.model_name = "gpt-4o-mini"     # TODO: This should come from prompty

    def render(self, input_variables: dict[str, any], message_format: str | None = None) -> list[ChatRequestMessage]:
        if message_format == None:
            parsed = prepare(self.prompty, input_variables)

            messages = []
            for message in parsed:
                message_class = RoleMap.get_message_class(message["role"])
                messages.append(message_class(content=message["content"]))
            return messages
        
        elif message_format == "openai":
            # Output the JSON format for OpenAI
            pass

        else:
            return  prepare(self.prompty, input_variables)
