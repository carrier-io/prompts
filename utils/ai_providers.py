import json
from abc import ABC, abstractmethod

from ..models.pd.prompts_pd import VertexAIIntegrationSettings, OpenAIIntegrationSettings
from ...integrations.models.pd.integration import SecretField
from tools import rpc_tools
from pylon.core.tools import log


class AiIntegration(ABC):

    def __init__(self, project_id: int, integration_settings: dict):
        self.project_id = project_id
        self.settings: dict | VertexAIIntegrationSettings | OpenAIIntegrationSettings = \
            self.format_settings(integration_settings)

    def format_settings(self, integration_settings: dict):
        return integration_settings

    @abstractmethod
    def predict(self, content: str) -> str:
        pass


class OpenAiIntegration(AiIntegration):
    def format_settings(self, integration_settings: dict) -> OpenAIIntegrationSettings:
        return OpenAIIntegrationSettings.parse_obj(integration_settings)

    def predict(self, content: str) -> str:
        import openai
        api_key = SecretField.parse_obj(self.settings.api_token).unsecret(self.project_id)
        openai.api_key = api_key
        response = openai.Completion.create(
            model=self.settings.model_name,
            prompt=content,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            top_p=self.settings.top_p,
        )
        log.info(f"{response=}")
        return response['choices'][0]['text']


class VertexAiIntegration(AiIntegration):
    def format_settings(self, integration_settings: dict) -> VertexAIIntegrationSettings:
        return VertexAIIntegrationSettings.parse_obj(integration_settings)

    def predict(self, content: str) -> str:
        import vertexai
        from google.oauth2.service_account import Credentials
        from vertexai.preview.language_models import TextGenerationModel

        service_account = SecretField.parse_obj(self.settings.service_account_info)
        log.info(f"{service_account=} {self.project_id=} {self.settings=}")
        service_info = json.loads(service_account.unsecret(self.project_id))
        log.info(f"{service_info=}")
        credentials = Credentials.from_service_account_info(service_info)
        """Predict using a Large Language Model."""
        log.info(f"{self.settings.project=} {self.settings.zone=} {credentials=}")
        vertexai.init(
            project=self.settings.project,
            location=self.settings.zone,
            credentials=credentials
        )
        model = TextGenerationModel.from_pretrained(self.settings.model_name)
        if self.settings.tuned_model_name:
            model = model.get_tuned_model(self.settings.tuned_model_name)

        response = model.predict(
            content,
            temperature=self.settings.temperature,
            max_output_tokens=self.settings.max_decode_steps,
            top_k=self.settings.top_k,
            top_p=self.settings.top_p,
        )
        log.info(f"Response from Model: {response.text}")
        return response.text


class AIProvider:

    @classmethod
    def from_integration(
            cls, project_id: int, integration_id: int, request_settings: dict
    ) -> AiIntegration:
        integration = rpc_tools.RpcMixin().rpc.call.integrations_get_by_id(
            project_id,
            integration_id
        )
        settings = {**integration.settings, **request_settings}
        if integration.name == 'open_ai':
            return OpenAiIntegration(project_id, settings)
        elif integration.name == 'vertex_ai':
            return VertexAiIntegration(project_id, settings)
        else:
            raise NotImplementedError(f"Integration {integration.name} not implemented")


# class AIProvider(rpc_tools.RpcMixin):
#     ai_class_map = {
#         'open_ai': OpenAiIntegration,
#         'vertex_ai': VertexAiIntegration
#     }
#
#     def __init__(self, project_id: int, integration_id: int, request_settings: dict | None = None):
#         self.project_id = project_id
#         self.integration_id = integration_id
#         self.request_settings = request_settings or dict()
#
#         self.integration = self.rpc.call.integrations_get_by_id(
#             project_id,
#             integration_id
#         )
#
#         assert self.integration.name in self.ai_class_map.keys(), NotImplementedError(
#             f"Integration {self.integration.name} not implemented"
#         )
#
#         self.merged_settings = self.integration.settings
#         self.merged_settings.update(self.request_settings)
#
#         self._ai_class = None
#
#     @property
#     def ai_class(self) -> AiIntegration:
#         if not self._ai_class:
#             self._ai_class = self.ai_class_map[self.integration.name](
#                 project_id=self.project_id,
#                 integration_settings=self.integration.settings
#             )
#         return self._ai_class
#
#     # @classmethod
#     # def from_integration(
#     #         cls, project_id: int, integration_id: int, request_settings: dict
#     # ) -> AiIntegration:
#
#     def __getattr__(self, item):
#         log.info('GETATTR %s', item)
#         try:
#             return self.__dict__[item]
#         except KeyError:
#             return getattr(self.ai_class, item)
#
#     # def format_settings(self, integration_settings: dict):
#     #     return self.ai_class.format_settings(integration_settings)
#     #
#     # def predict(self, content: str) -> str:
#     #     return self.ai_class.predict(content)

