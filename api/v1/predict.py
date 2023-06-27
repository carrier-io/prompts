import json

from flask import request
from pylon.core.tools import log

from ....integrations.models.pd.integration import SecretField
from tools import session_project, api_tools


def predict_openai(
        content: str,
        project_id: int,
        model_settings: dict,
):
    import openai
    api_key = SecretField.parse_obj(model_settings['api_token']).unsecret(project_id)
    openai.api_key = api_key
    response = openai.Completion.create(
        model=model_settings['model_name'],
        prompt=content,
        temperature=model_settings['temperature'],
        max_tokens=model_settings['max_tokens'],
        top_p=model_settings['top_p'],
    )
    log.info(f"{response=}")
    return response['choices'][0]['text']


def predict_large_language_model_sample(
        content: str,
        project_id: int,
        model_settings: dict,
):
    import vertexai
    from google.oauth2.service_account import Credentials
    from vertexai.preview.language_models import TextGenerationModel

    service_account = SecretField.parse_obj(model_settings['service_account_info'])
    log.info(f"{service_account=} {project_id=} {model_settings=}")
    service_info = json.loads(service_account.unsecret(project_id))
    log.info(f"{service_info=}")
    credentials = Credentials.from_service_account_info(service_info)
    """Predict using a Large Language Model."""
    log.info(f"{model_settings['project']=} {model_settings['zone']=} {credentials=}")
    vertexai.init(
        project=model_settings['project'],
        location=model_settings['zone'],
        credentials=credentials
    )
    model = TextGenerationModel.from_pretrained(model_settings['model_name'])
    if model_settings['tuned_model_name']:
        model = model.get_tuned_model(model_settings['tuned_model_name'])

    response = model.predict(
        content,
        temperature=model_settings['temperature'],
        max_output_tokens=model_settings['max_decode_steps'],
        top_k=model_settings['top_k'],
        top_p=model_settings['top_p'],
    )
    log.info(f"Response from Model: {response.text}")
    return response.text


class ProjectAPI(api_tools.APIModeHandler):

    def post(self, project_id):
        data = request.json
        integration = self.module.context.rpc_manager.call.integrations_get_by_id(
            project_id,
            data["integration_id"]
        )
        settings = integration.settings
        request_settings = data.get('integration_settings', {})
        log.info(f'{settings=} {request_settings=}')
        log.info(f'testing prompt {data} for project {project_id}')

        text_prompt = self.module.prepare_text_prompt(
            project_id, data["prompt_id"], data['input']
        )
        model_settings = {**settings, **request_settings}
        log.info(f'{model_settings=}')
        if integration.name == 'open_ai':
            return predict_openai(
                text_prompt,
                project_id=project_id,
                model_settings=model_settings
            )
        elif integration.name == 'vertex_ai':
            return predict_large_language_model_sample(
                text_prompt,
                project_id=project_id,
                model_settings=model_settings
            )


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
