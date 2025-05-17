"""
Entity：search_channel

create 2025/05/17 hamada
"""
import dataclasses


@dataclasses.dataclass
class SearchChannel:
    channel_id = None
    display_flg = None
    default_check_flg = None

    def __init__(self, channel_id = None, display_flg = None, default_check_flg = None):
        self.channel_id = channel_id
        self.display_flg = display_flg
        self.default_check_flg = default_check_flg
