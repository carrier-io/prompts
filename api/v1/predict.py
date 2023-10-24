from flask import request
from tools import api_tools
from pylon.core.tools import log
import tiktoken
from ...models.pd.prompts_pd import PredictPostModel
from ...models.prompts import Prompt
from ...utils.ai_providers import AIProvider
from traceback import format_exc

from tools import db, auth, config as c

from pylon.core.tools import log

# TODO add more models or find an API to get tokens limit
MODEL_TOKENS_MAPPER = {
    "text-davinci-003": 4097,
    "text-davinci-002": 4097
}


class ProjectAPI(api_tools.APIModeHandler):
    @auth.decorators.check_api({
        "permissions": ["models.prompts.predict.post"],
        "recommended_roles": {
            c.ADMINISTRATION_MODE: {"admin": True, "editor": True, "viewer": False},
            c.DEFAULT_MODE: {"admin": True, "editor": True, "viewer": False},
        }})
    @api_tools.endpoint_metrics
    def post(self, project_id: int):
        payload = dict(request.json)
        log.info("payload **************")
        log.info(payload)
        ignore_template_error = payload.pop('ignore_template_error', False)
        update_prompt = payload.pop('update_prompt', False)
        payload['project_id'] = project_id
        try:
            data = PredictPostModel.parse_obj(payload)
        except Exception as e:
            log.error("************* data = PredictPostModel.parse_obj(payload)")
            log.error(str(e))
            log.info(str(format_exc()))
            log.error("*************")
            return {"error": str(e)}, 400
        model_settings = data.integration_settings.dict(exclude={'project_id'})
        if update_prompt:
            with db.with_project_schema_session(project_id) as session:
                session.query(Prompt).filter(Prompt.id == data.prompt_id).update(
                    dict(
                        model_settings=model_settings,
                        test_input=data.input_,
                        integration_uid=data.integration_uid
                    )
                )
                session.commit()

        _input = data.input_
        prompt = self.module.get_by_id(project_id, data.prompt_id)
        if prompt:
            _context = prompt["prompt"]
            embedding = prompt.get("embeddings", {})
            if embedding:
                embedding["top_k"] = payload.get("embedding_settings", {}).get("top_k", 20)
                embedding["cutoff"] = payload.get("embedding_settings", {}).get("cutoff", 0.1)
        else:
            _context = data.context
            embedding = {}

        if payload.get("embedding"):
            embedding = payload.get("embedding")

        try:
            if embedding:
                model_name = model_settings["model_name"]
                encoding = tiktoken.encoding_for_model(model_name)
                max_tokens = MODEL_TOKENS_MAPPER.get(model_name, 4000)
                tokens_for_completion = model_settings["max_tokens"]
                tokens_for_context = max_tokens - tokens_for_completion
                results_list = self.module.context.rpc_manager.call.embeddings_similarity_search(project_id,
                                                                                                 embedding["id"],
                                                                                                 _input,
                                                                                                 embedding["top_k"],
                                                                                                 embedding["cutoff"])
                for item in results_list:
                    if len(encoding.encode(item + _context)) <= tokens_for_context:
                        _context += item
                    else:
                        break
                tokens_for_context = len(encoding.encode(_context))
                total_tokens = tokens_for_context + tokens_for_completion
                log.info(f"total_tokens = {total_tokens}")
        except Exception as e:
            log.error(str(e))
            log.info(str(format_exc()))
            log.error("Failed to append embedding to the context")
        try:
            integration = AIProvider.get_integration(
                project_id=project_id,
                integration_uid=data.integration_uid,
            )
            prompt_struct = self.module.prepare_prompt_struct(
                project_id, data.prompt_id, _input,
                _context, data.examples, data.variables,
                chat_history=data.chat_history,
                ignore_template_error=ignore_template_error
            )
        except Exception as e:
            log.error("************* AIProvider.get_integration and self.module.prepare_prompt_struct")
            log.error(str(e))
            log.info(str(format_exc()))
            log.error("*************")
            return str(e), 400

        result = AIProvider.predict(project_id, integration, model_settings, prompt_struct)
        if not result['ok']:
            log.error("************* if not result['ok']")
            log.error(str(result['error']))
            log.error("*************")
            return str(result['error']), 400

        if isinstance(result['response'], str):
            result['response'] = {'messages': [{'type': 'text', 'content': result['response']}]}
        return result['response'], 200


class API(api_tools.APIBase):
    url_params = [
        '<string:mode>/<int:project_id>',
        '<int:project_id>',
    ]

    mode_handlers = {
        c.DEFAULT_MODE: ProjectAPI,
    }
