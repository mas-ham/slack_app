"""
インストール

create 2025/05/13 hamada
"""
import os


def install(bin_dir, conn):
    cur = conn.cursor()

    # テーブルcreate
    # __create_table(cur, bin_dir, 'auth_user')
    # __create_table(cur, bin_dir, 'channel')
    __create_table(cur, bin_dir, 'search_channel')
    __create_table(cur, bin_dir, 'search_user')
    # __create_table(cur, bin_dir, 'slack_user')
    # __create_table(cur, bin_dir, 'sso_user')
    # __create_table(cur, bin_dir, 'tr_channel_histories')
    # __create_table(cur, bin_dir, 'tr_channel_replies')

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


