from flask_restful import Resource
from flask import request

from pylon.core.tools import log
from tools import api_tools


class ProjectAPI(api_tools.APIModeHandler):

    def get(self, project_id, prompt_id=None):
        if prompt_id:
            return self.module.get_tags(project_id, prompt_id), 200
        return self.module.get_all_tags(project_id), 200

    def put(self, project_id, prompt_id):  # pylint: disable=R0201
        tags = request.json
        resp = self.module.update_tags(project_id, prompt_id, tags)
        return resp, 200


class AdminAPI(api_tools.APIModeHandler):
    ...


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>',
        '<int:project_id>',
        '<string:mode>/<int:project_id>/<int:prompt_id>',
        '<int:project_id>/<int:prompt_id>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        'administration': AdminAPI,
    }
