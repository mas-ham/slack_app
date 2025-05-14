"""
Entity：tr_channel_replies

create 2025/05/14 hamada
"""
import dataclasses


@dataclasses.dataclass
class TrChannelReplies:
    channel_reply_id = None
    channel_history_id = None
    reply_date = None
    reply_slack_user_id = None
    reply_message = None

    def __init__(self, channel_reply_id = None, channel_history_id = None, reply_date = None, reply_slack_user_id = None, reply_message = None):
        self.channel_reply_id = channel_reply_id
        self.channel_history_id = channel_history_id
        self.reply_date = reply_date
        self.reply_slack_user_id = reply_slack_user_id
        self.reply_message = reply_message
