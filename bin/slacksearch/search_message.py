"""
Slackからエクスポートした情報から検索する

create 2025/05/10 hamada
"""
import os
import re

import pandas as pd

from common import const

CHECKBOX_WIDTH = 20
POSTER_COLS = 5
CHANNEL_COLS = 5


def get_poster_list(root_dir, bin_dir):
    """
    投稿者/返信者一覧を取得

    Args:
        root_dir:
        bin_dir:

    Returns:

    """
    poster_list = []

    # 検索用ファイル
    search_filename = os.path.join(root_dir, const.CONF_DIR, 'search', 'search_user_list.xlsx')
    if os.path.isfile(search_filename):
        df = pd.read_excel(search_filename, sheet_name=const.USER_SHEET_NAME).query('display_flg == True')
        for _, row in df.iterrows():
            poster_list.append({
                'user_id': row['user_display_name'],
                'user_name': row['user_name'],
                'display_name': f"{row['user_display_name']}：{row['user_name']}",
                'checked': 'checked' if row['default_check_flg'] == True else '',
            })
    else:
        # 検索用ファイルがない場合はマスタから取得する
        df = pd.read_excel(os.path.join(bin_dir, const.DATA_DIR, const.USER_FILENAME), sheet_name=const.USER_SHEET_NAME)
        for _, row in df.iterrows():
            poster_list.append({
                'user_id': row['user_display_name'],
                'user_name': row['user_name'],
                'display_name': f"{row['user_display_name']}：{row['user_name']}",
                'checked': '',
            })

    # 行の高さを算出
    q, r = divmod(len(poster_list), POSTER_COLS)
    poster_rows = q if r == 0 else q + 1

    result_list = []
    poster_index = 0
    for i in range(1, poster_rows + 2):
        records = []
        for j in range(0, POSTER_COLS):
            if poster_index < len(poster_list):
                records.append(poster_list[poster_index])
                poster_index += 1

        result_list.append(records)

    return result_list


def get_channel_list(root_dir, bin_dir, channel_type):
    """
    チャンネル一覧を取得

    Args:
        root_dir:
        bin_dir:
        channel_type:

    Returns:

    """
    channel_list = []

    # 検索用ファイル
    search_filename = os.path.join(root_dir, const.CONF_DIR, 'search', f'search_{channel_type}_channel_list.xlsx')
    if os.path.isfile(search_filename):
        df = pd.read_excel(search_filename, sheet_name=const.CHANNEL_SHEET_NAME).query('display_flg == True')
        for _, row in df.iterrows():
            channel_list.append({
                'channel_name': row['channel_name'],
                'checked': 'checked' if row['default_check_flg'] == True else '',
            })
    else:
        # 検索用ファイルがない場合はマスタから取得する
        search_filename = os.path.join(bin_dir, const.DATA_DIR, f'{channel_type}_channel_list.xlsx')
        if not os.path.isfile(search_filename):
            # マスタにも存在しない場合は空のリストを返却
            return []
        df = pd.read_excel(search_filename, sheet_name=const.CHANNEL_SHEET_NAME)
        for _, row in df.iterrows():
            channel_list.append({
                'channel_name': row['channel_name'],
                'checked': '',
            })

    # 行の高さを算出
    q, r = divmod(len(channel_list), CHANNEL_COLS)
    channel_rows = q if r == 0 else q + 1

    result_list = []
    channel_index = 0
    for i in range(1, channel_rows + 2):
        records = []
        for j in range(0, CHANNEL_COLS):
            if channel_index < len(channel_list):
                records.append(channel_list[channel_index])
                channel_index += 1

        result_list.append(records)

    return result_list


def search(root_dir, **kwargs):
    """
    検索

    Args:
        root_dir:
        **kwargs:

    Returns:

    """

    # 検索条件
    search_val = kwargs['search_val']
    search_type = kwargs['search_type']
    poster_list_joined = kwargs['poster_list']
    public_channel_list_joined = kwargs['public_channel_list']
    private_channel_list_joined = kwargs['private_channel_list']
    im_channel_list_joined = kwargs['im_channel_list']

    # 検索条件のリスト項目をリストに戻す
    poster_list = poster_list_joined.split(',')
    public_channel_list = public_channel_list_joined.split(',')
    private_channel_list = private_channel_list_joined.split(',')
    im_channel_list = im_channel_list_joined.split(',')

    # 検索文字列を分割
    search_val_list = re.split(r'[ 　]+', search_val)

    result_list = []
    # public
    for channel_name in public_channel_list:
        result = _search_from_channel(root_dir, const.PUBLIC_DIR, channel_name, search_val_list, search_type, poster_list)
        if result is None:
            continue
        result_list.append(result)

    # private
    for channel_name in private_channel_list:
        result = _search_from_channel(root_dir, const.PRIVATE_DIR, channel_name, search_val_list, search_type, poster_list)
        if result is None:
            continue
        result_list.append(result)

    # im
    for channel_name in im_channel_list:
        result = _search_from_channel(root_dir, const.IM_DIR, channel_name, search_val_list, search_type, poster_list)
        if result is None:
            continue
        result_list.append(result)

    return _convert_to_json_for_search(result_list, search_val_list)


