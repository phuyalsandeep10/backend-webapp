"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
<% 
from os import getenv
name=getenv("MIGRATION_NAME")%>
from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

class ${name}Migration(BaseMigration):

    table_name = ""
    def __init__(self):
        super().__init__(revision=${repr(up_revision)},down_revision=${repr(down_revision)})
        #describe your schemas here


def upgrade() -> None:
  """
  Function to create a table
  """
  ${name}Migration().upgrade()
  

def downgrade() -> None:
  """
  Function to drop a table
  """
  ${name}Migration().downgrade()
