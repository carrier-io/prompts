from pylon.core.tools import web, log
from pydantic import ValidationError

from tools import tasklib
from ..models.pd.prompts_pd import PredictPostModel
from ..utils.ai_providers import AIProvider

import re

def handle_exceptions(fn):

    def _is_special_value(value):

        if not isinstance(value, str):
            return False
        
        variable_pattern = r"([a-zA-Z0-9_]+)"
        variables_pattern = r"{{variables\." + variable_pattern + r"}}"
        prev_pattern = r"{{nodes\['"+ variable_pattern + r"'\]\.?" + variable_pattern + r"?}}"

        if re.fullmatch(variables_pattern, value) or \
            re.fullmatch(prev_pattern, value):
            return True

        return False

    def decorated(self, **kwargs):
        try:
            fn(self, **kwargs)
            return {"ok": True}
        except ValidationError as e:
            valid_erros = []
            for error in e.errors():
                log.info(f"ERROR: {error}")
                if error['type'] == "value_error.missing" or "__root__" in error['loc']:
                    valid_erros.append(error)
                    continue
                
                invalid_value = {**kwargs}
                for loc in error["loc"]:
                    invalid_value = invalid_value[loc]
                
                # check for special values
                if not _is_special_value(invalid_value):
                    valid_erros.append(error)

            if valid_erros:
                return {"ok": False, "errors": valid_erros}
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        
    return decorated


class RPC:

    @web.rpc('prompts_predict__validate', 'predict__validate')
    @handle_exceptions
    def validate_predict_payload(self, **kwargs):
        return PredictPostModel.validate(kwargs)


    @web.rpc('prompts_predict', 'predict')
    @tasklib.task("prompts_predict", {
        "uid": "prompt",
        "tooltip": "prompt.svg",
        "icon_url":"/flows/static/icons/prompt.svg",
    })
    def predict(self, project_id: int, **kwargs):
        try:
            data = PredictPostModel.validate(kwargs)
        except ValidationError as e:
            log.error(e.errors())
            return {"ok": False, "error": e.errors()}
        
        model_settings = data.integration_settings
        try:
            integration = AIProvider.get_integration(
                project_id=project_id,
                integration_id=data.integration_id,
            )
            text_prompt = self.prepare_text_prompt(
                project_id, data.prompt_id, data.input_, 
                data.context, data.examples, data.variables
            )
        except Exception as e:
            log.error(str(e))
            return {"ok": False, "error": str(e)}
        
        output = AIProvider.predict(project_id, integration, model_settings, text_prompt)
        return {"ok": True, "result": output}
