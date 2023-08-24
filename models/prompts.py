from sqlalchemy import Integer, Column, String, DateTime, func, JSON
from sqlalchemy.orm import relationship, backref

from tools import db_tools, db, rpc_tools


class Prompt(
    db_tools.AbstractBaseMixin, db.Base, rpc_tools.RpcMixin,
):
    __tablename__ = "models_prompts"
    __table_args__ = {'schema': 'tenant'}

    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, nullable=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(String(256), nullable=True)
    prompt = Column(String, nullable=True)
    test_input = Column(String, nullable=True)
    type = Column(String(128), nullable=False)
    model_settings = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    tags = relationship("Tag", secondary='tenant.models_prompts_tags_association', 
        backref=backref("prompts"), lazy='joined')
