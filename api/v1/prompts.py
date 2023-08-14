from flask import request
from pydantic import ValidationError
from pylon.core.tools import log

from tools import session_project, api_tools


class ProjectAPI(api_tools.APIModeHandler):

    def get(self, project_id):
        log.info('Getting all prompts for project %s', project_id)
        prompts = self.module.get_all(project_id)

        return prompts

    def post(self, project_id):
        try:
            prompt = self.module.create(project_id, request.json)
            return prompt, 201
        except ValidationError as e:
            return e.errors(), 400


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
