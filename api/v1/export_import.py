from itertools import chain
from typing import Optional, Literal, List

from flask import request
from pydantic import ValidationError, BaseModel, parse_obj_as
from pylon.core.tools import log

from tools import api_tools, db

from sqlalchemy.exc import IntegrityError
from ...models.example import Example
from ...models.pd.example import ExampleModel
from ...models.pd.export_import import PromptExport, PromptImport
from ...models.pd.prompts_pd import VertexAISettings, OpenAISettings
from ...models.pd.variable import VariableModel
from ...models.prompts import Prompt
from ...models.variable import Variable
from ...utils.ai_providers import AIProvider


class ProjectAPI(api_tools.APIModeHandler):
    def get(self, project_id: int, prompt_id: int, **kwargs):
        # struct = {
        #     'prompt': None,
        #     'examples': []
        # }
        with db.with_project_schema_session(project_id) as session:
            prompt = session.query(Prompt).filter(
                Prompt.id == prompt_id,
            ).one_or_none()
            if not prompt:
                return {'error': f'Prompt with id: {prompt_id} not found'}, 400
            # struct['prompt'] = prompt.to_json()
            result = PromptExport.from_orm(prompt).dict_flat(
                exclude_unset=True, by_alias=False, exclude={'integration_id'}
            )
            examples = session.query(Example).filter(
                Example.prompt_id == prompt_id,
            ).all()
            # result['examples'] = [i.to_json(exclude_fields={'id', 'prompt_id'}) for i in examples]
            result['examples'] = [
                ExampleModel.from_orm(i).dict(exclude={'id', 'prompt_id'})
                for i in examples
            ]
            variables = session.query(Variable).filter(
                Variable.prompt_id == prompt_id,
            ).all()
            # result['variables'] = [i.to_json(exclude_fields={'id', 'prompt_id'}) for i in variables]
            result['variables'] = [
                VariableModel.from_orm(i).dict(exclude={'id', 'prompt_id'})
                for i in variables
            ]
            return result

    def post(self, project_id: int, **kwargs):
        try:
            integration_id = request.json['integration_id']
        except KeyError:
            return {'error': 'integration_id is required in body'}, 400

        examples = request.json.pop('examples', [])
        variables = request.json.pop('variables', [])
        prompt_data = PromptImport.parse_obj(request.json)

        integration = self.module.context.rpc_manager.call.integrations_get_by_id(
            project_id,
            integration_id
        )
        if integration.name == 'vertex_ai':
            model_settings = prompt_data.model_settings.dict(
                exclude_unset=True, by_alias=True
            )
            log.info('settings to parse %s will be: %s', integration.name, model_settings)
            settings = VertexAISettings.parse_obj(model_settings)
        elif integration.name == 'open_ai':
            model_settings = prompt_data.model_settings.dict(
                exclude_unset=True, by_alias=False
            )
            log.info('settings to parse %s will be: %s', integration.name, model_settings)
            settings = OpenAISettings.parse_obj(model_settings)
        else:
            err_msg = f'Integration of type: {integration.name} could not be parsed'
            log.critical(err_msg)
            return {'error': err_msg}, 400
        log.info('settings parse result: %s', settings.dict())

        prompt_dict = prompt_data.dict(exclude_unset=False, by_alias=True, exclude={'model_settings'})
        prompt_dict['model_settings'] = settings.dict()
        # result = {
        #     'examples': examples,
        # }

        if request.json.get('skip'):
            return {
                'examples': examples,
                'variables': variables,
                **prompt_dict
            }, 200

        try:
            p = self.module.create(project_id=project_id, prompt=prompt_dict)
        except IntegrityError:
            return {'error': f'Prompt name \'{prompt_dict["name"]}\' already exists'}, 400

        # self.module.create_example(project_id, request.json, from_test_input=from_test_input)
        for i in chain(examples, variables):
            i['prompt_id'] = p['id']
        self.module.create_examples_bulk(project_id=project_id, examples=examples)
        self.module.create_variables_bulk(project_id=project_id, variables=variables)
        # result.update(p)
        return self.module.get_by_id(project_id, p['id']), 201


# class AdminAPI(api_tools.APIModeHandler):
#     ...


class API(api_tools.APIBase):
    url_params = [
        '<int:project_id>/<int:prompt_id>',
        '<string:mode>/<int:project_id>/<int:prompt_id>',
        '<int:project_id>',
        '<string:mode>/<int:project_id>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        # 'administration': AdminAPI,
    }
