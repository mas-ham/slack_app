"""
Slack操作ツール：共通処理

create 2025/05/09 hamada
"""
import os
import json
import datetime

import dateutil

from common import const


def get_icon_dir(bin_dir):
    """
    アイコンフォルダを取得

    Args:
        bin_dir:

    Returns:

    """
    return os.path.join(bin_dir, 'static', 'icon')

def get_datafile(bin_dir, data_type):
    """
    チャンネル一覧、投稿一覧、返信一覧ファイルパスを取得

    Args:
        bin_dir:
        data_type:

    Returns:

    """
    if data_type == 'public':
        channel_list_path = os.path.join(bin_dir, const.DATA_DIR, const.PUBLIC_CHANNEL_FILENAME)
        history_list_path = os.path.join(bin_dir, const.DATA_DIR, const.PUBLIC_HISTORY_FILENAME)
        replies_list_path = os.path.join(bin_dir, const.DATA_DIR, const.PUBLIC_REPLIES_FILENAME)
    elif data_type == 'private':
        channel_list_path = os.path.join(bin_dir, const.DATA_DIR, const.PRIVATE_CHANNEL_FILENAME)
        history_list_path = os.path.join(bin_dir, const.DATA_DIR, const.PRIVATE_HISTORY_FILENAME)
        replies_list_path = os.path.join(bin_dir, const.DATA_DIR, const.PRIVATE_REPLIES_FILENAME)
    elif data_type == 'im':
        channel_list_path = os.path.join(bin_dir, const.DATA_DIR, const.IM_CHANNEL_FILENAME)
        history_list_path = os.path.join(bin_dir, const.DATA_DIR, const.IM_HISTORY_FILENAME)
        replies_list_path = os.path.join(bin_dir, const.DATA_DIR, const.IM_REPLIES_FILENAME)
    else:
        channel_list_path = ''
        history_list_path = ''
        replies_list_path = ''

    return channel_list_path, history_list_path, replies_list_path


def get_token():
    """
    SlackAPIトークンを取得

    Returns:

    """
    return os.getenv('SLACK_API_TOKEN')


def get_conf(root_dir):
    """
    設定ファイルを読み込み

    Args:
        root_dir:

    Returns:

    """
    # 設定ファイル読み込み
    json_file = os.path.join(root_dir, const.CONF_DIR, const.SETTINGS_FILENAME)
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_conf(root_dir, filename, json_data):
    """
    設定ファイルを更新

    Args:
        root_dir:
        filename:
        json_data:

    Returns:

    """
    json_file = os.path.join(root_dir, const.CONF_DIR, filename)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)


def convert_from_date(val):
    """
    期間(From)に変換

    Args:
        val:

    Returns:

    """
    converted_datetime = dateutil.parser.parse(val)
    return converted_datetime.strftime('%Y-%m-%d %H:%M:%S')

def convert_to_date(val):
    """
    期間(To)に変換

    Args:
        val:

    Returns:

    """
    converted_datetime = dateutil.parser.parse(val)
    converted_datetime = converted_datetime + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
    return converted_datetime.strftime('%Y-%m-%d %H:%M:%S')
