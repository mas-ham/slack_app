"""
Entity：search_user

create 2025/05/17 hamada
"""
import dataclasses


@dataclasses.dataclass
class SearchUser:
    slack_user_id = None
    display_flg = None
    default_check_flg = None

    def __init__(self, slack_user_id = None, display_flg = None, default_check_flg = None):
        self.slack_user_id = slack_user_id
        self.display_flg = display_flg
        self.default_check_flg = default_check_flg
