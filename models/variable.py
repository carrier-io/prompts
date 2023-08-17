from sqlalchemy import Integer, Column, String, ForeignKey, UniqueConstraint
from tools import db_tools, db, rpc_tools


class Variable(db_tools.AbstractBaseMixin, db.Base):
    __tablename__ = "models_variables"
    __table_args__ = (
        UniqueConstraint('prompt_id', 'name'),
        {"schema": "tenant"},
    )
    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey('tenant.models_prompts.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
