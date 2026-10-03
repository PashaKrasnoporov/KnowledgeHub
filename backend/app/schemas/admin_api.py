from pydantic import BaseModel


class UserActiveStatusAPIRequest(BaseModel):
    is_active: bool
