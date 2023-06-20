import json

import vertexai
from flask import request
from google.oauth2.service_account import Credentials
from pylon.core.tools import log
from vertexai.preview.language_models import TextGenerationModel

from ....integrations.models.pd.integration import SecretField
from tools import session_project, api_tools


def predict_large_language_model_sample(
        credentials: Credentials,
        project_id: str,
        model_name: str,
        temperature: float,
        max_decode_steps: int,
        top_p: float,
        top_k: int,
        content: str,
        location: str = "us-central1",
        tuned_model_name: str = "",
):
    """Predict using a Large Language Model."""
    vertexai.init(project=project_id, location=location, credentials=credentials)
    model = TextGenerationModel.from_pretrained(model_name)
    if tuned_model_name:
        model = model.get_tuned_model(tuned_model_name)

    response = model.predict(
        content,
        temperature=temperature,
        max_output_tokens=max_decode_steps,
        top_k=top_k,
        top_p=top_p,
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
        service_account = SecretField.parse_obj(settings['service_account_info'])
        service_info = json.loads(
            service_account.unsecret(project_id))
        credentials = Credentials.from_service_account_info(service_info)
        log.info(f'{settings=}')
        log.info(f'testing prompt {data} for project {project_id}')

        text_prompt = self.module.prepare_text_prompt(
            project_id, data["prompt_id"], data['input']
        )

        return predict_large_language_model_sample(
            credentials=credentials,
            project_id=settings['project'],
            model_name=settings['model_name'],
            temperature=settings['temperature'],
            max_decode_steps=settings['max_decode_steps'],
            top_p=settings['top_p'],
            top_k=settings['top_k'],
            content=text_prompt,
            location=settings['zone'],
            tuned_model_name=settings['tuned_model_name'],
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
