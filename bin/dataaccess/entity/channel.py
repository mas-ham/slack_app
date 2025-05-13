"""
Entity：channel

create 2025/05/13 hamada
"""
import dataclasses


@dataclasses.dataclass
class Channel:
    channel_id = None
    channel_name = None
    channel_type = None

    def __init__(self, channel_id = None, channel_name = None, channel_type = None):
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.channel_type = channel_type
