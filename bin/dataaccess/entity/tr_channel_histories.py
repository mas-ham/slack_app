"""
Entity：tr_channel_histories

create 2025/05/14 hamada
"""
import dataclasses


@dataclasses.dataclass
class TrChannelHistories:
    channel_history_id = None
    channel_id = None
    post_date = None
    post_slack_user_id = None
    post_message = None

    def __init__(self, channel_history_id = None, channel_id = None, post_date = None, post_slack_user_id = None, post_message = None):
        self.channel_history_id = channel_history_id
        self.channel_id = channel_id
        self.post_date = post_date
        self.post_slack_user_id = post_slack_user_id
        self.post_message = post_message
