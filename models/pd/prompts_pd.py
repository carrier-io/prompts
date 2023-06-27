import enum
from typing import Optional, List, Union

from pydantic import BaseModel, EmailStr
from pydantic.class_validators import validator
from pydantic.fields import ModelField
from pylon.core.tools import log


class PromptType(str, enum.Enum):
    chat = 'chat'
    structured = 'structured'
    freeform = 'freeform'


class VertexAISettings(BaseModel):
    model_name: str = 'text-bison@001'
    temperature: float = 1.0
    max_decode_steps: int = 256
    top_p: float = 0.8
    top_k: int = 40
    tuned_model_name: str = ''


class OpenAISettings(BaseModel):
    model: str = 'text-davinci-003'
    temperature: float = 1.0
    max_tokens: int = 7
    top_p: float = 0.8


class PromptModel(BaseModel):
    name: str
    description: str | None
    prompt: str
    type: PromptType = PromptType.structured
    model_settings: VertexAISettings | OpenAISettings | None = None

    class Config:
        use_enum_values = True


class PromptUpdateModel(PromptModel):
    id: int


class ExampleModel(BaseModel):
    prompt_id: int
    input: str
    output: str
    is_active: bool = True


class ExampleUpdateModel(ExampleModel):
    id: int
