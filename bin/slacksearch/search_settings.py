"""
Slack検索の設定

create 2025/05/13 hamada
"""
import os
import re

import pandas as pd
import bleach

from common import const
from app_common import app_shared_service
from slacksearch.models import SlackSearchModel, SlackDetailModel, SlackResultModel


def get_poster_list(root_dir, bin_dir):
    """
    投稿者/返信者一覧を取得

    Args:
        root_dir:
        bin_dir:

    Returns:

    """
    poster_list = []

    # マスタ情報
    df = pd.read_excel(os.path.join(bin_dir, const.DATA_DIR, const.USER_FILENAME), sheet_name=const.USER_SHEET_NAME)

    # 検索用ファイル
    search_filename = os.path.join(root_dir, const.CONF_DIR, 'search', 'search_user_list.xlsx')
    if os.path.isfile(search_filename):
        df = pd.read_excel(search_filename, sheet_name=const.USER_SHEET_NAME).query('display_flg == True')
        for _, row in df.iterrows():
            poster_list.append({
                'user_id': row['user_display_name'],
                'user_name': row['user_name'],
                'display_name': f"{row['user_display_name']}：{row['user_name']}",
                'checked': True if row['default_check_flg'] == True else False,
            })
    else:
        # 検索用ファイルがない場合はマスタから取得する
        df = pd.read_excel(os.path.join(bin_dir, const.DATA_DIR, const.USER_FILENAME), sheet_name=const.USER_SHEET_NAME)
        for _, row in df.iterrows():
            poster_list.append({
                'user_id': row['user_display_name'],
                'user_name': row['user_name'],
                'display_name': f"{row['user_display_name']}：{row['user_name']}",
                'checked': False,
            })

    return poster_list


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
                'checked': True if row['default_check_flg'] == True else False,
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

    return channel_list


def search(root_dir, model: SlackSearchModel):
    """
    検索

    Args:
        root_dir:
        model:

    Returns:

    """

    result_list = []
    # public
    for channel_name in model.public_channel_list:
        result = _search_from_channel(root_dir, const.PUBLIC_DIR, channel_name, model)
        if result is None:
            continue
        result_list.append(result)

    # private
    for channel_name in model.private_channel_list:
        result = _search_from_channel(root_dir, const.PRIVATE_DIR, channel_name, model)
        if result is None:
            continue
        result_list.append(result)

    # im
    for channel_name in model.im_channel_list:
        result = _search_from_channel(root_dir, const.IM_DIR, channel_name, model)
        if result is None:
            continue
        result_list.append(result)

    return _convert_to_json_for_search(result_list, model.search_val_list)


def _search_from_channel(root_dir, channel_type, channel_name, model: SlackSearchModel):
    """
    チャンネルから対象を検索

    Args:
        root_dir:
        channel_type:
        channel_name:
        model:

    Returns:

    """

    filename = os.path.join(root_dir, const.EXPORT_DIR, channel_type, f'{channel_name}.xlsx')
    if not os.path.isfile(filename):
        return None

    # 全件を取得
    df_all = pd.read_excel(filename, index_col=[0], names=('no', 'post_icon', 'post_name', 'post_date', 'post_message', 'reply_icon', 'reply_name', 'reply_date', 'reply_message', 'group_flg'), dtype=str).fillna('')
    df_all['channel_name'] = channel_name
    df_all['channel_type'] = channel_type

    # 投稿内容で検索
    filtered_by_post = _search_post_replies(df_all, model, True)

    if not model.is_contains_reply:
        # 返信を含めない場合はここで返却
        return filtered_by_post

    # 返信内容で検索
    filtered_by_reply = _search_post_replies(df_all, model, False)

    # マージ
    merged_data = pd.concat([filtered_by_post, filtered_by_reply])
    if merged_data.empty:
        return pd.DataFrame()

    # 重複を除去してソート
    return merged_data.drop_duplicates(subset='post_date', keep='first').sort_values(by='post_date')


def _search_post_replies(df_all, model:SlackSearchModel, is_post):
    """
    投稿内容/返信内容から検索

    Args:
        df_all:
        model:
        is_post:

    Returns:

    """
    prefix = 'post' if is_post else 'reply'

    # 投稿者/返信者で絞り込み
    filtered_data = df_all
    if is_post:
        # 投稿者が対象の場合、group_flgが「0」のデータで絞り込む
        filtered_data = filtered_data.query('group_flg == "0"')

    if model.poster_list:
        filtered_data = df_all[df_all[f'{prefix}_name'].isin(model.poster_list)]

    # 期間(From)で絞り込み
    if model.search_from_date:
        from_date = app_shared_service.convert_from_date(model.search_from_date)
        filtered_data = filtered_data[filtered_data[f'{prefix}_date'] >= from_date]

    # 期間(To)で絞り込み
    if model.search_to_date:
        to_date = app_shared_service.convert_to_date(model.search_to_date)
        filtered_data = filtered_data[filtered_data[f'{prefix}_date'] <= to_date]

    # 検索文字列で絞り込み
    if model.search_val_list:
        if model.search_type == '01':
            # AND検索
            filtered_data = filtered_data[
                filtered_data[f'{prefix}_message'].apply(lambda x: all(kw.lower() in x.lower() for kw in model.search_val_list))
            ]
        else:
            # OR検索
            filtered_data = filtered_data[
                filtered_data[f'{prefix}_message'].apply(lambda x: any(kw.lower() in x.lower() for kw in model.search_val_list))
            ]

    return filtered_data


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


def get_detail(root_dir, model: SlackDetailModel) -> SlackResultModel:
    """
    詳細を取得

    Args:
        root_dir:
        model:

    Returns:

    """
    result = SlackResultModel()
    result.post_date = model.post_date
    df = pd.read_excel(os.path.join(root_dir, const.EXPORT_DIR, model.channel_type, f'{model.channel_name}.xlsx'), dtype=str).fillna('').query('post_date == "' + result.post_date + '"')

    result_list = []
    for _, row in df.iterrows():
        if not result.post_name:
            result.post_name = row['post_name']
            result.post_message = _add_highlights(row['post_message'], model.search_val_list)
        result_list.append({
            'reply_name': row['reply_name'],
            'reply_date': row['reply_date'],
            'reply_message': _add_highlights(row['reply_message'], model.search_val_list),
        })

    result.result_list = result_list
    return result


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

    # サニタイズして返却
    allowed_tags = ['mark']
    return bleach.clean(result, tags=set(allowed_tags))
