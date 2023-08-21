from flask_restful import Resource

from pylon.core.tools import log


class API(Resource):
    url_params = [
        '<int:project_id>',
    ]

    def __init__(self, module):
        self.module = module

    def get(self, project_id: int):
        prompts = self.module.get_all(project_id)
        all_tags = set()
        for prompt in prompts:
            all_tags.update(tag for tag in prompt.tags)

        return {"tags": all_tags}, 200
