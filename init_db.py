from tools import db


def init_db():
    from .models.tags import Tag
    from .models.prompts import Prompt
    from .models.example import Example
    from .models.variable import Variable
    db.get_shared_metadata().create_all(bind=db.engine)
