from itertools import groupby

from flask import request, g
from pydantic import ValidationError
from pylon.core.tools import log

from tools import session_project, api_tools


class ProjectAPI(api_tools.APIModeHandler):

    def get(self, project_id: int, file_name: str, **kwargs):
        project = self.module.context.rpc_manager.call.project_get_or_404(project_id=project_id)
        s3_settings = test_data['test_config'].get(
            'integrations', {}).get('system', {}).get('s3_integration', {})
        minio_client = MinioClient(project, **s3_settings)
        bucket_name = str(test_data["name"]).replace("_", "").replace(" ", "").lower()
        try:
            file = minio_client.download_file(bucket_name, filename)
            try:
                return send_file(BytesIO(file), attachment_filename=filename)
            except TypeError:  # new flask
                return send_file(BytesIO(file), download_name=filename, as_attachment=True)
        except:
            abort(404)

    # def put(self, project_id: int, **kwargs):
    #     # used to regenerate token from ui
    #     token = self.module.regenerate_token(user_id=g.auth.id)
    #     return {'token': token}, 200


# class AdminAPI(api_tools.APIModeHandler):
#     ...


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>',
        '<int:project_id>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        # 'administration': AdminAPI,
    }
