from tools import db


def init_db():
    from .models.prompts import Prompt, Example
    # db.get_shared_metadata().create_all(bind=db.engine)