def _search_from_channel(root_dir, channel_type, channel_name, search_val_list, search_type, poster_list):
    """
    チャンネルから対象を検索

    Args:
        root_dir:
        channel_type:
        channel_name:
        search_val_list:
        search_type:
        poster_list:

    Returns:

    """

    filename = os.path.join(root_dir, const.EXPORT_DIR, channel_type, f'{channel_name}.xlsx')
    if not os.path.isfile(filename):
        return None

    # 全件を取得
    df_all = pd.read_excel(filename, index_col=[0], names=('no', 'post_icon', 'post_name', 'post_date', 'post_message', 'reply_icon', 'reply_name', 'reply_date', 'reply_message', 'group_flg'), dtype=str).fillna('')
    df_all['channel_name'] = channel_name
    df_all['channel_type'] = channel_type

    # 投稿者/返信者で絞り込み
    filtered_poster = df_all
    if poster_list:
        filtered_poster = df_all[df_all['post_name'].isin(poster_list) | df_all['reply_name'].isin(poster_list)]

    if not search_val_list:
        # 検索文字列が未入力の場合、この時点で返却
        return filtered_poster

    df_work_list = []
    for target in search_val_list:
        # 投稿
        df_work1 = filtered_poster.query('group_flg == "0"')
        df_work1 = df_work1[df_work1['post_message'].str.contains(target, case=False)]
        # 返信
        df_work2 = filtered_poster
        df_work2 = df_work2[df_work2['reply_message'].str.contains(target, case=False)]

        # マージ
        df_work = pd.concat([df_work1, df_work2])
        df_work_list.append(df_work.groupby(df_work.index).first())

    df_base = df_work_list[0]
    for i in range(1, len(df_work_list)):
        if search_type == '01':
            # AND検索の場合
            df_base = pd.merge(df_base, df_work_list[i], how='inner')
        else:
            # OR検索の場合
            df_base = pd.concat([df_base, df_work_list[i]])
            df_base = df_base.groupby(df_base.index).first()

    return df_base


def _convert_to_json_for_search(record_list, search_val_list):
    """
    検索結果画面に返却する用にJSONへコンバート
    Args:
        record_list:

    Returns:

    """
    if not record_list:
        return []

    result_list = []
    before_key = ''
    for record in record_list:
        for _, row in record.iterrows():
            if before_key == row['post_date']:
                continue

            result_list.append({
                'channel_name': row['channel_name'],
                'post_name': row['post_name'],
                'post_date': row['post_date'],
                'post_message': _add_highlights(row['post_message'], search_val_list),
                'channel_type': row['channel_type'],
            })

            before_key = row['post_date']

    return result_list


def get_detail(root_dir, channel_type, channel_name, post_date, search_val):
    """
    詳細を取得

    Args:
        root_dir:
        channel_type:
        channel_name:
        post_date:
        search_val:

    Returns:

    """
    df = pd.read_excel(os.path.join(root_dir, const.EXPORT_DIR, channel_type, f'{channel_name}.xlsx'), dtype=str).fillna('').query('post_date == @post_date')

    # ハイライト用に検索文字列を分割
    search_val_list = re.split(r'[ 　]+', search_val)

    result_list = []
    post_name = ''
    post_message = ''
    for _, row in df.iterrows():
        if not post_name:
            post_name = row['post_name']
            post_message = _add_highlights(row['post_message'], search_val_list)
        result_list.append({
            'reply_name': row['reply_name'],
            'reply_date': row['reply_date'],
            'reply_message': _add_highlights(row['reply_message'], search_val_list),
        })

    return post_date, post_name, post_message, result_list


def _add_highlights(val, target_vals):
    """
    ハイライト表示

    Args:
        val:
        target_vals:

    Returns:

    """
    result = val
    for target_val in target_vals:
        pattern = re.compile(re.escape(target_val), re.IGNORECASE)
        result = pattern.sub(lambda match: f"<mark>{match.group()}</mark>", result)

    return result
