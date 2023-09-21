from flask import request
from flask import request
from tools import api_tools


class ProjectAPI(api_tools.APIModeHandler):

    def get(self, project_id: int, prompt_id: int):
        ignore_template_error = request.args.get('ignore_template_error', False)
        prompt_struct = self.module.prepare_prompt_struct(
            project_id, prompt_id, "",
            ignore_template_error=ignore_template_error
        )
        return prompt_struct, 200


# class AdminAPI(api_tools.APIModeHandler):
#     ...


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>/<int:prompt_id>',
        '<int:project_id>/<int:prompt_id>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        # 'administration': AdminAPI,
    }
