from sqlalchemy import Column
from sqlmodel import Field, ForeignKey, UniqueConstraint

from src.common.models import BaseModel


class Priority(BaseModel, table=True):
    __tablename__ = "priority"  # type:ignore
    __table_args__ = {UniqueConstraint("organization_id", "name", name="uniq_org_name")}

    name: str
    level: int
    color: str
    organization_id: int = Field(
        sa_column=Column(ForeignKey("sys_organizations.id", ondelete="CASCADE"))
    )
