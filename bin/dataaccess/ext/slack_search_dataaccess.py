import pandas as pd

# 投稿者/返信者を取得
SQL_GET_POSTER_LIST = (
    """
    SELECT
        slack.user_id              AS user_id
      , slack.user_name            AS user_name
      , slack.delete_flg           AS delete_flg
      , search.display_flg         AS display_flg
      , search.default_check_flg   AS default_check_flg
    FROM
      slack_user              slack
      LEFT JOIN search_user   search
        ON  search.user_id         = slack.user_id
    WHERE
      display_flg                  = 1
    ORDER BY
        slack.user_id
    """
)

# チャンネルを取得
SQL_GET_CHANNEL_LIST = (
    """
    SELECT
        channel.channel_id         AS channel_id
      , channel.channel_name       AS channel_name
      , channel.channel_type       AS channel_type
      , search.display_flg         AS display_flg
      , search.default_check_flg   AS default_check_flg
    FROM
      channel                   channel
      LEFT JOIN search_channel  search
        ON  search.channel_id      = channel.channel_id
    WHERE
          display_flg              = 1
      AND channel_type             = ?
    ORDER BY
        channel.channel_name
    """
)
class SlackSearchDataaccess:
    def __init__(self, conn):
        self.conn = conn

    def get_poster_list(self) -> pd.DataFrame:
        """
        投稿者/返信者一覧取得

        Args:

        Returns:

        """
        return pd.read_sql(SQL_GET_POSTER_LIST, self.conn)


    def get_channel_list(self, channel_type) -> pd.DataFrame:
        """
        チャンネル一覧取得

        Args:
            channel_type:

        Returns:

        """
        return pd.read_sql(SQL_GET_CHANNEL_LIST, con=self.conn, params=[channel_type])

