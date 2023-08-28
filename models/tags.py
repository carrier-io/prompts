from sqlalchemy import String, Column, Integer, ForeignKey

from tools import db, db_tools


class PromptTag(db_tools.AbstractBaseMixin, db.Base):
    __tablename__ = "models_prompts_tags_association"
    __table_args__ = {'schema': 'tenant'}

    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey('tenant.models_prompts.id'))
    tag_id = Column(Integer, ForeignKey('tenant.models_prompts_tags.id'))


class Tag(db_tools.AbstractBaseMixin, db.Base):
    __tablename__ = "models_prompts_tags"
    __table_args__ = {'schema': 'tenant'}

    id = Column(Integer, primary_key=True)
    tag = Column(String(250), unique=True, nullable=False)
    color = Column(String(15))
