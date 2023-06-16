from sqlalchemy import Integer, Column, String, DateTime, UniqueConstraint, func

from tools import db_tools, db, rpc_tools
from pylon.core.tools import log  # pylint: disable=E0611,E0401


class Prompt(
    db_tools.AbstractBaseMixin, db.Base, rpc_tools.RpcMixin,
):
    __tablename__ = "prompts"
    __table_args__ = {'schema': 'tenant'}

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(String(256), nullable=True)
    type = Column(String(64))
    prompt = Column(String, nullable=True)
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
    created_at = Column(DateTime, nullable=False, server_default=func.now())
