import pandas as pd

# 投稿者/返信者を取得
SQL_GET_POSTER_LIST = (
    """
    SELECT
        slack.slack_user_id        AS slack_user_id
      , slack.user_id              AS user_id
      , slack.user_name            AS user_name
      , slack.delete_flg           AS delete_flg
      , search.display_flg         AS display_flg
      , search.default_check_flg   AS default_check_flg
    FROM
      search_user                  search
      LEFT JOIN slack_user         slack
        ON  slack.slack_user_id    = search.slack_user_id
    WHERE
      slack.user_id                <> 'deactivateduser'
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
      search_channel               search
      LEFT JOIN channel            channel
        ON  channel.channel_id     = search.channel_id
    ORDER BY
        CASE channel.channel_type WHEN 'public_channel'  THEN 1
                                  WHEN 'private_channel' THEN 2
                                  WHEN 'im'              THEN 3
                                  WHEN 'mpim'            THEN 4
                                                         ELSE 9 END
      , channel.channel_name
    """
)

# 検索
SQL_SEARCH_WITH = (
    """
    WITH message AS (
        SELECT
            user1.user_id                  AS post_name
          , history.post_slack_user_id     AS post_slack_user_id
          , history.post_date              AS post_date
          , history.post_message           AS post_message
          , user2.user_id                  AS reply_name
          , reply.reply_slack_user_id      AS reply_slack_user_id
          , reply.reply_date               AS reply_date
          , reply.reply_message            AS reply_message
          , channel.channel_id             AS channel_id
          , channel.channel_name           AS channel_name
          , channel.channel_type           AS channel_type
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
          {}
    )
    """
)

SQL_SEARCH_COMMON = (
    """
    SELECT
      post_name,
      post_date,
      post_message,
      reply_name,
      reply_date,
      reply_message,
      channel_type,
      channel_name
    FROM 
      message
    WHERE
          1 = 1
    """
)

SQL_SEARCH_ORDER_BY = (
    """
    ORDER BY
        post_date
      , reply_date
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


    def get_channel_list(self) -> pd.DataFrame:
        """
        チャンネル一覧取得

        Args:

        Returns:

        """
        return pd.read_sql(SQL_GET_CHANNEL_LIST, con=self.conn)


    def search(self, slack_user_id_list, channel_id_list, search_val_list, search_type, is_contains_reply, from_date, to_date) -> pd.DataFrame:
        """
        検索

        Args:

        Returns:

        """
        # SQLを組み立て
        params = []
        # チャンネル
        sql_channel = ''
        if channel_id_list:
            placeholder_list = ['?' for _ in channel_id_list]
            val_list = [v for v in channel_id_list]
            sql_channel = f'channel.channel_id IN ({", ".join(placeholder_list)}) '
            params.extend(val_list)
        sql = SQL_SEARCH_WITH.format(sql_channel)

        # 投稿内容
        sql_post, params_post = _create_sql_search(slack_user_id_list, search_val_list, search_type, from_date, to_date, is_post=True)
        sql += sql_post
        params.extend(params_post)
        # 返信内容
        if is_contains_reply:
            sql += '\n    UNION ALL\n'
            sql_reply, params_reply = _create_sql_search(slack_user_id_list, search_val_list, search_type, from_date, to_date, is_post=False)
            sql += sql_reply
            params.extend(params_reply)
        # ORDER BY
        sql += f'{SQL_SEARCH_ORDER_BY}'

        # 実行
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return pd.DataFrame(cursor.fetchall(), columns=['post_name', 'post_date', 'post_message', 'reply_name', 'reply_date', 'reply_message', 'channel_name', 'channel_type'])


def _create_sql_search(slack_user_id_list, search_val_list, search_type, from_date, to_date, is_post=True):
    """
    検索用SQL組み立て

    Args:
        slack_user_id_list:
        search_val_list:
        search_type:
        from_date:
        to_date:
        is_post:

    Returns:

    """
    prefix = 'post' if is_post else 'reply'
    params = []
    sql = SQL_SEARCH_COMMON
    # 投稿者/返信者
    if slack_user_id_list:
        placeholder_list = ['?' for _ in slack_user_id_list]
        val_list = [v for v in slack_user_id_list]
        sql += f'\n      AND {prefix}_slack_user_id IN ({", ".join(placeholder_list)}) '
        params.extend(val_list)
    # 期間
    if from_date:
        sql += f'\n      AND {prefix}_date >= ?'
        params.append(from_date)
    if to_date:
        sql += f'\n      AND {prefix}_date <= ?'
        params.append(to_date)
    # 投稿/返信内容
    if search_val_list:
        cond = f' AND ' if search_type == '01' else ' OR '
        list_ = []
        for search_val in search_val_list:
            list_.append(f"{prefix}_message LIKE ?")
            params.append(f'%{search_val}%')
        cond_str = cond.join(list_)
        sql += f'\n      AND ({cond_str}) '

    return sql, params
