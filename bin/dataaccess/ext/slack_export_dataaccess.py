"""
Slackメッセージ取得用dataaccess

"""
import pandas as pd

# チャンネルを登録
SQL_UPSERT_CHANNEL = (
    """
    INSERT INTO channel (
        channel_id
      , channel_name
      , channel_type
    )
    VALUES (
        :channel_id
      , :channel_name
      , :channel_type
    )
    ON CONFLICT (channel_id)
    DO UPDATE 
        SET 
            channel_name     = :channel_name
          , channel_type     = :channel_type
    """
)


# 投稿内容を登録
SQL_UPSERT_HISTORIES = (
    """
    INSERT INTO tr_channel_histories (
        ts
      , channel_id
      , post_date
      , post_slack_user_id
      , post_message
    )
    VALUES (
        :ts
      , :channel_id
      , :post_date
      , :post_slack_user_id
      , :post_message
    )
    ON CONFLICT (ts)
    DO UPDATE 
        SET post_message     = :post_message
    """
)

# 返信内容を登録
SQL_UPSERT_REPLIES = (
    """
    INSERT INTO tr_channel_replies (
        ts
      , thread_ts
      , reply_date
      , reply_slack_user_id
      , reply_message
    )
    VALUES (
        :ts
      , :thread_ts
      , :reply_date
      , :reply_slack_user_id
      , :reply_message
    )
    ON CONFLICT (ts)
    DO UPDATE 
        SET reply_message     = :reply_message
    """
)

SQL_GET_SLACK_MESSAGES = (
    """
    SELECT
        history.ts                     AS thread_ts
      , reply.ts                       AS ts
      , user1.user_id                  AS post_user_id
      , history.post_date              AS post_date
      , history.post_message           AS post_message
      , user2.user_id                  AS reply_user_id
      , reply.reply_date               AS reply_date
      , reply.reply_message            AS reply_message
    FROM
      tr_channel_histories               history
      LEFT OUTER JOIN tr_channel_replies reply
        ON  reply.thread_ts           = history.ts
      LEFT OUTER JOIN channel            channel
        ON  channel.channel_id        = history.channel_id
      LEFT OUTER JOIN slack_user         user1
        ON  user1.slack_user_id       = history.post_slack_user_id
      LEFT OUTER JOIN slack_user         user2
        ON  user2.slack_user_id       = reply.reply_slack_user_id
    WHERE
          channel.channel_type  = :channel_type
      AND channel.channel_name  = :channel_name
    ORDER BY
        history.post_date
      , reply.reply_date
    """
)

class SlackExportDataaccess:
    def __init__(self, cursor):
        self.cursor = cursor

    def upsert_channel(self, params):
        """
        チャンネル一覧Upsert

        Args:
            params:

        Returns:

        """
        return self.cursor.execute(SQL_UPSERT_CHANNEL, params)


    def upsert_history(self, params):
        """
        チャンネル投稿一覧に登録/更新

        Args:
            params:

        Returns:

        """
        return self.cursor.execute(SQL_UPSERT_HISTORIES, params)


    def upsert_reply(self, params):
        """
        チャンネル返信一覧に登録/更新

        Args:
            params:

        Returns:

        """
        return self.cursor.execute(SQL_UPSERT_REPLIES, params)


    def get_slack_messages(self, params):
        """
        Excel出力用にSlackメッセージを検索

        Args:
            params:

        Returns:

        """
        self.cursor.execute(SQL_GET_SLACK_MESSAGES, params)
        return pd.DataFrame(self.cursor.fetchall(), columns=['thread_ts', 'ts', 'post_name', 'post_date', 'post_message', 'reply_name', 'reply_date', 'reply_message'])
