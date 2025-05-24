"""
Slack共通処理

"""
from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError

from common.logger.logger import Logger


class SlackService:
    def __init__(self, logger:Logger, token):
        self.client = WebClient(token=token, proxy=None)
        self.logger = logger


    def get_history(self, channel_id, oldest, latest, limit=1000):
        """
        投稿内容を取得

        Args:
            channel_id:
            oldest:
            latest:
            limit:

        Returns:

        """
        if oldest >= 0 and latest >= 0:
            return self.client.conversations_history(channel=channel_id, limit=limit, oldest=oldest, latest=latest)
        elif oldest >= 0 > latest:
            return self.client.conversations_history(channel=channel_id, limit=limit, oldest=oldest)
        elif oldest < 0 <= latest:
            return self.client.conversations_history(channel=channel_id, limit=limit, latest=latest)
        else:
            return self.client.conversations_history(channel=channel_id, limit=limit)


    def get_history_cursor(self, channel_id, cursor):
        """
        投稿内容を取得(カーソル使用)

        Args:
            channel_id:
            cursor:

        Returns:

        """
        return self.client.conversations_history(channel=channel_id, cursor=cursor)


    def get_replies(self, channel_id, ts):
        """
        返信内容を取得

        Args:
            channel_id:
            ts:

        Returns:

        """
        return self.client.conversations_replies(channel=channel_id, ts=ts)


    def get_user_list(self):
        """
        ユーザーリストを取得

        Returns:

        """
        return self.client.users_list()


    def get_channel_list(self, channel_type):
        """
        チャンネルリストを取得

        Args:
            channel_type:

        Returns:

        """
        return self.client.conversations_list(types=channel_type)