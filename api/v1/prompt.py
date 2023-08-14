from flask import request
from pydantic import ValidationError
from pylon.core.tools import log

from tools import session_project, api_tools


class ProjectAPI(api_tools.APIModeHandler):

    def get(self, project_id, prompt_id):
        prompt = self.module.get_by_id(project_id, prompt_id)
        if not prompt:
            return 'Prompt not found', 404
        return prompt

    def put(self, project_id):
        try:
            prompt = self.module.update(project_id, request.json)
            return prompt, 201
        except ValidationError as e:
            return e.errors(), 400

    def delete(self, project_id, prompt_id):
        self.module.delete(project_id, prompt_id)
        return '', 204


class AdminAPI(api_tools.APIModeHandler):
    ...


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>',
        '<string:mode>/<int:project_id>/<int:prompt_id>',
        '<int:project_id>',
        '<int:project_id>/<int:prompt_id>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        'administration': AdminAPI,
    }
