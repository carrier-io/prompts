from typing import Optional
from pylon.core.tools import log
from pylon.core.tools import web
from pydantic import parse_obj_as, ValidationError
from ..models.prompts import Prompt, Example
from tools import rpc_tools, db
from ..models.pd.prompts_pd import PromptModel, ExampleModel


class RPC:

    @web.rpc(f'prompts_get_all', "get_all")
    def prompts_get_all(self, project_id: int, **kwargs) -> list[dict]:
        with db.with_project_schema_session(project_id) as session:
            prompts = session.query(Prompt).all()
            return [prompt.dict() for prompt in prompts]

    @web.rpc("prompts_get_by_id", "get_by_id")
    def prompts_get_by_id(self, project_id: int, prompt_id: int, **kwargs) -> dict:
        with db.with_project_schema_session(project_id) as session:
            prompt = session.query(Prompt, Example).filter(
                Prompt.id == prompt_id,
                Prompt.id == Example.prompt_id
            ).all()
            return prompt.dict()

    @web.rpc(f'prompts_create', "create")
    @rpc_tools.wrap_exceptions(ValidationError)
    def prompts_create(self, project_id: int, prompt: dict, **kwargs) -> dict:
        prompt = PromptModel.validate(prompt)
        with db.with_project_schema_session(project_id) as session:
            prompt = Prompt(**prompt.dict())
            session.add(prompt)
            session.commit()
            return prompt.dict()

    @web.rpc(f'prompts_update', "update")
    @rpc_tools.wrap_exceptions(ValidationError)
    def prompts_update(self, project_id: int, prompt: dict, **kwargs) -> dict:
        prompt = PromptModel.validate(prompt)
        with db.with_project_schema_session(project_id) as session:
            prompt = session.query(Prompt).get(prompt['id'])
            prompt.update(**prompt)
            session.commit()
            return prompt.dict()

    @web.rpc(f'prompts_delete', "delete")
    @rpc_tools.wrap_exceptions(ValidationError)
    def prompts_delete(self, project_id: int, prompt_id: int, **kwargs) -> bool:
        with db.with_project_schema_session(project_id) as session:
            prompt = session.query(Prompt).get(prompt_id)
            session.delete(prompt)
            session.commit()
            return True

    @web.rpc("prompts_get_examples_by_prompt_id", "get_examples_by_prompt_id")
    def prompts_get_examples_by_prompt_id(
            self, project_id: int, prompt_id: int, **kwargs
    ) -> list[dict]:
        with db.with_project_schema_session(project_id) as session:
            examples = session.query(Example).filter(Example.prompt_id == prompt_id).all()
            return [example.dict() for example in examples]

    @web.rpc(f'prompts_create_example', "create_example")
    @rpc_tools.wrap_exceptions(ValidationError)
    def prompts_create_example(self, project_id: int, example: dict, **kwargs) -> dict:
        example = ExampleModel.validate(example)
        with db.with_project_schema_session(project_id) as session:
            session.query(Prompt).get_or_404(example['prompt_id'])
            example = Example(**example)
            session.add(example)
            session.commit()
            return example.dict()

    @web.rpc(f'prompts_update_example', "update_example")
    @rpc_tools.wrap_exceptions(ValidationError)
    def prompts_update_example(self, project_id: int, example: dict, **kwargs) -> dict:
        example = ExampleModel.validate(example)
        with db.with_project_schema_session(project_id) as session:
            example = session.query(Example).get(example.id)
            example.update(**example)
            session.commit()
            return example.dict()

    @web.rpc(f'prompts_delete_example', "delete_example")
    @rpc_tools.wrap_exceptions(ValidationError)
    def prompts_delete_example(self, project_id: int, example_id: int, **kwargs) -> bool:
        with db.with_project_schema_session(project_id) as session:
            example = session.query(Example).get(example_id)
            session.delete(example)
            session.commit()
            return True
