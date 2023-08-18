from flask import request
from tools import api_tools

from ...models.pd.prompts_pd import PredictPostModel
from ...models.prompts import Prompt
from ...utils.ai_providers import AIProvider


from tools import db


class ProjectAPI(api_tools.APIModeHandler):

    def post(self, project_id):
        data = PredictPostModel.parse_obj(request.json)

        with db.with_project_schema_session(project_id) as session:
            session.query(Prompt).filter(Prompt.id == data.prompt_id).update(
                dict(
                    model_settings=data.integration_settings,
                    test_input=data.input_,
                    integration_id=data.integration_id
                )
            )
            session.commit()

        project_id = request.json.get('project_id', project_id)

        try:
            integration = AIProvider.get_integration(
                project_id=project_id,
                integration_id=data.integration_id,
            )
            text_prompt = self.module.prepare_text_prompt(
                project_id, data.prompt_id, data.input_, 
                data.context, data.examples, data.variables
            )
        except Exception as e:
            return str(e), 400

        result = AIProvider.predict(project_id, integration, data.integration_settings, text_prompt)
        if not result['ok']:
            return str(result['error']), 400
        return result['response'], 200

# class AdminAPI(api_tools.APIModeHandler):
#     ...


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>',
        '<int:project_id>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        # 'administration': AdminAPI,
    }