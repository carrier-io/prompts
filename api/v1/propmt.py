from math import floor

from flask import request
from flask_restful import Resource
from pydantic import ValidationError
from pylon.core.tools import log

from tools import session_project, api_tools


class ProjectAPI(api_tools.APIModeHandler):
    ...


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

    def get(self, project_id, prompt_id):
        prompt = self.module.get_by_id(project_id, prompt_id)
        return prompt

    def put(self, project_id):
        try:
            prompt = self.module.update(project_id, **request.json)
            return prompt, 201
        except ValidationError as e:
            return e.errors(), 400

    def delete(self, project_id, prompt_id):
        self.module.delete(project_id, prompt_id)
        return '', 204
