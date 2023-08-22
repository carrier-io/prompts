from tools import rpc_tools
from pylon.core.tools import log


class IntegrationNotFound(Exception):
    "Raised when integration is not found"


class AIProvider:
    rpc = rpc_tools.RpcMixin().rpc.call

    @classmethod
    def get_integration_settings(
        cls, project_id: int, integration_id: int, prompt_settings: dict
    ) -> dict:
        try:
            integration = cls.get_integration(project_id, integration_id)
        except IntegrationNotFound as e:
            log.error(str(e))
            return {}
        return {**integration.settings, **prompt_settings}

    @classmethod
    def get_integration(cls, project_id: int, integration_id: int):
        integration = cls.rpc.integrations_get_by_id(
            project_id,
            integration_id
        )
        if integration is None:
            raise IntegrationNotFound(
                f"Integration is not found when project_id={project_id}, integration_id={integration_id}"
            )
        return integration

    @classmethod
    def _get_rpc_function(cls, integration_name, suffix="__predict"):
        rpc_name = integration_name + suffix
        rpc_func = getattr(cls.rpc, rpc_name)
        return rpc_func

    @classmethod
    def predict(cls, project_id: int, integration, request_settings: dict, text_prompt: str):
        rpc_func = cls._get_rpc_function(integration.name)
        settings = {**integration.settings, **request_settings}
        result = rpc_func(project_id, settings, text_prompt)
        return result

    @classmethod
    def parse_settings(cls, integration, settings):
        rpc_func = cls._get_rpc_function(integration.name, "__parse_settings")
        return rpc_func(settings)
