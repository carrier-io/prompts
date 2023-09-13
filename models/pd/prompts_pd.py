import enum
from typing import Optional

from pydantic import BaseModel, validator, root_validator, ValidationError
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
    integration_uid: Optional[str] = None
    type: PromptType = PromptType.structured
    model_settings: dict | None = None
    version: Optional[str] = 'latest'
    is_active_input: bool = True

    class Config:
        use_enum_values = True

    @root_validator
    def check_settings(cls, values: dict):
        if not (values['project_id'] and values['integration_uid']):
            return values
        project_id, integration_uid = values['project_id'], values['integration_uid']
        integration = AIProvider.get_integration(project_id, integration_uid)
        model_settings = values['model_settings']
        response = AIProvider.parse_settings(integration, model_settings)
        if not response['ok']:
            raise response['error']
        values['model_settings'] = response['item']
        return values


class PromptUpdateModel(PromptModel):
    id: int
    version: Optional[str]

class PromptUpdateNameModel(BaseModel):
    name: str

class PredictPostModel(BaseModel):
    input_: str = ''
    integration_uid: str
    integration_settings: Optional[dict] = {}
    prompt_id: Optional[int] = None
    project_id: Optional[int] = None
    examples: Optional[list] = []
    context: Optional[str] = ''
    variables: Optional[dict] = {}

    class Config:
        fields = {'input_': 'input'}

    @root_validator(pre=True, allow_reuse=True)
    def get_integration_uid(cls, values: dict):
        values['integration_uid'] = values.get('integration_uid') or values.get('integration_id')
        return values

    @root_validator
    def check_settings(cls, values: dict):
        if not (values['project_id'] and values['integration_uid']):
            return values
        project_id, integration_uid = values['project_id'], values['integration_uid']

        integration = AIProvider.get_integration(project_id, integration_uid)
        model_settings = values['integration_settings']
        response = AIProvider.parse_settings(integration, model_settings)

        if not response['ok']:
            error = response['error']
            # error_items = []
            # for error_item in error.errors():
            #     modified_loc = ('integration_settings',) + error_item['loc']
            #     error_item['loc'] = modified_loc
            #     error_items.append(error_items)

            # log.info(ValidationError(model=error.model, errors=error_items))
            # log.info(type(error))
            raise error
        
        values['integration_settings'] = response['item']
        return values