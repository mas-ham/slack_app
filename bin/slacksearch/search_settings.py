"""
Slack検索の設定

create 2025/05/13 hamada
"""
from dataaccess.general.search_user_dataaccess import SearchUserDataAccess
from dataaccess.entity.search_user import SearchUser
from dataaccess.entity.search_channel import SearchChannel
from dataaccess.ext import slack_search_dataaccess
from dataaccess.general.search_channel_dataaccess import SearchChannelDataAccess


def get_poster_list(conn):
    """
    投稿者/返信者一覧を取得

    Args:
        conn:

    Returns:

    """
    dataaccess = slack_search_dataaccess.SlackSearchDataaccess(conn)
    return dataaccess.get_poster_list()


def get_channel_list(conn):
    """
    チャンネル一覧を取得

    Args:
        conn:

    Returns:

    """
    dataaccess = slack_search_dataaccess.SlackSearchDataaccess(conn)
    return dataaccess.get_channel_list()


def regist(conn, poster_display_selected, poster_check_selected, channel_display_selected, channel_check_selected):
    """
    検索設定保存

    Args:
        conn:
        poster_display_selected:
        poster_check_selected:
        channel_display_selected:
        channel_check_selected:

    Returns:

    """
    # ユーザー
    search_user_dataaccess = SearchUserDataAccess(conn)
    user_list = search_user_dataaccess.select_all()
    for user in user_list:
        slack_user_id = user.slack_user_id
        # 更新用エンティティ
        entity = SearchUser()
        entity.display_flg = 1 if slack_user_id in poster_display_selected else 0
        entity.default_check_flg = 1 if slack_user_id in poster_check_selected else 0
        # Update
        search_user_dataaccess.update_selective(entity, slack_user_id)

    # チャンネル
    search_channel_dataaccess = SearchChannelDataAccess(conn)
    channel_list = search_channel_dataaccess.select_all()
    for channel in channel_list:
        channel_id = channel.channel_id
        # 更新用エンティティ
        entity = SearchChannel()
        entity.display_flg = 1 if channel_id in channel_display_selected else 0
        entity.default_check_flg = 1 if channel_id in channel_check_selected else 0
        # Update
        search_channel_dataaccess.update_selective(entity, channel_id)
