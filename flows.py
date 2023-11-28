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
)
def prompt(flow_context: dict, clean_data: dict, **kwargs):
    project_id = flow_context.get('project_id')
    # model_settings = data.integration_settings.dict(exclude={'project_id'}, exclude_unset=True)
    # model_settings = clean_data['integration_settings']
    # model_settings.pop('project_id', None)
    # integration_uid = clean_data['integration_uid']
    # input_ = clean_data['input_']
    # prompt_id = clean_data['prompt_id']
    # context = clean_data['context']
    # examples = clean_data['examples']
    # variables = clean_data['variables']

    # data = dict(kwargs)
    # data['input'] = data['prompt_input']
    # project_id = flow_context.get('project_id')
    # data['project_id'] = project_id
    # try:
    #     data = PredictPostModel.validate(data)
    # except ValidationError as e:
    #     log.error(e.errors())
    #     return {"ok": False, "error": e.errors()}
    # log.info('Prompt kwargs %s', kwargs)
    # log.info('Prompt node %s', data)
    #
    # if isinstance(data.integration_settings, dict):
    #     model_settings = data.integration_settings
    # else:
    #     model_settings = data.integration_settings.dict(exclude={'project_id'}, exclude_unset=True)

    log.info(clean_data)

    try:
        integration = AIProvider.get_integration(
            project_id=project_id,
            integration_uid=clean_data['integration_uid'],
        )
        prompt_struct = rpc_tools.RpcMixin().rpc.call.prompts_prepare_prompt_struct(
            project_id, clean_data['prompt_id'], clean_data['input_'],
            clean_data['context'], clean_data['examples'], clean_data['variables']
            # todo: handle ignore_template_error - maybe this need to be take from clean_data
        )
    except Exception as e:
        log.error(str(e))
        return {"ok": False, "error": str(e)}
    log.info(prompt_struct)
    output = AIProvider.predict(project_id, integration, clean_data['integration_settings'], prompt_struct)
    if not output['ok']:
        return output
    return {"ok": True, "result": output['response']}


@flow_tools.validator(flow_uid='prompt')
def prompt_validate(**kwargs) -> dict:
    kwargs['input'] = kwargs.pop('prompt_input')
    kwargs['integration_settings'] = kwargs.pop('model_settings')
    variables = kwargs.pop('variables')
    kwargs['variables'] = {}
    for var in variables:
        kwargs['variables'][var['name']] = var['value']
    result = PredictPostModel.parse_obj(kwargs)
    result.integration_settings.pop('service_account_info', None)
    result.integration_settings.pop('api_token', None)
    return result.dict()
