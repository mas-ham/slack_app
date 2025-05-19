"""
エクスポートした内容を公開する

create 2025/05/17 hamada
"""
import os
import shutil
from pathlib import Path

from common import const, sql_shared_service
from common.logger.logger import Logger
from dataaccess.common.set_cond_model import Condition
from dataaccess.general import channel_dataaccess, slack_user_dataaccess, search_channel_dataaccess, search_user_dataaccess, tr_channel_histories_dataaccess, tr_channel_replies_dataaccess


class Publish:
    def __init__(self, logger:Logger, root_dir, bin_dir):
        self.logger = logger
        self.root_dir = root_dir
        self.bin_dir = bin_dir


    def main(self):
        """
        エクスポートした内容を公開する

        Returns:

        """

        # 公開用DBでテーブルを再作成
        os.makedirs(os.path.join(self.root_dir, 'dist', 'db'), exist_ok=True)
        with sql_shared_service.get_connection(os.path.join(self.root_dir, 'dist')) as conn_dst:
            cursor_dist = conn_dst.cursor()
            _create_table(cursor_dist, self.bin_dir, 'slack_user')
            _create_table(cursor_dist, self.bin_dir, 'search_user', is_force_drop=False)
            _create_table(cursor_dist, self.bin_dir, 'channel')
            _create_table(cursor_dist, self.bin_dir, 'search_channel', is_force_drop=False)
            _create_table(cursor_dist, self.bin_dir, 'tr_channel_histories')
            _create_table(cursor_dist, self.bin_dir, 'tr_channel_replies')

            # インデックス
            cursor_dist.execute('CREATE INDEX idx_histories_post_user ON tr_channel_histories(post_slack_user_id)')
            cursor_dist.execute('CREATE INDEX idx_histories_channel_id ON tr_channel_histories(channel_id)')
            cursor_dist.execute('CREATE INDEX idx_replies_reply_user ON tr_channel_replies(reply_slack_user_id)')
            cursor_dist.execute('CREATE INDEX idx_replies_history_id ON tr_channel_replies(thread_ts)')

        # 移行データを取得
        print('get source_data')
        with sql_shared_service.get_connection(self.root_dir) as conn_src:
            slack_user_records = _get_slack_user(conn_src)
            search_user_records = _get_search_user(conn_src)
            channel_records = _get_channel(conn_src)
            channel_id_list = [r.channel_id for r in channel_records]
            search_channel_records = _get_search_channel(conn_src, channel_id_list)
            history_records = _get_channel_histories(conn_src, channel_id_list)
            thread_ts_list = [r.ts for r in history_records]
            reply_records = _get_channel_replies(conn_src, thread_ts_list)

        # 新DBへ登録
        print('insert dist_db')
        with sql_shared_service.get_connection(os.path.join(self.root_dir, 'dist')) as conn_dst:
            _insert_slack_user(conn_dst, slack_user_records)
            _insert_search_user(conn_dst, search_user_records)
            _insert_channel(conn_dst, channel_records)
            _insert_search_channel(conn_dst, search_channel_records)
            _insert_histories(conn_dst, history_records)
            _insert_replies(conn_dst, reply_records)

        # Excelをコピー
        print('copy excel')
        export_dir = os.path.join(self.root_dir, 'dist', const.EXPORT_DIR, const.PUBLIC_CHANNEL)
        if os.path.isdir(export_dir):
            shutil.rmtree(export_dir, ignore_errors=True)
        os.makedirs(export_dir, exist_ok=True)

        for file_path in Path(os.path.join(self.root_dir, const.EXPORT_DIR, const.PUBLIC_CHANNEL)).glob('*.xlsx'):
            if file_path.is_file():
                shutil.copy2(file_path, os.path.join(export_dir, file_path.name))


def _get_slack_user(conn):
    dataaccess = slack_user_dataaccess.SlackUserDataAccess(conn)
    return dataaccess.select_all()


def _get_search_user(conn):
    dataaccess = search_user_dataaccess.SearchUserDataAccess(conn)
    return dataaccess.select_all()


def _get_channel(conn):
    cond = [Condition('channel_type', const.PUBLIC_CHANNEL)]
    dataaccess = channel_dataaccess.ChannelDataAccess(conn)
    return dataaccess.select(conditions=cond)


def _get_search_channel(conn, channel_id_list):
    cond = [Condition('channel_id', channel_id_list, 'in')]
    dataaccess = search_channel_dataaccess.SearchChannelDataAccess(conn)
    return dataaccess.select(conditions=cond)


def _get_channel_histories(conn, channel_id_list):
    cond = [Condition('channel_id', channel_id_list, 'in')]
    dataaccess = tr_channel_histories_dataaccess.TrChannelHistoriesDataAccess(conn)
    return dataaccess.select(conditions=cond)


def _get_channel_replies(conn, thread_ts_list):
    cond = [Condition('thread_ts', thread_ts_list, 'in')]
    dataaccess = tr_channel_replies_dataaccess.TrChannelRepliesDataAccess(conn)
    return dataaccess.select(conditions=cond)


def _insert_slack_user(conn, list_):
    dataaccess = slack_user_dataaccess.SlackUserDataAccess(conn)
    dataaccess.insert_many(list_)


def _insert_search_user(conn, list_):
    dataaccess = search_user_dataaccess.SearchUserDataAccess(conn)
    for l in list_:
        slack_user_id = l.slack_user_id
        if dataaccess.select_by_pk(slack_user_id) is None:
            dataaccess.insert(l)


def _insert_channel(conn, list_):
    dataaccess = channel_dataaccess.ChannelDataAccess(conn)
    dataaccess.insert_many(list_)


def _insert_search_channel(conn, list_):
    dataaccess = search_channel_dataaccess.SearchChannelDataAccess(conn)
    for l in list_:
        channel_id = l.channel_id
        if dataaccess.select_by_pk(channel_id) is None:
            dataaccess.insert(l)


def _insert_histories(conn, list_):
    dataaccess = tr_channel_histories_dataaccess.TrChannelHistoriesDataAccess(conn)
    dataaccess.insert_many(list_)


def _insert_replies(conn, list_):
    dataaccess = tr_channel_replies_dataaccess.TrChannelRepliesDataAccess(conn)
    dataaccess.insert_many(list_)


def _create_table(cur, bin_dir, table_id, is_force_drop=True):
    """
    テーブルCreate
    """
    # drop
    if is_force_drop:
        cur.execute(_create_query_drop(table_id))
    # create
    cur.execute(_get_query(bin_dir, f'{table_id}.sql'))


def _create_query_drop(table_id):
    """
    Drop文取得
    """
    return f'DROP TABLE IF EXISTS {table_id}'


def _get_query(bin_dir, filename):
    """
    Create文取得
    """
    with open(os.path.join(bin_dir, 'settings', 'ddl', filename), 'r', encoding='utf-8') as f:
        query = f.read()
    return query


