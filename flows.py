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
def prompt(flow_context: dict, clean_data: dict, **kwargs):
    project_id = flow_context.get('project_id')
    # model_settings = data.integration_settings.dict(exclude={'project_id'}, exclude_unset=True)
    model_settings = clean_data['integration_settings']
    model_settings.pop('project_id', None)
    integration_uid = clean_data['integration_uid']
    input_ = clean_data['input_']
    prompt_id = clean_data['prompt_id']
    context = clean_data['context']
    examples = clean_data['examples']
    variables = clean_data['variables']
    
    try:
        integration = AIProvider.get_integration(
            project_id=project_id,
            integration_uid=integration_uid,
        )
        text_prompt = rpc_tools.RpcMixin().rpc.call.prompts_prepare_text_prompt(
            project_id, prompt_id, input_,
            context, examples, variables
        )
    except Exception as e:
        log.error(str(e))
        return {"ok": False, "error": str(e)}

    output = AIProvider.predict(project_id, integration, model_settings, text_prompt)
    if not output['ok']:
        return output
    return {"ok": True, "result": output['response']}


@flow_tools.validator(flow_uid='prompt')
def prompt_validate(**kwargs):
    return PredictPostModel.validate(kwargs)
