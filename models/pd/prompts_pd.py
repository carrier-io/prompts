import enum
from typing import Optional

from pydantic import BaseModel, validator
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
    model_name: str = 'text-davinci-003'
    temperature: float = 1.0
    max_tokens: int = 7
    top_p: float = 0.8


class AzureOpenAISettings(BaseModel):
    model_name: str = 'gpt-35-turbo'
    api_version: str = '2023-03-15-preview'
    api_base: str = "https://ai-proxy.lab.epam.com"
    temperature: float = 0
    max_tokens: int = 7
    top_p: float = 0.8


class PromptModel(BaseModel):
    name: str
    description: str | None
    prompt: str
    test_input: Optional[str] = None
    integration_id: Optional[int] = None
    type: PromptType = PromptType.structured
    model_settings: dict | None = None

    class Config:
        use_enum_values = True

    @validator('model_settings')
    def choose_correct_model_for_settings(cls, value: dict):
        log.info('validator %s %s', value, type(value))
        if isinstance(value, dict):
            if 'max_decode_steps' in value:
                return VertexAISettings.parse_obj(value)
            elif 'max_tokens' in value:
                return OpenAISettings.parse_obj(value)
            else:
                raise ValueError('Cannot determine parser for model_settings')
        return value


class PromptUpdateModel(PromptModel):
    id: int


class PredictPostModel(BaseModel):
    input_: str
    integration_id: int
    integration_settings: Optional[dict] = {}
    prompt_id: Optional[int] = None
    examples: Optional[list] = []
    context: Optional[str] = ''
    variables: Optional[dict] = {}

    class Config:
        fields = {'input_': 'input'}
