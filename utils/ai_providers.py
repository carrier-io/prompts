from tools import rpc_tools
from pylon.core.tools import log


class IntegrationNotFound(Exception):
    "Raised when integration is not found"


class AIProvider:
    rpc = rpc_tools.RpcMixin().rpc.call

    @classmethod
    def get_integration_settings(
        cls, project_id: int, integration_uid: str, prompt_settings: dict
    ) -> dict:
        try:
            integration = cls.get_integration(project_id, integration_uid)
        except IntegrationNotFound as e:
            log.error(str(e))
            return None
        return {**integration.settings, **prompt_settings}

    @classmethod
    def get_integration(cls, project_id: int, integration_uid: str):
        integration = cls.rpc.integrations_get_by_uid(
            integration_uid=integration_uid,
            project_id=project_id,
            check_all_projects=False
        )
        if integration is None:
            raise IntegrationNotFound(
                f"Integration is not found when project_id={project_id}, integration_uid={integration_uid}"
            )
        return integration

    @classmethod
    def _get_rpc_function(cls, integration_name, suffix="__predict"):
        rpc_name = integration_name + suffix
        rpc_func = getattr(cls.rpc, rpc_name)
        return rpc_func

    @classmethod
    def predict(cls, project_id: int, integration, request_settings: dict, prompt_struct: dict):
        rpc_func = cls._get_rpc_function(integration.name)
        settings = {**integration.settings, **request_settings}
        result = rpc_func(project_id, settings, prompt_struct)
        return result

    @classmethod
    def parse_settings(cls, integration, settings):
        rpc_func = cls._get_rpc_function(integration.name, "__parse_settings")
        return rpc_func(settings)
