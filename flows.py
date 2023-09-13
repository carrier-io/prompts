from pylon.core.tools import web, log
from pydantic import ValidationError

from tools import flow_tools, rpc_tools
from .models.pd.prompts_pd import PredictPostModel
from .utils.ai_providers import AIProvider


@flow_tools.flow(
    uid='prompt',
    display_name='Prompt',
    tooltip='AI Predict prompt',
    icon_url='/flows/static/icons/prompt.svg',
    # validation_rpc='embeddings_deduplicate_flow_validate'
)
def prompt(project_id: int, **kwargs):
    try:
        data = PredictPostModel.validate(kwargs)
    except ValidationError as e:
        log.error(e.errors())
        return {"ok": False, "error": e.errors()}

    model_settings = data.integration_settings
    try:
        integration = AIProvider.get_integration(
            project_id=project_id,
            integration_uid=data.integration_uid,
        )
        text_prompt = rpc_tools.RpcMixin().rpc.prompts_prepare_text_prompt(
            project_id, data.prompt_id, data.input_,
            data.context, data.examples, data.variables
        )
    except Exception as e:
        log.error(str(e))
        return {"ok": False, "error": str(e)}

    output = AIProvider.predict(project_id, integration, model_settings, text_prompt)
    return {"ok": True, "result": output}


@flow_tools.validator(flow_uid='prompt')
def prompt_validate(**kwargs):
    return PredictPostModel.validate(kwargs)