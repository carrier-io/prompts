from flask import request
from tools import api_tools
from pylon.core.tools import log

from ...models.pd.prompts_pd import PredictPostModel
from ...models.prompts import Prompt
from ...utils.ai_providers import AIProvider


from tools import db

from pylon.core.tools import log


class ProjectAPI(api_tools.APIModeHandler):
    @api_tools.endpoint_metrics
    def post(self, project_id):
        payload = request.json
        payload['project_id'] = project_id
        try:
            data = PredictPostModel.parse_obj(payload)
        except Exception as e:
            return {"error": str(e)}, 400
        model_settings = data.integration_settings.dict(exclude={'project_id'}, exclude_unset=True)
        with db.with_project_schema_session(project_id) as session:
            session.query(Prompt).filter(Prompt.id == data.prompt_id).update(
                dict(
                    model_settings=model_settings,
                    test_input=data.input_,
                    integration_uid=data.integration_uid
                )
            )
            session.commit()

        try:
            integration = AIProvider.get_integration(
                project_id=project_id,
                integration_uid=data.integration_uid,
            )
            text_prompt = self.module.prepare_text_prompt(
                project_id, data.prompt_id, data.input_, 
                data.context, data.examples, data.variables
            )
        except Exception as e:
            return str(e), 400

        result = AIProvider.predict(project_id, integration, model_settings, text_prompt)
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
