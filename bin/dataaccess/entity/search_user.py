"""
Entity：search_user

create 2025/05/16 hamada
"""
import dataclasses


@dataclasses.dataclass
class SearchUser:
    settings_user_id = None
    slack_user_id = None
    display_flg = None
    default_check_flg = None

    def __init__(self, settings_user_id = None, slack_user_id = None, display_flg = None, default_check_flg = None):
        self.settings_user_id = settings_user_id
        self.slack_user_id = slack_user_id
        self.display_flg = display_flg
        self.default_check_flg = default_check_flg
