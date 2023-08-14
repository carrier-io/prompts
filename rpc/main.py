import re
import jinja2
from typing import Optional
from pylon.core.tools import log
from pylon.core.tools import web

from ..models.prompts import Prompt, Example, Variable
from tools import rpc_tools, db
from ..models.pd.prompts_pd import PromptModel, ExampleModel, PromptUpdateModel, \
    ExampleUpdateModel
from ..utils.ai_providers import AIProvider


class RPC:

    @web.rpc(f'prompts_get_all', "get_all")
    def prompts_get_all(self, project_id: int, **kwargs) -> list[dict]:
        with db.with_project_schema_session(project_id) as session:
            prompts = session.query(Prompt).all()
            return [prompt.to_json() for prompt in prompts]

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
                whole_settings = AIProvider.from_integration(
                    project_id, prompt.integration_id, prompt.model_settings
                ).settings
                if not isinstance(whole_settings, dict):
                    whole_settings = whole_settings.dict()
                result['model_settings'] = whole_settings
            result['examples'] = [example.to_json() for example in examples]
            result['variables'] = [var.to_json() for var in variables]
            return result

    @web.rpc(f'prompts_create', "create")
    def prompts_create(self, project_id: int, prompt: dict, **kwargs) -> dict:
        prompt = PromptModel.validate(prompt)
        with db.with_project_schema_session(project_id) as session:
            prompt = Prompt(**prompt.dict())
            session.add(prompt)
            session.commit()
            return prompt.to_json()

    @web.rpc(f'prompts_update', "update")
    def prompts_update(self, project_id: int, prompt: dict, **kwargs) -> bool:
        prompt = PromptUpdateModel.validate(prompt)
        with db.with_project_schema_session(project_id) as session:
            session.query(Prompt).filter(Prompt.id == prompt.id).update(
                prompt.dict(exclude={'id'}, exclude_none=True)
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
                                    input_: str, context: str = '', examples: list = (),
                                    **kwargs) -> str:
        text_prompt = ""
        prompt_template = '\ninput: {input}\noutput: {output}'
        if prompt_id:
            prompt = self.get_by_id(project_id, prompt_id)
            text_prompt += prompt['prompt']
            text_prompt = resolve_variables(project_id, prompt_id, text_prompt)
            if examples:
                prompt['examples'].extend(examples)
            if context:
                text_prompt += context
            for example in prompt['examples']:
                if not example['is_active']:
                    continue
                examples = prompt['examples']
        else:
            text_prompt += context
        for example in examples:
            text_prompt += prompt_template.format(**example)
        if input_:
            text_prompt += prompt_template.format(input=input_, output='')
        log.info(f"FINAL: {text_prompt}")
        return text_prompt
    

def resolve_variables(project_id, prompt_id, text_prompt):
    if not re.findall(r'\{\{.*?\}\}', text_prompt):
        return text_prompt

    with db.with_project_schema_session(project_id) as session:
        variables = session.query(Variable).filter(Variable.prompt_id == prompt_id)
        variables = {var.name: var.value for var in variables}

    try:
        environment = jinja2.Environment()
        template = environment.from_string(text_prompt)
        text_prompt = template.render(**variables)
    except:
        raise Exception("Invalid jinja template in context")
    return text_prompt