"""
Slack操作ツール：共通処理

create 2025/05/09 hamada
"""
import os
import json
import datetime
import re

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

def convert_jst(unix):
    """
    UNIX時間をJSTに変換

    Args:
        unix:

    Returns:

    """
    dt_utc = datetime.datetime.fromtimestamp(unix, tz=datetime.timezone.utc)
    jst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    return jst.strftime('%Y-%m-%d %H:%M:%S')


def convert_from_date(val):
    """
    期間(From)に変換

    Args:
        val:

    Returns:

    """
    if val is None:
        return ''
    converted_datetime = dateutil.parser.parse(val.strftime('%Y-%m-%d'))
    return converted_datetime.strftime('%Y-%m-%d %H:%M:%S')


def convert_to_date(val):
    """
    期間(To)に変換

    Args:
        val:

    Returns:

    """
    if val is None:
        return ''
    converted_datetime = dateutil.parser.parse(val.strftime('%Y-%m-%d'))
    converted_datetime = converted_datetime + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
    return converted_datetime.strftime('%Y-%m-%d %H:%M:%S')


def convert_flg(val: bool) -> str:
    """
    bool型のフラグをstrに変換

    Args:
        val:

    Returns:

    """
    return '1' if val else '0'


def remove_control_characters(text):
    """
    ASCII範囲の制御文字を除去

    Args:
        text:

    Returns:

    """
    return re.sub(r'[\x00-\x1F\x7F]', '', text)
