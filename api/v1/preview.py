from flask import request

from flask import request

from tools import api_tools
from ...utils.ai_providers import AIProvider


class ProjectAPI(api_tools.APIModeHandler):

    def get(self, project_id, prompt_id):
        text_prompt = self.module.prepare_text_prompt(
            project_id, prompt_id, ""
        )
        return text_prompt


class AdminAPI(api_tools.APIModeHandler):
    ...


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>/<int:prompt_id>',
        '<int:project_id>/<int:prompt_id>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        'administration': AdminAPI,
    }
