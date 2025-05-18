"""
Entity：tr_channel_replies

create 2025/05/18 hamada
"""
import dataclasses


@dataclasses.dataclass
class TrChannelReplies:
    ts = None
    thread_ts = None
    reply_date = None
    reply_slack_user_id = None
    reply_message = None

    def __init__(self, ts = None, thread_ts = None, reply_date = None, reply_slack_user_id = None, reply_message = None):
        self.ts = ts
        self.thread_ts = thread_ts
        self.reply_date = reply_date
        self.reply_slack_user_id = reply_slack_user_id
        self.reply_message = reply_message
