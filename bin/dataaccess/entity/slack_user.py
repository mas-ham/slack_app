"""
Entity：slack_user

create 2025/05/14 hamada
"""
import dataclasses


@dataclasses.dataclass
class SlackUser:
    slack_user_id = None
    user_id = None
    user_name = None
    icon = None
    delete_flg = None

    def __init__(self, slack_user_id = None, user_id = None, user_name = None, icon = None, delete_flg = None):
        self.slack_user_id = slack_user_id
        self.user_id = user_id
        self.user_name = user_name
        self.icon = icon
        self.delete_flg = delete_flg
