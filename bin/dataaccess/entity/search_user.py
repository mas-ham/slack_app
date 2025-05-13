"""
Entity：search_user

create 2025/05/13 hamada
"""
import dataclasses


@dataclasses.dataclass
class SearchUser:
    settings_user_id = None
    user_id = None
    display_flg = None
    default_check_flg = None

    def __init__(self, settings_user_id = None, user_id = None, display_flg = None, default_check_flg = None):
        self.settings_user_id = settings_user_id
        self.user_id = user_id
        self.display_flg = display_flg
        self.default_check_flg = default_check_flg
