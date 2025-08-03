import contextvars

organization_id_ctx = contextvars.ContextVar("organization_id")


class TenantContext:

    @classmethod
    def set(cls, organization_id: int):
        """
        Sets the context with the organization_id
        """
        organization_id_ctx.set(organization_id)

    @classmethod
    def get(cls):
        """
        gets the organization id from the current context
        """
        return organization_id_ctx.get(None)
