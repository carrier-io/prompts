from flask import request
from tools import api_tools


class ProjectAPI(api_tools.APIModeHandler):

    def get(self, project_id: int, prompt_id: int):
        ignore_template_error = request.args.get('ignore_template_error', False)
        text_prompt = self.module.prepare_text_prompt(
            project_id, prompt_id, "",
            ignore_template_error=ignore_template_error
        )
        return text_prompt, 200


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
