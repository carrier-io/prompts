from flask import request

from flask import request

from tools import api_tools
from ...utils.ai_providers import AIProvider


class ProjectAPI(api_tools.APIModeHandler):

    def post(self, project_id):
        data = request.json
        request_settings = data.get('integration_settings', {})

        ai_integration = AIProvider.from_integration(
            project_id=project_id,
            integration_id=data["integration_id"],
            request_settings=request_settings
        )
        if text_input := data.get('input'):
            text_prompt = self.module.prepare_text_prompt(
                project_id, data["prompt_id"], text_input
            )
        elif full_context := data.get('context'):
            text_prompt = full_context
        else:
            raise ValueError("No input or context provided")

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
