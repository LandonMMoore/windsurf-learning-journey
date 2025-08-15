from datetime import datetime

from abs_nosql_repository_core.document import BaseDraftDocument


class Integration(BaseDraftDocument):
    provider_name: str
    email: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    user_id: int

    class Settings:
        name = "integrations"
