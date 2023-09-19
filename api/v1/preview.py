from tools import api_tools


class ProjectAPI(api_tools.APIModeHandler):

    def get(self, project_id, prompt_id):
        prompt_struct = self.module.prepare_prompt_struct(
            project_id, prompt_id, ""
        )
        return prompt_struct


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
