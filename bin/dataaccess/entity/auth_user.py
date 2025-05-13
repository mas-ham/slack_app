"""
Entity：auth_user

create 2025/05/13 hamada
"""
import dataclasses


@dataclasses.dataclass
class AuthUser:
    user_id = None
    channel_id = None

    def __init__(self, user_id = None, channel_id = None):
        self.user_id = user_id
        self.channel_id = channel_id
