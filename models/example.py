from sqlalchemy import Integer, Column, String, DateTime, func, Boolean, ForeignKey
from tools import db_tools, db, rpc_tools


class Example(
    db_tools.AbstractBaseMixin, db.Base, rpc_tools.RpcMixin,
):
    __tablename__ = "models_examples"
    __table_args__ = (
        {"schema": "tenant"},
    )
    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey('tenant.models_prompts.id', ondelete='CASCADE'), nullable=False)
    input = Column(String)
    output = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
