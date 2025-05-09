"""
Slack操作ツール：共通処理

create 2025/05/09 hamada
"""
import os
import json

import pandas as pd

from common import const

def regist_datafile(df, filename, sheetname, indexlist):
    """
    データファイルに登録する

    Args:
        df:
        filename:
        sheetname:
        indexlist:

    Returns:

    """

    if indexlist:
        df = df.set_index(indexlist, drop=True)

    writer = pd.ExcelWriter(filename, options={'strings_to_urls':False}, engine='openpyxl')
    df.to_excel(writer, sheet_name=sheetname)
    writer.close()


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


def get_conf(root_dir, filename, target_key):
    """
    設定ファイルを読み込む

    Args:
        root_dir:
        filename:
        target_key:

    Returns:

    """
    # 設定ファイル読み込み
    json_file = os.path.join(root_dir, const.CONF_DIR, f'{target_key}_{filename}')
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_conf(root_dir, filename, target_key, json_data):
    """
    設定ファイルを更新

    Args:
        root_dir:
        filename:
        target_key:
        json_data:

    Returns:

    """
    json_file = os.path.join(root_dir, const.CONF_DIR, f'{target_key}_{filename}')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
