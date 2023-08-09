from pylon.core.tools import log, web

from tools import VaultClient


class Event:

    @web.event("new_ai_user")
    def handle_new_ai_user(self, context, event, payload: int):
        # payload == user_id
        secrets = VaultClient().get_all_secrets()
        try:
            ai_project_id = secrets['ai_project_id']
        except KeyError:
            log.critical('Secret for "ai_project_id" is not set')
            return

        try:
            ai_project_roles = secrets['ai_project_roles']
        except KeyError:
            project_secrets = VaultClient(ai_project_id).get_all_secrets()
            try:
                ai_project_roles = project_secrets['ai_project_roles']
            except KeyError:
                log.critical('Secret for "ai_project_roles" is not set')
                return
        ai_project_roles = [i.strip() for i in ai_project_roles.split(',')]

        context.rpc_manager.call.admin_add_user_to_project(
            ai_project_id, payload, ai_project_roles
        )
