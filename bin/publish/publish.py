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
from dataaccess.ext.slack_export_dataaccess import SlackExportDataaccess


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
            _create_table(conn_dst.cursor(), self.bin_dir, 'slack_user')
            _create_table(conn_dst.cursor(), self.bin_dir, 'search_user')
            _create_table(conn_dst.cursor(), self.bin_dir, 'channel')
            _create_table(conn_dst.cursor(), self.bin_dir, 'search_channel')
            _create_table(conn_dst.cursor(), self.bin_dir, 'tr_channel_histories')
            _create_table(conn_dst.cursor(), self.bin_dir, 'tr_channel_replies')

        # 移行データを取得
        print('get source_data')
        with sql_shared_service.get_connection(self.root_dir) as conn_src:
            slack_user_records = _get_slack_user(conn_src)
            search_user_records = _get_search_user(conn_src)
            channel_records = _get_channel(conn_src)
            channel_id_list = [r.channel_id for r in channel_records]
            search_channel_records = _get_search_channel(conn_src, channel_id_list)
            history_records = _get_channel_histories(conn_src, channel_id_list)
            history_id_list = [r.channel_history_id for r in history_records]
            reply_records = _get_channel_replies(conn_src, history_id_list)
            history_reply_records = _get_histories_replies(history_records, reply_records)

        # 新DBへ登録
        print('insert dist_db')
        with sql_shared_service.get_connection(os.path.join(self.root_dir, 'dist')) as conn_dst:
            _insert_slack_user(conn_dst, slack_user_records)
            _insert_search_user(conn_dst, search_user_records)
            _insert_channel(conn_dst, channel_records)
            _insert_search_channel(conn_dst, search_channel_records)
            _insert_histories_replies(conn_dst, history_reply_records)

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


def _get_channel_replies(conn, history_id_list):
    cond = [Condition('channel_history_id', history_id_list, 'in')]
    dataaccess = tr_channel_replies_dataaccess.TrChannelRepliesDataAccess(conn)
    return dataaccess.select(conditions=cond)


def _get_histories_replies(histories, replies):
    result_list = []
    for history in histories:
        reply_list = []
        history_id = history.channel_history_id
        for reply in replies:
            if history_id == reply.channel_history_id:
                reply_list.append({
                    'channel_history_id': history_id,
                    'reply_date': reply.reply_date,
                    'reply_slack_user_id': reply.reply_slack_user_id,
                    'reply_message': reply.reply_message,
                })
        result_list.append({
            'channel_id': history.channel_id,
            'post_date': history.post_date,
            'post_slack_user_id': history.post_slack_user_id,
            'post_message': history.post_message,
            'reply_list': reply_list,
        })

    return result_list


def _insert_slack_user(conn, list_):
    dataaccess = slack_user_dataaccess.SlackUserDataAccess(conn)
    dataaccess.insert_many(list_)


def _insert_search_user(conn, list_):
    dataaccess = search_user_dataaccess.SearchUserDataAccess(conn)
    dataaccess.insert_many(list_)


def _insert_channel(conn, list_):
    dataaccess = channel_dataaccess.ChannelDataAccess(conn)
    dataaccess.insert_many(list_)


def _insert_search_channel(conn, list_):
    dataaccess = search_channel_dataaccess.SearchChannelDataAccess(conn)
    dataaccess.insert_many(list_)


def _insert_histories(conn, list_):
    dataaccess = tr_channel_histories_dataaccess.TrChannelHistoriesDataAccess(conn)
    dataaccess.insert_many(list_)


def _insert_replies(conn, list_):
    dataaccess = tr_channel_replies_dataaccess.TrChannelRepliesDataAccess(conn)
    dataaccess.insert_many(list_)


def _insert_histories_replies(conn, list_):
    cursor = conn.cursor()
    dataaccess = SlackExportDataaccess(cursor)
    for history_info in list_:
        history_params = {
            'channel_id': history_info['channel_id'],
            'post_date': history_info['post_date'],
            'post_slack_user_id': history_info['post_slack_user_id'],
            'post_message': history_info['post_message']
        }
        dataaccess.upsert_history(history_params)
        # 登録されたID
        if cursor.lastrowid:
            channel_history_id = cursor.lastrowid
        else:
            # 既存のIDを取得
            channel_history_id = _get_channel_history_id_by_logical_pk(conn, history_info['post_date'])

        # 返信内容
        for reply_info in history_info['reply_list']:
            reply_params = {
                'channel_history_id': channel_history_id,
                'reply_date': reply_info['reply_date'],
                'reply_slack_user_id': reply_info['reply_slack_user_id'],
                'reply_message': reply_info['reply_message']
            }
            dataaccess.upsert_reply(reply_params)

def _get_channel_history_id_by_logical_pk(conn, post_date):
    """
    論理キーで投稿履歴IDを取得する

    Args:
        post_date:

    Returns:

    """
    cond = [Condition('post_date', post_date)]
    dataaccess = tr_channel_histories_dataaccess.TrChannelHistoriesDataAccess(conn)
    results = dataaccess.select(conditions=cond)

    return results[0].channel_id


def _create_table(cur, bin_dir, table_id):
    """
    テーブルCreate
    """
    # drop
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


