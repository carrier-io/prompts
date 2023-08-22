import enum
from typing import Optional

from pydantic import BaseModel, validator, root_validator
from pylon.core.tools import log
from ...utils.ai_providers import AIProvider


class PromptType(str, enum.Enum):
    chat = 'chat'
    structured = 'structured'
    freeform = 'freeform'


class PromptModel(BaseModel):
    name: str
    description: str | None
    prompt: str
    project_id: Optional[int] = None
    test_input: Optional[str] = None
    integration_id: Optional[int] = None
    type: PromptType = PromptType.structured
    model_settings: dict | None = None

    class Config:
        use_enum_values = True

    @root_validator
    def check_settings(cls, values: dict):
        if not (values['project_id'] and values['integration_id']):
            return values
        project_id, integration_id = values['project_id'], values['integration_id']
        integration = AIProvider.get_integration(project_id, integration_id)
        model_settings = values['model_settings']
        response = AIProvider.parse_settings(integration, model_settings)
        if not response['ok']:
            raise ValueError('Cannot determine parser for model_settings')
        values['model_settings'] = response['item']
        return values


class PromptUpdateModel(PromptModel):
    id: int


class PredictPostModel(BaseModel):
    input_: str
    integration_id: int
    integration_settings: Optional[dict] = {}
    prompt_id: Optional[int] = None
    project_id: Optional[int] = None
    examples: Optional[list] = []
    context: Optional[str] = ''
    variables: Optional[dict] = {}

    class Config:
        fields = {'input_': 'input'}

    @root_validator
    def check_settings(cls, values: dict):
        if not (values['project_id'] and values['integration_id']):
            return values
        project_id, integration_id = values['project_id'], values['integration_id']
        
        integration = AIProvider.get_integration(project_id, integration_id)
        model_settings = values['integration_settings']
        response = AIProvider.parse_settings(integration, model_settings)
        
        if not response['ok']:
            raise ValueError('Cannot determine parser for model_settings')
        values['integration_settings'] = response['item']
        return values
