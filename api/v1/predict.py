from flask import request
from tools import api_tools

from ...models.pd.prompts_pd import PredictPostModel
from ...models.prompts import Prompt
from ...utils.ai_providers import AIProvider


from tools import rpc_tools, db


class ProjectAPI(api_tools.APIModeHandler):

    def post(self, project_id):
        data = PredictPostModel.parse_obj(request.json)
        if 'project_id' not in request.json:
            data.project_id = project_id

        with db.with_project_schema_session(project_id) as session:
            session.query(Prompt).filter(Prompt.id == data.prompt_id).update(
                dict(
                    model_settings=data.integration_settings,
                    test_input=data.input_,
                    integration_id=data.integration_id
                )
            )
            session.commit()

        ai_integration = AIProvider.from_integration(
            project_id=project_id,
            integration_id=data.integration_id,
            request_settings=data.integration_settings
        )
        # if data.input:
        text_prompt = self.module.prepare_text_prompt(
            project_id, **data.dict(
                exclude={'integration_settings'},
                exclude_unset=True,
                exclude_defaults=True
            )
        )

        # else:
        #     raise ValueError("No input provided")

        return ai_integration.predict(text_prompt)


class AdminAPI(api_tools.APIModeHandler):
    ...


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>',
        '<int:project_id>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        'administration': AdminAPI,
    }