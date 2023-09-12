import re
from jinja2 import Environment, meta, DebugUndefined
from typing import Optional, List
from pylon.core.tools import web, log

from pydantic import parse_obj_as
from ..models.example import Example
from ..models.pd.example import ExampleModel, ExampleUpdateModel
from ..models.prompts import Prompt
from ..models.pd.prompts_pd import PromptModel, PromptUpdateModel
from ..models.variable import Variable
from ..utils.ai_providers import AIProvider
from traceback import format_exc
from tools import rpc_tools, db


class RPC:

    @web.rpc(f'prompts_get_all', "get_all")
    def prompts_get_all(self, project_id: int, **kwargs) -> list[dict]:
        with db.with_project_schema_session(project_id) as session:
            prompts = session.query(Prompt).order_by(Prompt.id.asc()).all()
            return [prompt.to_json() | {'tags': [tag.to_json() for tag in prompt.tags]} 
                    for prompt in prompts]

    @web.rpc("prompts_get_by_id", "get_by_id")
    def prompts_get_by_id(self, project_id: int, prompt_id: int, **kwargs) -> dict | None:
        with db.with_project_schema_session(project_id) as session:
            prompt = session.query(Prompt).filter(
                Prompt.id == prompt_id,
            ).one_or_none()
            if not prompt:
                return None
            examples = session.query(Example).filter(
                Example.prompt_id == prompt_id,
            ).all()

            variables = session.query(Variable).filter(
                Variable.prompt_id == prompt_id,
            ).all()

            result = prompt.to_json()
            if prompt.integration_id:
                whole_settings = AIProvider.get_integration_settings(
                    project_id, prompt.integration_id, prompt.model_settings
                )
                result['model_settings'] = whole_settings
            result['examples'] = [example.to_json() for example in examples]
            result['variables'] = [var.to_json() for var in variables]
            result['tags'] = [tag.to_json() for tag in prompt.tags]
            return result

    @web.rpc(f'prompts_create', "create")
    def prompts_create(self, project_id: int, prompt: dict, **kwargs) -> dict:
        prompt['project_id'] = project_id
        prompt = PromptModel.validate(prompt)
        with db.with_project_schema_session(project_id) as session:
            prompt = Prompt(**prompt.dict(exclude={'project_id'}))
            session.add(prompt)
            session.commit()
            return prompt.to_json()

    @web.rpc(f'prompts_update', "update")
    def prompts_update(self, project_id: int, prompt: dict, **kwargs) -> bool:
        prompt['project_id'] = project_id
        prompt = PromptUpdateModel.validate(prompt)
        with db.with_project_schema_session(project_id) as session:
            session.query(Prompt).filter(Prompt.id == prompt.id).update(
                prompt.dict(exclude={'id', 'project_id'}, exclude_none=True)
            )
            session.commit()
            updated_prompt = session.query(Prompt).get(prompt.id)
            return updated_prompt.to_json()

    @web.rpc(f'prompts_delete', "delete")
    def prompts_delete(self, project_id: int, prompt_id: int, **kwargs) -> bool:
        with db.with_project_schema_session(project_id) as session:
            prompt = session.query(Prompt).get(prompt_id)
            examples = session.query(Example).filter(Example.prompt_id == prompt_id).all()
            if prompt:
                session.delete(prompt)
            for example in examples:
                session.delete(example)

            session.commit()
            return True

    @web.rpc("prompts_get_examples_by_prompt_id", "get_examples_by_prompt_id")
    def prompts_get_examples_by_prompt_id(
            self, project_id: int, prompt_id: int, **kwargs
    ) -> list[dict]:
        with db.with_project_schema_session(project_id) as session:
            examples = session.query(Example).filter(Example.prompt_id == prompt_id).all()
            return [example.to_json() for example in examples]

    @web.rpc(f'prompts_create_example', "create_example")
    def prompts_create_example(self, project_id: int, example: dict, from_test_input: bool = False, **kwargs) -> dict:
        example = ExampleModel.validate(example)
        with db.with_project_schema_session(project_id) as session:
            example = Example(**example.dict())
            session.add(example)
            if from_test_input:
                session.query(Prompt).filter(Prompt.id == example.prompt_id).update(
                    {'test_input': None}
                )
            session.commit()
            return example.to_json()

    @web.rpc(f'prompts_create_examples_bulk', "create_examples_bulk")
    def prompts_create_examples_bulk(self, project_id: int, examples: List[dict], **kwargs) -> None:
        examples = parse_obj_as(List[ExampleModel], examples)
        with db.with_project_schema_session(project_id) as session:
            for i in examples:
                example = Example(**i.dict())
                session.add(example)
            session.commit()

    @web.rpc(f'prompts_update_example', "update_example")
    def prompts_update_example(self, project_id: int, example: dict, **kwargs) -> bool:
        example = ExampleUpdateModel.validate(example)
        with db.with_project_schema_session(project_id) as session:
            session.query(Example).filter(Example.id == example.id).update(
                example.dict(exclude={'id'}, exclude_none=True)
            )
            session.commit()
            updated_example = session.query(Example).get(example.id)
            return updated_example.to_json()

    @web.rpc(f'prompts_delete_example', "delete_example")
    def prompts_delete_example(self, project_id: int, example_id: int, **kwargs) -> bool:
        with db.with_project_schema_session(project_id) as session:
            example = session.query(Example).get(example_id)
            if example:
                session.delete(example)
                session.commit()
            return True

    @web.rpc(f'prompts_prepare_text_prompt', "prepare_text_prompt")
    def prompts_prepare_text_prompt(self, project_id: int, prompt_id: Optional[int],
                                    input_: str, context: str = '', examples: list = [],
                                    variables: dict = {},
                                    **kwargs) -> str:

        example_template = '\ninput: {input}\noutput: {output}'

        prompt_struct = {
            "context": context,
            "examples": examples,       # list of dicts {"input": "value", "output": "value"}
            "variables": variables,     # list of dicts {"var_name": "value"}
            "prompt": input_
        }
        if prompt_id:
            prompt_template = self.get_by_id(project_id, prompt_id)
            if not prompt_template:
                raise Exception(f"Prompt with id {prompt_id} in project {project_id} not found")
            prompt_struct['context'] = prompt_template['prompt'] + prompt_struct['context']
            for example in prompt_template['examples']:
                if not example['is_active']:
                    continue
                prompt_struct['examples'].append({
                    "input": example['input'],
                    "output": example['output']
                })
            for variable in prompt_template['variables']:
                if not prompt_struct['variables'].get(variable['name']):
                    prompt_struct['variables'][variable['name']] = variable['value']
            prompt_struct['variables']['prompt'] = prompt_struct['prompt']
        
        prompt_struct = resolve_variables(prompt_struct)

        for example in prompt_struct['examples']:
            prompt_struct['context'] += example_template.format(**example)

        if prompt_struct['prompt']:
            prompt_struct['context'] += example_template.format(input=prompt_struct['prompt'], output='')

        log.info(f"FINAL: {prompt_struct['context']}")
        return prompt_struct['context']


def resolve_variables(prompt_struct):
    try:
        environment = Environment(undefined=DebugUndefined)
        ast = environment.parse(prompt_struct['context'])
        if 'prompt' in set(meta.find_undeclared_variables(ast)):
            prompt_struct['prompt'] = ''
        template = environment.from_string(prompt_struct['context'])
        prompt_struct['context'] = template.render(**prompt_struct['variables'])
    except:
        log.critical(format_exc())
        raise Exception("Invalid jinja template in context")

    return prompt_struct
