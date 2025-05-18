"""
Entity：tr_channel_histories

create 2025/05/18 hamada
"""
import dataclasses


@dataclasses.dataclass
class TrChannelHistories:
    ts = None
    channel_id = None
    post_date = None
    post_slack_user_id = None
    post_message = None

    def __init__(self, ts = None, channel_id = None, post_date = None, post_slack_user_id = None, post_message = None):
        self.ts = ts
        self.channel_id = channel_id
        self.post_date = post_date
        self.post_slack_user_id = post_slack_user_id
        self.post_message = post_message
