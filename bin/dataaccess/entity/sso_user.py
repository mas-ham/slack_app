"""
Entity：sso_user

create 2025/05/14 hamada
"""
import dataclasses


@dataclasses.dataclass
class SsoUser:
    pc_user = None
    user_id = None
    is_admin = None

    def __init__(self, pc_user = None, user_id = None, is_admin = None):
        self.pc_user = pc_user
        self.user_id = user_id
        self.is_admin = is_admin
