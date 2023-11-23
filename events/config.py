from pylon.core.tools import log, web

from tools import VaultClient


class Event:

    @web.event("new_ai_user")
    def handle_new_ai_user(self, context, event, payload: dict):
        # payload == {user_id: int, user_email: str}
        secrets = VaultClient().get_all_secrets()
        allowed_domains = {i.strip().strip('@') for i in secrets.get('ai_project_allowed_domains', '').split(',')}
        user_email_domain = payload.get('user_email', '').split('@')[-1]
        log.info(
            'Checking if user eligible to join special project. %s with domain |%s| in allowed domains |%s| and result is |%s|',
            payload.get('user_email'),
            user_email_domain,
            allowed_domains,
            user_email_domain in allowed_domains
        )
        if user_email_domain in allowed_domains:
            log.info('Adding epam user to project %s', payload)
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
            log.info('Adding epam user %s to project %s with roles %s', payload, ai_project_id, ai_project_roles)
            #
            users_roles = context.rpc_manager.call.admin_get_users_roles_in_project(ai_project_id)
            #
            needed_roles = []
            if payload['user_id'] not in users_roles:
                log.info("New AI user: %s", payload['user_id'])
                needed_roles = ai_project_roles
            else:
                for ai_role in ai_project_roles:
                    if ai_role not in users_roles[payload['user_id']]:
                        needed_roles.append(ai_role)
            #
            if needed_roles:
                log.info("Adding needed roles for user %s to project %s: %s", payload['user_id'], ai_project_id, needed_roles)
                context.rpc_manager.call.admin_add_user_to_project(
                    ai_project_id, payload['user_id'], needed_roles
                )
            else:
                log.info("User already added (no roles to add)")
        else:
            log.warning('User with non-epam email registered %s', payload)
