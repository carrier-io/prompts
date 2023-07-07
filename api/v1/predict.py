from flask import request

from flask import request

from tools import api_tools
from ...utils.ai_providers import AIProvider


class ProjectAPI(api_tools.APIModeHandler):

    def post(self, project_id):
        data = request.json
        request_settings = data.get('integration_settings', {})

        ai_integration = AIProvider.from_integration(
            project_id=data["project_id"],
            integration_id=data["integration_id"],
            request_settings=request_settings
        )
        if text_input := data.get('input'):
            text_prompt = self.module.prepare_text_prompt(
                project_id, data.get("prompt_id", None), 
                text_input, data.get('context', ""), data.get('examples', [])
            )
        else:
            raise ValueError("No input provided")

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
