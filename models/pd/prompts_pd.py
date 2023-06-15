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
    id: int
    name: str
    description: str | None
    type: PromptType = PromptType.freeform
    prompt: str
    created_at: str
    updated_at: str

    class Config:
        use_enum_values = True


class ExampleModel(BaseModel):
    id: int
    prompt_id: int
    input: str
    output: str
    created_at: str

    class Config:
        use_enum_values = True
