from typing import Optional, List

from pydantic import root_validator
from .prompts_pd import VertexAISettings, OpenAISettings, PromptModel
from pylon.core.tools import log


class ModelSettingsExport(VertexAISettings, OpenAISettings):
    class Config:
        fields = {
            'max_tokens': 'max_decode_steps',
            'max_decode_steps': {'exclude': True},
            'tuned_model_name': {'exclude': True},
            'model_name': {'exclude': True},
        }
        allow_population_by_field_name = True


class PromptExport(PromptModel):
    class Config:
        fields = {
            'context': 'prompt',
            'input': 'test_input',
            'prompt': {'exclude': True},
            'test_input': {'exclude': True},
            # 'integration_id': {'exclude': True},
        }
        orm_mode = True
        allow_population_by_field_name = True
    prompt: Optional[str] = None
    context: str
    input: str
    variables: List[dict] = []
    model_settings: ModelSettingsExport
    # integration_id: Optional[int] = None

    def dict_flat(self, **kwargs) -> dict:
        d = self.dict(**kwargs)
        if 'model_settings' in d:
            d.update(d.pop('model_settings'))
        return d


class PromptImport(PromptExport):
    model_settings: Optional[ModelSettingsExport] = {}

    @root_validator(pre=True)
    def set_model_settings(cls, values: dict) -> dict:
        # log.info('QWESDZ %s | %s', values)
        values['model_settings'] = ModelSettingsExport.parse_obj(values)
        # log.info('QWESDZ %s ', values['model_settings'])
        return values
