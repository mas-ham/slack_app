"""
Entity：search_channel

create 2025/05/16 hamada
"""
import dataclasses


@dataclasses.dataclass
class SearchChannel:
    settings_user_id = None
    channel_id = None
    display_flg = None
    default_check_flg = None

    def __init__(self, settings_user_id = None, channel_id = None, display_flg = None, default_check_flg = None):
        self.settings_user_id = settings_user_id
        self.channel_id = channel_id
        self.display_flg = display_flg
        self.default_check_flg = default_check_flg
