import enum
from typing import Optional

from pydantic import BaseModel, EmailStr
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


class VertexAIIntegrationSettings(VertexAISettings):
    service_account_info: dict
    project: str
    zone: str


class OpenAISettings(BaseModel):
    model_name: str = 'text-davinci-003'
    temperature: float = 1.0
    max_tokens: int = 7
    top_p: float = 0.8


class OpenAIIntegrationSettings(OpenAISettings):
    api_token: dict


class PromptModel(BaseModel):
    name: str
    description: str | None
    prompt: str
    test_input: Optional[str] = None
    integration_id: Optional[int] = None
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


class PredictPostModel(BaseModel):
    input_: str
    integration_id: int
    integration_settings: Optional[dict] = {}
    prompt_id: Optional[int] = None
    examples: Optional[list] = []
    context: Optional[str] = ''

    class Config:
        fields = {'input_': 'input'}
