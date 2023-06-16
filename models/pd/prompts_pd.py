import enum
from typing import Optional, List, Union

from pydantic import BaseModel, EmailStr
from pydantic.class_validators import validator
from pydantic.fields import ModelField
from pylon.core.tools import log


class PromptType(str, enum.Enum):
    structured = 'structured'
    freeform = 'freeform'


class PromptModel(BaseModel):
    name: str
    description: str | None
    type: PromptType = PromptType.freeform
    prompt: str

    class Config:
        use_enum_values = True


class PromptUpdateModel(PromptModel):
    id: int


class ExampleModel(BaseModel):
    prompt_id: int
    input: str
    output: str


class ExampleUpdateModel(ExampleModel):
    id: int
