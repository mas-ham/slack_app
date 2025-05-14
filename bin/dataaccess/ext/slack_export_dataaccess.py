import pandas as pd

# 投稿内容を登録
SQL_UPSERT_HISTORIES = (
    """
    INSERT INTO tr_channel_histories (
        channel_id
      , post_date
      , post_slack_user_id
      , post_message
    )
    VALUES (
        ?
      , ?
      , ?
      , ?
    )
    ON CONFLICT (post_date)
    DO UPDATE 
        SET post_message     = ?
    """
)

# 返信内容を登録
SQL_UPSERT_REPLIES = (
    """
    INSERT INTO tr_channel_replies (
        channel_history_id
      , reply_date
      , reply_slack_user_id
      , reply_message
    )
    VALUES (
        ?
      , ?
      , ?
      , ?
    )
    ON CONFLICT (reply_date)
    DO UPDATE 
        SET reply_message     = ?
    """
)

SQL_GET_SLACK_MESSAGES = (
    """
    SELECT
        ''                       AS no
      , ''                       AS post_icon
      , user1.user_id            AS post_user_id
      , history.post_date        AS post_date
      , history.post_message     AS post_message
      , ''                       AS reply_icon
      , user2.user_id            AS reply_user_id
      , reply.reply_date         AS reply_date
      , reply.reply_message      AS reply_message
    FROM
      tr_channel_histories               history
      LEFT OUTER JOIN tr_channel_replies reply
        ON  reply.channel_history_id  = history.channel_history_id
      LEFT OUTER JOIN channel            channel
        ON  channel.channel_id        = history.channel_id
      LEFT OUTER JOIN slack_user         user1
        ON  user1.slack_user_id       = history.post_slack_user_id
      LEFT OUTER JOIN slack_user         user2
        ON  user2.slack_user_id       = reply.reply_slack_user_id
    WHERE
          channel.channel_type  = ?
      AND channel.channel_name  = ?
    ORDER BY
        history.channel_history_id
      , reply.channel_reply_id
    """
)

class SlackExportDataaccess:
    def __init__(self, cursor):
        self.cursor = cursor

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
        self.cursor.execute(SQL_GET_SLACK_MESSAGES, params)
        return pd.DataFrame(self.cursor.fetchall(), columns=['no', 'post_icon', 'post_name', 'post_date', 'post_message', 'reply_icon', 'reply_name', 'reply_date', 'reply_message'])
