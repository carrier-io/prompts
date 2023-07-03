from typing import Optional
from pylon.core.tools import log
from pylon.core.tools import web
from pydantic import parse_obj_as, ValidationError
from requests import HTTPError

from ..models.prompts import Prompt, Example
from tools import rpc_tools, db
from ..models.pd.prompts_pd import PromptModel, ExampleModel, PromptUpdateModel, \
    ExampleUpdateModel


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
            result = prompt.to_json()
            result['examples'] = [example.to_json() for example in examples]
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
    def prompts_create_example(self, project_id: int, example: dict, **kwargs) -> dict:
        example = ExampleModel.validate(example)
        with db.with_project_schema_session(project_id) as session:
            example = Example(**example.dict())
            session.add(example)
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
    def prompts_prepare_text_prompt(self, project_id: int, prompt_id: int, input_: str) -> str:
        prompt = self.get_by_id(project_id, prompt_id)

        text_prompt = ""
        text_prompt += prompt['prompt']

        for example in prompt['examples']:
            if not example['is_active']:
                continue
            text_prompt += f"""\ninput: {example['input']}\noutput: {example['output']}"""

        text_prompt += f"""\ninput: {input_}\n output:"""
        return text_prompt
