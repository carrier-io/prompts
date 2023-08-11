from sqlalchemy import Integer, Column, String, DateTime, func, JSON, Boolean, ForeignKey
from tools import db_tools, db, rpc_tools


class Prompt(
    db_tools.AbstractBaseMixin, db.Base, rpc_tools.RpcMixin,
):
    __tablename__ = "prompts"
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


class Example(
    db_tools.AbstractBaseMixin, db.Base, rpc_tools.RpcMixin,
):
    __tablename__ = "examples"
    __table_args__ = (
        {"schema": "tenant"},
    )
    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, nullable=False)
    input = Column(String)
    output = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class Variable(db_tools.AbstractBaseMixin, db.Base):
    __tablename__ = "variables"
    __table_args__ = (
        {"schema": "tenant"},
    )
    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey('tenant.prompts.id'), nullable=False)
    name = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)