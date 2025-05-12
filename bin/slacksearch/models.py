"""
Slack検索用モデル

create 2025/05/11 hamada
"""
import dataclasses

@dataclasses.dataclass
class SlackSearchModel:
    search_val: str = ''
    search_val_list: list = None
    search_type: str = '01'
    is_contains_reply: bool = True
    poster_list: list = None
    public_channel_list: list = None
    private_channel_list: list = None
    im_channel_list: list = None
    search_from_date: str = ''
    search_to_date: str = ''

@dataclasses.dataclass
class SlackDetailModel:
    channel_type: str = ''
    channel_name: str = ''
    post_date: str = ''
    search_val: str = ''
    search_val_list: list = None

@dataclasses.dataclass
class SlackResultModel:
    post_date: str = ''
    post_icon: str = ''
    post_name: str = ''
    post_message: str = ''
    result_list: list = None
