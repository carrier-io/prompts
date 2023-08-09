from pylon.core.tools import web, log  # pylint: disable=E0611,E0401

from tools import auth, theme  # pylint: disable=E0401


class Slot:  # pylint: disable=E1101,R0903

    @web.slot('models_config_content')
    @auth.decorators.check_slot(['models.config'],
                                access_denied_reply=theme.access_denied_part)
    def content(self, context, slot, payload):
        # log.info('slot: [%s], payload: %s', slot, payload)
        # ai_integrations = context.rpc_manager.call.integrations_get_all_integrations_by_section(
        #     project_id=context.rpc_manager.call.project_get_id(),
        #     section_name='ai'
        # )
        # ai_integrations = [integration.dict(
        #     exclude={'section'}
        # ) for integration in ai_integrations]

        # all_tokens = auth.list_tokens(
        #     user_id=payload.auth.id,
        #     name=TOKEN_NAME
        # )
        # #
        # if len(all_tokens) < 1:
        #     token_id = auth.add_token(
        #         user_id=payload.auth.id,
        #         name=TOKEN_NAME,
        #         # expires=datetime.datetime.now()+datetime.timedelta(seconds=30),
        #     )
        # else:
        #     token_id = all_tokens[0]["id"]
        # token = auth.encode_token(token_id)

        # data = self.get_config(project_id=payload.project.id, user_id=payload.auth.id)
        # table_data = [{'key': k, 'value': v} for k, v in data.dict().items()]

        with context.app.app_context():
            return self.descriptor.render_template(
                'config/content.html',
                payload=payload,
                # data=data,
                # table_data=table_data
            )

    @web.slot('models_config_scripts')
    @auth.decorators.check_slot(['models.config'])
    def scripts(self, context, slot, payload):
        with context.app.app_context():
            return self.descriptor.render_template(
                'config/scripts.html',
            )

    @web.slot('models_config_styles')
    @auth.decorators.check_slot(['models.config'])
    def styles(self, context, slot, payload):
        with context.app.app_context():
            return self.descriptor.render_template(
                'config/styles.html',
            )
