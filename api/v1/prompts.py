from flask import request
from pydantic import ValidationError
from pylon.core.tools import log

from tools import api_tools, auth, config as c


class ProjectAPI(api_tools.APIModeHandler):
    @auth.decorators.check_api({
        "permissions": ["models.prompts.prompts.list"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": False},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": False},
        }})
    def get(self, project_id):
        log.info('Getting all prompts for project %s', project_id)
        with_versions = request.args.get('versions', '').lower() == 'true'
        prompts = self.module.get_all(project_id, with_versions)

        return prompts

    @auth.decorators.check_api({
        "permissions": ["models.prompts.prompts.create"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": False},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": False},
        }})
    def post(self, project_id):
        try:
            prompt = self.module.create(project_id, request.json)
            return prompt, 201
        except ValidationError as e:
            return e.errors(), 400


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>',
        '<int:project_id>',
    ]

    mode_handlers = {
        c.DEFAULT_MODE: ProjectAPI,
    }
