from flask import request
from pydantic import ValidationError
from pylon.core.tools import log

from tools import session_project, api_tools


class ProjectAPI(api_tools.APIModeHandler):

    def post(self, project_id):
        try:
            variable = self.module.create_variable(project_id, request.json)
            return variable, 201
        except ValidationError as e:
            return e.errors(), 400

    def put(self, project_id):
        try:
            variable = self.module.update_variable(project_id, request.json)
            return variable, 201
        except ValidationError as e:
            return e.errors(), 400

    def delete(self, project_id, variable_id):
        self.module.delete_variable(project_id, variable_id)
        return '', 204


class AdminAPI(api_tools.APIModeHandler):
    ...


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>',
        '<string:mode>/<int:project_id>/<int:variable_id>',
        '<int:project_id>',
        '<int:project_id>/<int:variable_id>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        'administration': AdminAPI,
    }