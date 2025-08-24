import contextvars
from typing import Optional

organization_id_ctx = contextvars.ContextVar("organization_id")
user_id_ctx = contextvars.ContextVar("user_id")


class TenantContext:
    """
    Tenant context for organization id
    """

    @classmethod
    def set(cls, organization_id: Optional[int] = None):
        """
        Sets the context with the organization_id
        """
        # print(f"setting organization id {organization_id}")
        if not organization_id:
            organization_id_ctx.set(None)

        organization_id_ctx.set(organization_id)

    @classmethod
    def get(cls):
        """
        gets the organization id from the current context
        """
        return organization_id_ctx.get(None)


class UserContext:
    """
    User context for user id
    """

    @classmethod
    def set(cls, user_id: int):
        """
        Sets the context with the user_id
        """
        user_id_ctx.set(user_id)

    @classmethod
    def get(cls):
        """
        gets the user id from the current context
        """
        return user_id_ctx.get(None)
