import enum
from typing import Optional, List, Union

from pydantic import BaseModel, EmailStr
from pydantic.class_validators import validator
from pydantic.fields import ModelField
from pylon.core.tools import log


class VertexAISettings(BaseModel):
    model_name: str = 'text-bison@001'
    temperature: float = 1.0
    max_decode_steps: int = 256
    top_p: float = 0.8
    top_k: int = 40
    tuned_model_name: str = ''


class OpenAISettings(BaseModel):
    engine: str = 'davinci'
    temperature: float = 1.0
    max_decode_steps: int = 256
    top_p: float = 0.8
    top_k: int = 40


class PromptModel(BaseModel):
    name: str
    description: str | None
    prompt: str
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
