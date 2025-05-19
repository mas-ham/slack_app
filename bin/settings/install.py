"""
インストール

create 2025/05/13 hamada
"""
import os


def install(bin_dir, conn):
    cur = conn.cursor()

    # テーブルcreate
    __create_table(cur, bin_dir, 'channel')
    __create_table(cur, bin_dir, 'search_channel')
    __create_table(cur, bin_dir, 'search_user')
    __create_table(cur, bin_dir, 'slack_user')
    __create_table(cur, bin_dir, 'tr_channel_histories')
    __create_table(cur, bin_dir, 'tr_channel_replies')

    # インデックス
    cur.execute('CREATE INDEX idx_histories_post_user ON tr_channel_histories(post_slack_user_id)')
    cur.execute('CREATE INDEX idx_histories_channel_id ON tr_channel_histories(channel_id)')
    cur.execute('CREATE INDEX idx_replies_reply_user ON tr_channel_replies(reply_slack_user_id)')
    cur.execute('CREATE INDEX idx_replies_history_id ON tr_channel_replies(thread_ts)')

    conn.commit()
    cur.close()


def __create_table(cur, bin_dir, table_id):
    """
    テーブルCreate
    """
    # drop
    cur.execute(__create_query_drop(table_id))
    # create
    cur.execute(__get_query(bin_dir, f'{table_id}.sql'))


def __create_query_drop(table_id):
    """
    Drop文取得
    """
    return f'DROP TABLE IF EXISTS {table_id}'


def __get_query(bin_dir, filename):
    """
    Create文取得
    """
    print(filename)
    with open(os.path.join(bin_dir, 'settings', 'ddl', filename), 'r', encoding='utf-8') as f:
        query = f.read()
    return query


