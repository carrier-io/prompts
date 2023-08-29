from pylon.core.tools import web, log
from pydantic import ValidationError

from tools import tasklib
from ..models.pd.prompts_pd import PredictPostModel
from ..utils.ai_providers import AIProvider


class RPC:

    @web.rpc('prompts_predict', 'predict')
    @tasklib.task("prompts_predict", {})
    def predict(self, project_id: int, payload: dict):
        try:
            data = PredictPostModel.parse_obj(payload)
        except ValidationError as e:
            log.error(e.errors())
            return {"ok": False, "error": e.errors()}
        model_settings = data.integration_settings.dict(exclude={'project_id'})
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
